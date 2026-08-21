#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VERIFY_ROOT="${VERIFY_ROOT:-/tmp/outcome_aligned_mas_verification}"

cd "$PROJECT_DIR"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PROJECT_DIR"

echo "PASS 1/3: definition and invariant unit tests"
"$PYTHON_BIN" -m unittest discover -s experiment/tests -p 'test_*.py' -v

echo "PASS 2/3: complete fake-model condition x logarithmic-seed matrix"
mkdir -p "$VERIFY_ROOT/factorial"
"$PYTHON_BIN" scripts/verify_factorial_matrix.py \
  --output-dir "$VERIFY_ROOT/factorial"

echo "PASS 3/3: OpenAI-compatible HTTP integration contract"
REQUIRE_LOOPBACK_TEST=1 "$PYTHON_BIN" -m unittest \
  experiment.tests.test_open_model_provider.OpenModelProviderTest -v

echo "ALL THREE VERIFICATION PASSES SUCCEEDED"
