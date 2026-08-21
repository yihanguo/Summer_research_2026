#!/usr/bin/env bash

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/.venv-open-models/bin/python}"
RUN_ROOT="${RUN_ROOT:-$PROJECT_DIR/runs_open_models/$(date -u +%Y%m%dT%H%M%SZ)}"
PORT="${PORT:-8080}"
SEEDS=(1 101 1001 10001)
CONDITIONS=(pp pm mp mm)
MODELS=(mistral_nemo_12b phi3_medium_14b qwen3_30b_a3b llama31_8b)

mkdir -p "$RUN_ROOT/server_logs"
cd "$PROJECT_DIR" || exit 10
export PYTHONPATH="$PROJECT_DIR"
export PYTHONDONTWRITEBYTECODE=1
export LOCAL_LLM_BACKEND=vllm
export LOCAL_LLM_BASE_URL="http://127.0.0.1:$PORT/v1"
export LOCAL_LLM_SERVER_VERSION="0.27.1"
# A caller may have exported the model ID used by an earlier vLLM server.
# Each loop iteration below binds this value to the newly served model.
unset LOCAL_LLM_MODEL_ID

server_pid=""
server_process_group=""
matrix_pid=""
matrix_process_group=""
cleanup_server() {
  if [[ -n "$server_process_group" ]]; then
    kill -TERM -- "-$server_process_group" 2>/dev/null || true
  elif [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill -TERM "$server_pid" 2>/dev/null || true
  fi
  if [[ -n "$server_pid" ]]; then
    wait "$server_pid" 2>/dev/null || true
  fi
  server_pid=""
  server_process_group=""
}
cleanup_matrix() {
  if [[ -n "$matrix_process_group" ]]; then
    kill -TERM -- "-$matrix_process_group" 2>/dev/null || true
  elif [[ -n "$matrix_pid" ]] && kill -0 "$matrix_pid" 2>/dev/null; then
    kill -TERM "$matrix_pid" 2>/dev/null || true
  fi
  if [[ -n "$matrix_pid" ]]; then
    wait "$matrix_pid" 2>/dev/null || true
  fi
  matrix_pid=""
  matrix_process_group=""
}
cleanup_all() {
  cleanup_matrix
  cleanup_server
}
handle_signal() {
  cleanup_all
  exit 130
}
trap cleanup_all EXIT
trap handle_signal INT TERM HUP

wait_for_server() {
  local expected_model="$1"
  local attempts=0
  while (( attempts < 360 )); do
    if ! kill -0 "$server_pid" 2>/dev/null; then
      return 1
    fi
    models_payload="$(curl -fsS "http://127.0.0.1:$PORT/v1/models" 2>/dev/null || true)"
    if [[ -n "$models_payload" ]] && MODELS_PAYLOAD="$models_payload" \
      "$PYTHON_BIN" - "$expected_model" <<'PY' >/dev/null 2>&1
import json
import os
import sys

payload = json.loads(os.environ["MODELS_PAYLOAD"])
expected = sys.argv[1]
if not any(item.get("id") == expected for item in payload.get("data", [])):
    raise SystemExit(1)
PY
    then
      return 0
    fi
    sleep 10
    ((attempts++))
  done
  return 1
}

overall_rc=0
for model in "${MODELS[@]}"; do
  cleanup_server
  if [[ "$model" == "qwen3_30b_a3b" ]]; then
    export CUDA_VISIBLE_DEVICES="${QWEN_GPUS:-5,6}"
  else
    export CUDA_VISIBLE_DEVICES="${SINGLE_GPU:-5}"
  fi

  server_log="$RUN_ROOT/server_logs/${model}.log"
  echo "START_SERVER model=$model gpus=$CUDA_VISIBLE_DEVICES $(date -u +%FT%TZ)" | tee -a "$server_log"
  if command -v setsid >/dev/null 2>&1; then
    setsid "$PROJECT_DIR/scripts/serve_vllm_model.sh" "$model" "$PORT" >>"$server_log" 2>&1 &
    server_process_group=$!
  else
    "$PROJECT_DIR/scripts/serve_vllm_model.sh" "$model" "$PORT" >>"$server_log" 2>&1 &
  fi
  server_pid=$!
  echo "$server_pid" >"$RUN_ROOT/server_logs/${model}.pid"

  expected_model="$(
    LOCAL_LLM_BACKEND=vllm "$PYTHON_BIN" - "$model" <<'PY'
import sys
from experiment.model_registry import get_model_config

print(get_model_config(sys.argv[1])["source_model_id"])
PY
  )"
  export LOCAL_LLM_MODEL_ID="$expected_model"

  if ! wait_for_server "$expected_model"; then
    echo "SERVER_FAILED model=$model $(date -u +%FT%TZ)" | tee -a "$server_log"
    overall_rc=1
    continue
  fi

  echo "SERVER_READY model=$model $(date -u +%FT%TZ)" | tee -a "$server_log"
  matrix_command=(
    "$PYTHON_BIN" run_open_model_matrix.py
    --model "$model"
    --conditions "${CONDITIONS[@]}"
    --seeds "${SEEDS[@]}"
    --output-dir "$RUN_ROOT"
    --base-url "http://127.0.0.1:$PORT/v1"
    --threads 1
    --attempts 2
  )
  if command -v setsid >/dev/null 2>&1; then
    setsid "${matrix_command[@]}" &
    matrix_process_group=$!
  else
    "${matrix_command[@]}" &
  fi
  matrix_pid=$!
  if ! wait "$matrix_pid"; then
    overall_rc=1
  fi
  matrix_pid=""
  matrix_process_group=""
  echo "MODEL_DONE model=$model $(date -u +%FT%TZ)" | tee -a "$server_log"
done

cleanup_server
"$PYTHON_BIN" analyze_open_model_results.py --runs "$RUN_ROOT" || overall_rc=1
"$PYTHON_BIN" analyze_temporal_coordination.py \
  --runs "$RUN_ROOT" \
  --output-dir "$RUN_ROOT/analysis" \
  --lag 1 \
  --permutations "${COORDINATION_NULL_PERMUTATIONS:-100}" || overall_rc=1
echo "ALL_MODELS_FINISHED rc=$overall_rc run_root=$RUN_ROOT $(date -u +%FT%TZ)"
exit "$overall_rc"
