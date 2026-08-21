"""Run one instrumented Werewolf episode through a local open-model server."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from experiment.conditions import get_condition
from experiment.model_registry import get_model_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Registry alias, e.g. llama31_8b")
    parser.add_argument("--condition", required=True, help="Signs, slug, or historical C ID")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output-dir", default="runs_open_models")
    parser.add_argument("--experiment-config", default="configs/open_model_experiment.json")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--backend", choices=("mlx", "vllm", "test"), default="vllm")
    args = parser.parse_args()

    condition = get_condition(args.condition)
    local_name = f"local:{args.model}"
    get_model_config(local_name)

    env = os.environ.copy()
    env["LOCAL_LLM_BACKEND"] = args.backend
    env["EXPERIMENT_SEED"] = str(args.seed)
    if args.base_url:
        env["LOCAL_LLM_BASE_URL"] = args.base_url.rstrip("/")
    env.setdefault("LOCAL_LLM_API_KEY", "local-no-key")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    command = [
        sys.executable,
        "main.py",
        "--run",
        f"--v_models={local_name}",
        f"--w_models={local_name}",
        f"--threads={args.threads}",
        f"--experiment_condition={condition.condition_slug}",
        f"--experiment_seed={args.seed}",
        f"--experiment_config={args.experiment_config}",
        f"--output_dir={args.output_dir}",
        "--disable_synthetic_votes",
    ]
    return subprocess.call(command, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
