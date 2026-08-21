# Open-model factorial Werewolf experiments

## Condition names

The first sign is the good-agent full-disclosure instruction. The second sign
is the Werewolf truth-restriction instruction. `+` means that instruction is
present and `-` means it is absent.

| Display ID | Safe slug | Historical ID | Good-agent policy | Werewolf policy | Evidence |
|---|---|---|---|---|---|
| `++` | `pp` | C3 | Full disclosure | Truth restricted | Full complementary |
| `+-` | `pm` | C1 | Full disclosure | Strategic | Full complementary |
| `-+` | `mp` | C4 | Baseline | Truth restricted | Full complementary |
| `--` | `mm` | C0 | Baseline | Strategic | None |

The signs encode the two prompt-policy interventions, not evidence presence.
This preserves the four strategies in the existing study exactly. It is not a
perfectly orthogonal 2 x 2 evidence design because `-+` has complementary
evidence while `--` does not. Every manifest therefore saves both intervention
flags and `evidence_available`. Analyses label the affected contrasts as
evidence-confounded rather than presenting them as clean causal main effects.

## Matched seeds

The preregistered pilot grid is `1, 101, 1001, 10001`. Every model receives the
same role assignment and initial Python random state for the same seed in all
four conditions. Local generation calls receive a deterministic request seed
derived from the episode seed, model alias, and rendered prompt.

## Pinned model families

The registry is [configs/open_source_models.json](configs/open_source_models.json).
It pins both the source checkpoint and the optional Apple-Silicon MLX build.
The lab-server experiment uses the exact source checkpoints in bfloat16:

- `NousResearch/Meta-Llama-3.1-8B-Instruct` at revision `d10aef7999a2b5ba950ab3974312feeedbfe0b77`. This is a public mirror of `meta-llama/Llama-3.1-8B-Instruct` revision `0e9e39f249a16976918f6564b8830bc894c89659`. All four safetensor byte sizes and SHA-256 hashes were checked against the upstream repository and match exactly.
- `Qwen/Qwen3-30B-A3B-Instruct-2507`
- `mistralai/Mistral-Nemo-Instruct-2407`
- `microsoft/Phi-3-medium-128k-instruct`

The source revision, server revision, dtype, context limit, token limit,
provider, model family, and experiment Git commit are saved in every manifest.
Qwen uses tensor parallelism over two GPUs; the other three models use one GPU.
All four models use vLLM's JSON-schema-constrained decoding for the action
schemas and a uniform 512-token output cap. This prevents markdown preambles
and truncation from being mistaken for gameplay failures while keeping the
generation policy identical across model families.

## Three verification gates

Run:

```bash
PYTHON_BIN=.venv-open-models/bin/python \
  bash scripts/verify_three_passes.sh
```

The gates are:

1. all unit and definition-level invariant tests, including condition aliases,
   protected-player consistency, prompt policy, evidence asymmetry, and the
   debate-turn budget;
2. a complete deterministic fake-model matrix over four conditions and four
   logarithmically spaced seeds, with saved artifacts re-read and asserted;
3. a real loopback HTTP test of the OpenAI-compatible request and response
   contract, including deterministic request seeds and provider metadata.

No GPU experiment should begin unless all three gates pass on the execution
server.

## Lab-server launch

From the repository root on `chili01`:

```bash
python3 -m pip install --user uv==0.12.3
"$HOME/.local/bin/uv" python install 3.12
"$HOME/.local/bin/uv" venv --python 3.12 .venv-open-models
"$HOME/.local/bin/uv" pip install \
  --python .venv-open-models/bin/python \
  -r requirements-open-models.txt

PYTHON_BIN=.venv-open-models/bin/python \
  bash scripts/verify_three_passes.sh

RUN_ROOT="$HOME/outcome_aligned_mas_runs/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN_ROOT"
nohup env \
  PYTHON_BIN="$PWD/.venv-open-models/bin/python" \
  RUN_ROOT="$RUN_ROOT" \
  SINGLE_GPU=5 \
  QWEN_GPUS=5,6 \
  bash scripts/run_server_experiment_matrix.sh \
  >"$RUN_ROOT/orchestrator.log" 2>&1 &
echo $! >"$RUN_ROOT/orchestrator.pid"
```

Python 3.12 is intentional. The pinned FlashInfer build uses a runtime generic
annotation supported by Python 3.12 but not by the system Python 3.10 on
`chili01`; the launcher refuses the incompatible interpreter before allocating
GPU memory.

The matrix runner is resumable. An episode is skipped only when its manifest,
metrics, event stream, and complete game state all exist and the metrics mark
it completed. Failed and partial episodes remain visible and are retried.

Analyze currently complete episodes with:

```bash
.venv-open-models/bin/python analyze_open_model_results.py \
  --runs "$RUN_ROOT"
```
