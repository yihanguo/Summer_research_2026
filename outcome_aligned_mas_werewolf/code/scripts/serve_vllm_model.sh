#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 MODEL_ALIAS [PORT]" >&2
  exit 2
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/.venv-open-models/bin/python}"
MODEL_ALIAS="$1"
PORT="${2:-8080}"
export PATH="$(dirname "$PYTHON_BIN"):$PATH"

"$PYTHON_BIN" - <<'PY'
import sys

if sys.version_info[:2] != (3, 12):
    raise SystemExit(
        "The pinned vLLM/FlashInfer server environment requires Python 3.12; "
        f"received {sys.version.split()[0]}"
    )
PY

readarray -t MODEL_FIELDS < <(
  cd "$PROJECT_DIR"
  LOCAL_LLM_BACKEND=vllm "$PYTHON_BIN" - "$MODEL_ALIAS" <<'PY'
import sys
from experiment.model_registry import get_model_config

config = get_model_config(sys.argv[1])
vllm = config["vllm"]
print(config["source_model_id"])
print(config["source_revision"])
print(vllm["tensor_parallel_size"])
print(vllm["dtype"])
print(vllm["gpu_memory_utilization"])
print(vllm["max_model_len"])
print("1" if vllm["trust_remote_code"] else "0")
PY
)

MODEL_ID="${MODEL_FIELDS[0]}"
REVISION="${MODEL_FIELDS[1]}"
TP_SIZE="${MODEL_FIELDS[2]}"
DTYPE="${MODEL_FIELDS[3]}"
GPU_MEMORY="${MODEL_FIELDS[4]}"
MAX_MODEL_LEN="${MODEL_FIELDS[5]}"
TRUST_REMOTE_CODE="${MODEL_FIELDS[6]}"

COMMAND=(
  "$PYTHON_BIN" -m vllm.entrypoints.openai.api_server
  --host 127.0.0.1
  --port "$PORT"
  --model "$MODEL_ID"
  --revision "$REVISION"
  --tokenizer-revision "$REVISION"
  --served-model-name "$MODEL_ID"
  --tensor-parallel-size "$TP_SIZE"
  --dtype "$DTYPE"
  --gpu-memory-utilization "$GPU_MEMORY"
  --max-model-len "$MAX_MODEL_LEN"
  --max-num-seqs 16
)
if [[ "$TRUST_REMOTE_CODE" == "1" ]]; then
  COMMAND+=(--trust-remote-code)
fi

echo "Serving $MODEL_ALIAS as $MODEL_ID revision=$REVISION tp=$TP_SIZE port=$PORT"
exec "${COMMAND[@]}"
