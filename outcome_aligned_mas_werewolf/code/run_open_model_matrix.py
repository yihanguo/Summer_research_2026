"""Run a resumable, matched condition-by-seed matrix for one served model."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from experiment.conditions import get_condition, primary_conditions
from experiment.model_registry import default_seed_grid, get_model_config, git_state


def configure_vllm_client(model_alias: str, base_url: str) -> dict[str, Any]:
    """Bind one matrix process to the model selected for this server.

    Matrix launchers are long-lived and may inherit ``LOCAL_LLM_MODEL_ID`` from
    an earlier model.  Never allow that stale override to leak across model
    families.  The server launcher exposes each vLLM model under its pinned
    source-model ID, so make that exact ID the client endpoint model too.
    """
    os.environ["LOCAL_LLM_BACKEND"] = "vllm"
    os.environ["LOCAL_LLM_BASE_URL"] = base_url.rstrip("/")
    os.environ.pop("LOCAL_LLM_MODEL_ID", None)
    model = get_model_config(model_alias)
    os.environ["LOCAL_LLM_MODEL_ID"] = str(model["source_model_id"])
    return get_model_config(model_alias)


def require_expected_server_model(
    model: dict[str, Any], base_url: str, timeout: float = 15.0
) -> tuple[str, ...]:
    """Fail before an episode if the endpoint serves a different model ID."""
    endpoint = f"{base_url.rstrip('/')}/models"
    request = Request(endpoint, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Could not validate the local model server at {endpoint}: {exc}"
        ) from exc
    served = tuple(
        str(item.get("id"))
        for item in payload.get("data", [])
        if isinstance(item, dict) and item.get("id")
    )
    expected = str(model["endpoint_model"])
    if expected not in served:
        raise RuntimeError(
            "Local model routing mismatch: "
            f"client expects {expected!r}, but {endpoint} serves {served!r}."
        )
    return served


def episode_dir(root: Path, model_alias: str, condition: str, seed: int) -> Path:
    return root / model_alias / get_condition(condition).condition_slug / f"seed_{seed}"


def completion_state(path: Path) -> tuple[bool, str]:
    required = ("manifest.json", "metrics.json", "game_complete.json", "events.jsonl")
    missing = [name for name in required if not (path / name).exists()]
    if missing:
        return False, f"missing:{','.join(missing)}"
    try:
        metrics = json.loads((path / "metrics.json").read_text(encoding="utf-8"))
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"invalid-json:{exc}"
    if metrics.get("episode_status") != "completed":
        return False, f"status:{metrics.get('episode_status')}"
    if manifest.get("condition_slug") != path.parent.name:
        return False, "manifest-condition-path-mismatch"
    return True, "complete"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=[condition.condition_slug for condition in primary_conditions()],
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=list(default_seed_grid()))
    parser.add_argument("--output-dir", default="runs_open_models")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--retry-delay-seconds", type=float, default=20.0)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    model = configure_vllm_client(args.model, args.base_url)
    conditions = [get_condition(value) for value in args.conditions]
    if len({condition.condition_id for condition in conditions}) != len(conditions):
        parser.error("conditions resolve to duplicate sign labels")
    if len(set(args.seeds)) != len(args.seeds) or any(seed < 0 for seed in args.seeds):
        parser.error("seeds must be unique non-negative integers")

    root = Path(args.output_dir).resolve()
    run_root = root / model["alias"]
    specification = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_alias": model["alias"],
        "model": model,
        "conditions": [
            {
                "condition_id": condition.condition_id,
                "condition_slug": condition.condition_slug,
                "legacy_id": condition.legacy_id,
                "evidence_mode": condition.evidence_mode,
                "good_policy": condition.good_policy,
                "wolf_policy": condition.wolf_policy,
                "good_intervention": condition.good_intervention,
                "wolf_intervention": condition.wolf_intervention,
            }
            for condition in conditions
        ],
        "seeds": args.seeds,
        "jobs": len(conditions) * len(args.seeds),
        "threads": args.threads,
        "base_url": args.base_url,
        "git": git_state(),
    }
    write_json(run_root / "matrix_spec.json", specification)
    if args.preflight_only:
        print(run_root / "matrix_spec.json")
        return 0

    require_expected_server_model(model, args.base_url)

    failures: list[dict[str, Any]] = []
    jobs = [(seed, condition) for seed in args.seeds for condition in conditions]
    for index, (seed, condition) in enumerate(jobs, start=1):
        output = episode_dir(root, model["alias"], condition.condition_slug, seed)
        complete, reason = completion_state(output)
        if complete:
            print(f"SKIP {index}/{len(jobs)} {condition.condition_id} seed={seed}", flush=True)
            continue

        succeeded = False
        for attempt in range(1, args.attempts + 1):
            print(
                f"RUN {index}/{len(jobs)} {condition.condition_id} seed={seed} "
                f"attempt={attempt} prior={reason}",
                flush=True,
            )
            command = [
                sys.executable,
                "run_open_model_experiment.py",
                "--model",
                model["alias"],
                "--condition",
                condition.condition_slug,
                "--seed",
                str(seed),
                "--output-dir",
                str(root),
                "--base-url",
                args.base_url,
                "--threads",
                str(args.threads),
                "--backend",
                "vllm",
            ]
            return_code = subprocess.call(command)
            succeeded, reason = completion_state(output)
            if return_code == 0 and succeeded:
                print(
                    f"DONE {index}/{len(jobs)} {condition.condition_id} seed={seed}",
                    flush=True,
                )
                break
            if attempt < args.attempts:
                time.sleep(args.retry_delay_seconds)
        if not succeeded:
            failures.append(
                {
                    "condition_id": condition.condition_id,
                    "condition_slug": condition.condition_slug,
                    "seed": seed,
                    "reason": reason,
                }
            )
            write_json(run_root / "failures.json", failures)

    write_json(run_root / "failures.json", failures)
    completed = len(jobs) - len(failures)
    write_json(
        run_root / "matrix_status.json",
        {
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "requested": len(jobs),
            "completed": completed,
            "failed": len(failures),
            "failures": failures,
        },
    )
    print(f"Matrix completed={completed} failed={len(failures)}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
