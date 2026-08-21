"""Validated registry for locally served open-weight model families."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPOSITORY_ROOT / "configs" / "open_source_models.json"


def registry_path() -> Path:
    override = os.environ.get("LOCAL_LLM_REGISTRY_PATH")
    return Path(override).expanduser().resolve() if override else DEFAULT_REGISTRY_PATH


def load_registry(path: str | Path | None = None) -> Dict[str, Any]:
    source = Path(path) if path else registry_path()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError(f"Unsupported model-registry schema in {source}")
    seeds = payload.get("default_seed_grid")
    if not isinstance(seeds, list) or not seeds or any(not isinstance(seed, int) for seed in seeds):
        raise ValueError("default_seed_grid must be a non-empty integer list")
    models = payload.get("models")
    if not isinstance(models, dict) or not models:
        raise ValueError("model registry must define at least one model")
    for alias, config in models.items():
        _validate_model(alias, config)
    return payload


def _validate_model(alias: str, config: Mapping[str, Any]) -> None:
    required = {
        "family",
        "source_model_id",
        "source_revision",
        "local_model_id",
        "local_revision",
        "quantization",
        "artifact_gib",
        "recommended_min_memory_gib",
        "base_url",
        "context_limit",
        "max_output_tokens",
        "supports_response_format",
        "supports_seed",
        "reasoning_mode",
        "vllm",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Model {alias} is missing registry fields: {missing}")
    for revision_field in ("source_revision", "local_revision"):
        revision = config[revision_field]
        if not isinstance(revision, str) or len(revision) != 40:
            raise ValueError(f"Model {alias} has an unpinned {revision_field}")
    if not str(config["base_url"]).endswith("/v1"):
        raise ValueError(f"Model {alias} base_url must end in /v1")
    vllm = config["vllm"]
    if not isinstance(vllm, dict) or int(vllm.get("tensor_parallel_size", 0)) < 1:
        raise ValueError(f"Model {alias} has invalid vllm settings")


def model_alias(model: str) -> str:
    if not model.startswith("local:"):
        raise ValueError(f"Local model names must use local:<alias>, got {model}")
    return model.split(":", 1)[1]


def get_model_config(model_or_alias: str) -> Dict[str, Any]:
    alias = model_alias(model_or_alias) if model_or_alias.startswith("local:") else model_or_alias
    registry = load_registry()
    try:
        config = dict(registry["models"][alias])
    except KeyError as exc:
        raise KeyError(f"Unknown local model alias: {alias}") from exc
    config["alias"] = alias
    backend = os.environ.get("LOCAL_LLM_BACKEND", "mlx").strip().lower()
    if backend not in {"mlx", "vllm", "test"}:
        raise ValueError(f"Unsupported LOCAL_LLM_BACKEND: {backend}")
    config["backend"] = backend
    config["base_url"] = os.environ.get("LOCAL_LLM_BASE_URL", config["base_url"])
    default_endpoint_model = (
        config["source_model_id"] if backend == "vllm" else config["local_model_id"]
    )
    config["endpoint_model"] = os.environ.get(
        "LOCAL_LLM_MODEL_ID", default_endpoint_model
    )
    config["endpoint_revision"] = (
        config["source_revision"] if backend == "vllm" else config["local_revision"]
    )
    config["endpoint_quantization"] = (
        config["vllm"]["dtype"] if backend == "vllm" else config["quantization"]
    )
    return config


def default_seed_grid() -> tuple[int, ...]:
    return tuple(load_registry()["default_seed_grid"])


def model_metadata(model: str) -> Dict[str, Any]:
    if not model.startswith("local:"):
        return {"provider": "external", "model": model}
    config = get_model_config(model)
    return {
        "provider": "openai_compatible_local",
        "alias": config["alias"],
        "family": config["family"],
        "source_model_id": config["source_model_id"],
        "source_revision": config["source_revision"],
        "served_model_id": config["endpoint_model"],
        "served_model_revision": config["endpoint_revision"],
        "quantization": config["endpoint_quantization"],
        "backend": config["backend"],
        "base_url": config["base_url"],
        "context_limit": config["context_limit"],
        "reasoning_mode": config["reasoning_mode"],
        "server_version": os.environ.get("LOCAL_LLM_SERVER_VERSION"),
    }


def git_state() -> Dict[str, Any]:
    """Return commit and dirty state without failing outside a Git checkout."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPOSITORY_ROOT, text=True
            ).strip()
        )
        return {"commit": commit, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
