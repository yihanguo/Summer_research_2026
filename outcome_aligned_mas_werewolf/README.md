# Outcome-Aligned Werewolf MAS: code and validated artifacts

This directory is a self-contained publication snapshot of the Outcome-Aligned
Werewolf multi-agent experiment, its information-theoretic coordination
analysis, and the August 21, 2026 debugging validation.

## Provenance

- Source repository: `yihanguo/Outcome-Aligned-MAS-Analysis-Exploration`
- Source branch: `codex/open-model-factorial-experiments`
- Base source commit: `df818b6886e9e4147dce2805c5408a4d166e730b`
- Validation server: Rice `chili01`, eight NVIDIA RTX A6000 GPUs
- Live validation model: `mistralai/Mistral-Nemo-Instruct-2407`
- Live condition and seed: `++`, seed `10001`

Model weights, API keys, virtual environments, caches, and server process logs
are intentionally excluded. The saved episode records contain model messages,
structured beliefs, game states, metrics, and analysis outputs.

The live manifest records the base commit above with `git_dirty: true` because
the routing patch was deliberately validated before publication. The exact
validated patched files are the copies under `code/` in this directory.

## Debugged failures

Two independent failures were identified.

1. Earlier temporal code aborted when structured belief retries were exhausted.
   The current code retains the last invalid structured response and applies a
   deterministic, auditable repair. Repaired states are marked explicitly, and
   the primary temporal estimator excludes transitions involving repaired
   belief states.
2. A stale `LOCAL_LLM_MODEL_ID` survived a server change from Mistral to Phi.
   The client then requested Mistral from the Phi server and received repeated
   HTTP 404 responses. `run_open_model_matrix.py` now rebinds the endpoint model
   for every model family and verifies the exact ID returned by `/v1/models`
   before launching an episode. The server-matrix script also resets and binds
   the environment variable on every iteration.

## Validation results

Three independent validation layers passed.

### 1. Unit, invariant, and syntax tests

- 48 of 48 tests passed.
- Shell syntax validation passed for the server matrix launcher.
- Tests cover structured-belief repair, complete panel coverage, exact public
  vector matching, temporal PID and macro definitions, stale model rebinding,
  and cross-family routing rejection.

The complete log is in
`results/debug_20260821/full_test_suite.log`.

### 2. Deterministic factorial matrix

- 16 of 16 episodes completed.
- Conditions: `++`, `+-`, `-+`, and `--`.
- Seeds: `1`, `101`, `1001`, and `10001`.
- Eight condition-by-coalition analysis cells were produced.
- Every cell had at least 12 valid temporal transitions and both PID and macro
  outputs.

See `results/debug_20260821/fake_matrix/verification_summary.json` and
`results/debug_20260821/fake_matrix/coordination_analysis/`.

### 3. Complete live Mistral episode

- Episode status: completed.
- Winner: Werewolves.
- Four game rounds.
- 160 belief snapshots arranged into 32 complete panels.
- Zero repaired belief snapshots.
- 32 public messages, four with transparent public-declaration repair.
- 28 valid primary temporal transitions.
- No HTTP 404, traceback, or missing structured-belief exception.

The validation-only estimates from this single live episode were:

| Coalition | Median PID synergy | Macro criterion |
|---|---:|---:|
| Good agents | 0.1667 bits | -6.9091 bits |
| All living agents | 0.1159 bits | -11.5316 bits |

These values validate execution and serialization. They are not scientific
effect estimates because they come from one episode.

See `results/debug_20260821/live_mistral/validation_summary.json`, the complete
episode under `live_mistral/mistral_nemo_12b/pp/seed_10001/`, and the temporal
analysis under `live_mistral/analysis/`.

## Directory layout

```text
outcome_aligned_mas_werewolf/
  code/                         Reproducible experiment and analysis source
    configs/                    Model registry and experiment configuration
    experiment/                 Conditions, events, metrics, PID, macro analysis
    scripts/                    Launchers and three-pass verification scripts
    werewolf/                   Game engine, prompts, model and API adapters
  results/debug_20260821/
    full_test_suite.log
    fake_matrix/                All 16 deterministic validation episodes
    live_mistral/               Complete live episode and temporal outputs
```

Each episode directory may contain:

- `manifest.json`: condition, seed, roles, model revision, and generation setup;
- `events.jsonl`: public messages, belief snapshots, and round extraction events;
- `game_complete.json`: complete terminal game state;
- `game_logs.json`: raw action-level model interaction logs;
- `evidence.json`: condition-specific evidence assignments;
- `metrics.json`: episode outcome and communication metrics.

## Reproduction

From `outcome_aligned_mas_werewolf/code` with the dependencies installed:

```bash
python -m unittest discover -s experiment/tests -v
python scripts/verify_factorial_matrix.py \
  --output-dir runs_validation/fake_matrix
```

For a locally served model, start the pinned vLLM server and run a matrix:

```bash
scripts/serve_vllm_model.sh mistral_nemo_12b 18080

python run_open_model_matrix.py \
  --model mistral_nemo_12b \
  --conditions pp \
  --seeds 10001 \
  --output-dir runs_validation/live_mistral \
  --base-url http://127.0.0.1:18080/v1 \
  --threads 1 \
  --attempts 1

python analyze_temporal_coordination.py \
  --runs runs_validation/live_mistral \
  --output-dir runs_validation/live_mistral/analysis \
  --lag 1 \
  --permutations 100
```

The model registry pins the model revisions and records the effective served
model in every manifest.

## Parallel 64-cell production launcher

`code/scripts/run_parallel_64.sh` runs the complete four-model, four-condition,
four-seed design on an eight-GPU server. It assigns Llama, Mistral, and Phi to
one GPU each and Qwen to two GPUs, starts one endpoint per family, and launches
all 16 independent cells per endpoint. vLLM can therefore batch concurrent
requests while every episode retains its own condition/seed directory, log,
PID, and control metadata.

Before launching any episode, the script requires the exact model ID from each
`/v1/models` endpoint and a successful real chat completion from all four
models. `run_open_model_matrix.py --control-dir` keeps the 64 shard status files
separate while sharing one episode root. At completion, the supervisor checks
all 64 artifact contracts and runs the outcome and temporal-coordination
analyses.

The August 21 production run was launched on `chili01` under:

```text
/home/yg108/outcome_aligned_mas_runs/parallel64_20260821T192500Z
```

It passed 49 unit/invariant tests, a 16-cell deterministic matrix, the loopback
HTTP contract, four live model smokes, and three delayed launch audits. The
production result directory is intentionally not included in this snapshot
while the episodes are still running.
