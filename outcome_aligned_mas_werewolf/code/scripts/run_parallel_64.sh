#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/.venv-open-models/bin/python}"
RUN_ROOT="${RUN_ROOT:-$PROJECT_DIR/runs_open_models/parallel_64_$(date -u +%Y%m%dT%H%M%SZ)}"
SERVER_WAIT_ATTEMPTS="${SERVER_WAIT_ATTEMPTS:-540}"
SERVER_WAIT_SECONDS="${SERVER_WAIT_SECONDS:-10}"
CELL_ATTEMPTS="${CELL_ATTEMPTS:-3}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found or not executable: $PYTHON_BIN" >&2
  exit 2
fi

MODELS=(llama31_8b mistral_nemo_12b phi3_medium_14b qwen3_30b_a3b)
CONDITIONS=(pp pm mp mm)
SEEDS=(1 101 1001 10001)

declare -A PORTS=(
  [llama31_8b]=18081
  [mistral_nemo_12b]=18082
  [phi3_medium_14b]=18083
  [qwen3_30b_a3b]=18084
)
declare -A GPUS=(
  [llama31_8b]=0
  [mistral_nemo_12b]=1
  [phi3_medium_14b]=2
  [qwen3_30b_a3b]=3,4
)
declare -A SERVER_PIDS=()
declare -A CELL_PIDS=()

mkdir -p "$RUN_ROOT"/{server_logs,cell_logs,control,pids}
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR"
export PYTHONDONTWRITEBYTECODE=1

cleanup_servers() {
  local model pid
  for model in "${MODELS[@]}"; do
    pid="${SERVER_PIDS[$model]:-}"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
    fi
  done
}

cleanup_cells() {
  local key pid
  for key in "${!CELL_PIDS[@]}"; do
    pid="${CELL_PIDS[$key]:-}"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
    fi
  done
}

handle_signal() {
  cleanup_cells
  cleanup_servers
  exit 130
}
cleanup_all() {
  cleanup_cells
  cleanup_servers
}
trap cleanup_all EXIT
trap handle_signal INT TERM HUP

expected_model() {
  env -u LOCAL_LLM_MODEL_ID LOCAL_LLM_BACKEND=vllm "$PYTHON_BIN" - "$1" <<'PY'
import sys
from experiment.model_registry import get_model_config

print(get_model_config(sys.argv[1])["source_model_id"])
PY
}

endpoint_ready() {
  local model="$1" port="$2" expected payload
  expected="$(expected_model "$model")"
  payload="$(curl -fsS --max-time 5 "http://127.0.0.1:$port/v1/models" 2>/dev/null || true)"
  [[ -n "$payload" ]] || return 1
  MODELS_PAYLOAD="$payload" "$PYTHON_BIN" - "$expected" <<'PY' >/dev/null
import json
import os
import sys

payload = json.loads(os.environ["MODELS_PAYLOAD"])
expected = sys.argv[1]
if not any(item.get("id") == expected for item in payload.get("data", [])):
    raise SystemExit(1)
PY
}

live_smoke() {
  local model="$1" port="$2" expected output
  expected="$(expected_model "$model")"
  output="$RUN_ROOT/server_logs/${model}_smoke.json"
  "$PYTHON_BIN" - "$port" "$expected" "$output" <<'PY'
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

port, model, output = sys.argv[1:]
payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Reply with exactly OK."}],
    "temperature": 0.0,
    "max_tokens": 8,
}
request = Request(
    f"http://127.0.0.1:{port}/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request, timeout=180) as response:
    result = json.loads(response.read().decode("utf-8"))
choices = result.get("choices") or []
if not choices or not isinstance(choices[0].get("message", {}).get("content"), str):
    raise SystemExit(f"invalid live completion for {model}: {result}")
Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
PY
}

write_launch_plan() {
  RUN_ROOT="$RUN_ROOT" "$PYTHON_BIN" - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["RUN_ROOT"])
models = ["llama31_8b", "mistral_nemo_12b", "phi3_medium_14b", "qwen3_30b_a3b"]
conditions = ["pp", "pm", "mp", "mm"]
seeds = [1, 101, 1001, 10001]
payload = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "models": models,
    "conditions": conditions,
    "seeds": seeds,
    "requested": len(models) * len(conditions) * len(seeds),
    "parallel_cell_processes": 64,
    "ports": {"llama31_8b": 18081, "mistral_nemo_12b": 18082,
              "phi3_medium_14b": 18083, "qwen3_30b_a3b": 18084},
    "gpus": {"llama31_8b": "0", "mistral_nemo_12b": "1",
             "phi3_medium_14b": "2", "qwen3_30b_a3b": "3,4"},
}
(root / "launch_plan.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY
}

write_launch_plan
echo "RUN_ROOT=$RUN_ROOT"

for model in "${MODELS[@]}"; do
  port="${PORTS[$model]}"
  gpu_set="${GPUS[$model]}"
  log="$RUN_ROOT/server_logs/$model.log"
  echo "START_SERVER model=$model port=$port gpus=$gpu_set $(date -u +%FT%TZ)" | tee -a "$log"
  CUDA_VISIBLE_DEVICES="$gpu_set" setsid "$PROJECT_DIR/scripts/serve_vllm_model.sh" \
    "$model" "$port" >>"$log" 2>&1 &
  pid=$!
  SERVER_PIDS[$model]="$pid"
  echo "$pid" >"$RUN_ROOT/pids/server_$model.pid"
done

for model in "${MODELS[@]}"; do
  port="${PORTS[$model]}"
  ready=0
  for ((attempt=1; attempt<=SERVER_WAIT_ATTEMPTS; attempt++)); do
    pid="${SERVER_PIDS[$model]}"
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "SERVER_EXITED model=$model" >&2
      tail -n 80 "$RUN_ROOT/server_logs/$model.log" >&2 || true
      exit 20
    fi
    if endpoint_ready "$model" "$port"; then
      ready=1
      break
    fi
    sleep "$SERVER_WAIT_SECONDS"
  done
  if [[ "$ready" != 1 ]]; then
    echo "SERVER_TIMEOUT model=$model" >&2
    exit 21
  fi
  echo "SERVER_READY model=$model port=$port $(date -u +%FT%TZ)" | tee -a "$RUN_ROOT/server_logs/$model.log"
done

for model in "${MODELS[@]}"; do
  live_smoke "$model" "${PORTS[$model]}"
  echo "LIVE_SMOKE_PASSED model=$model $(date -u +%FT%TZ)" | tee -a "$RUN_ROOT/server_logs/$model.log"
done
echo "ALL_LIVE_SMOKES_PASSED count=4 $(date -u +%FT%TZ)"

for model in "${MODELS[@]}"; do
  port="${PORTS[$model]}"
  for condition in "${CONDITIONS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      key="${model}_${condition}_${seed}"
      log="$RUN_ROOT/cell_logs/${key}.log"
      control="$RUN_ROOT/control/$model/$condition/seed_$seed"
      setsid "$PYTHON_BIN" run_open_model_matrix.py \
        --model "$model" \
        --conditions "$condition" \
        --seeds "$seed" \
        --output-dir "$RUN_ROOT" \
        --control-dir "$control" \
        --base-url "http://127.0.0.1:$port/v1" \
        --threads 1 \
        --attempts "$CELL_ATTEMPTS" \
        >"$log" 2>&1 &
      pid=$!
      CELL_PIDS[$key]="$pid"
      echo "$pid" >"$RUN_ROOT/pids/cell_${key}.pid"
    done
  done
done

if ! RUN_ROOT="$RUN_ROOT" "$PYTHON_BIN" - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["RUN_ROOT"])
pids = {}
for path in sorted((root / "pids").glob("cell_*.pid")):
    pids[path.stem.removeprefix("cell_")] = int(path.read_text().strip())
payload = {
    "audited_utc": datetime.now(timezone.utc).isoformat(),
    "planned": 64,
    "launched": len(pids),
    "cell_pids": pids,
}
(root / "launch_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
if len(pids) != 64:
    raise SystemExit(f"expected 64 cell processes, found {len(pids)}")
PY
echo "ALL_CELLS_LAUNCHED count=64 $(date -u +%FT%TZ)"

overall_rc=0
for key in "${!CELL_PIDS[@]}"; do
  if ! wait "${CELL_PIDS[$key]}"; then
    overall_rc=1
  fi
done

RUN_ROOT="$RUN_ROOT" "$PYTHON_BIN" - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from run_open_model_matrix import completion_state

root = Path(os.environ["RUN_ROOT"])
models = ["llama31_8b", "mistral_nemo_12b", "phi3_medium_14b", "qwen3_30b_a3b"]
conditions = ["pp", "pm", "mp", "mm"]
seeds = [1, 101, 1001, 10001]
cells = []
for model in models:
    for condition in conditions:
        for seed in seeds:
            path = root / model / condition / f"seed_{seed}"
            complete, reason = completion_state(path)
            cells.append({"model": model, "condition": condition, "seed": seed,
                          "complete": complete, "reason": reason, "path": str(path)})
completed = sum(cell["complete"] for cell in cells)
payload = {
    "completed_utc": datetime.now(timezone.utc).isoformat(),
    "requested": len(cells),
    "completed": completed,
    "failed": len(cells) - completed,
    "cells": cells,
}
(root / "matrix_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(f"GLOBAL_MATRIX completed={completed} failed={len(cells) - completed}")
if completed != len(cells):
    raise SystemExit(1)
PY
then
  overall_rc=1
fi

"$PYTHON_BIN" analyze_open_model_results.py --runs "$RUN_ROOT" || overall_rc=1
"$PYTHON_BIN" analyze_temporal_coordination.py \
  --runs "$RUN_ROOT" \
  --output-dir "$RUN_ROOT/analysis" \
  --lag 1 \
  --permutations "${COORDINATION_NULL_PERMUTATIONS:-100}" || overall_rc=1

echo "PARALLEL_MATRIX_FINISHED rc=$overall_rc run_root=$RUN_ROOT $(date -u +%FT%TZ)"
exit "$overall_rc"
