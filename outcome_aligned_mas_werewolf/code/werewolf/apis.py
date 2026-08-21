# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from typing import Any

try:
    from openai import OpenAI
except ImportError:  # Local stdlib provider does not require the OpenAI SDK.
    OpenAI = None

from experiment.model_registry import get_model_config


class GeneratedText(str):
    """String response carrying provider usage metadata when available."""

    def __new__(
        cls,
        content: str,
        usage: dict[str, Any] | None = None,
        provider_metadata: dict[str, Any] | None = None,
    ):
        value = str.__new__(cls, content)
        value.usage = usage
        value.provider_metadata = provider_metadata or {}
        return value


def _usage_dict(usage: Any) -> dict[str, Any] | None:
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    for method_name in ("model_dump", "to_dict"):
        method = getattr(usage, method_name, None)
        if callable(method):
            value = method()
            if isinstance(value, dict):
                return value
    fields = {}
    for field in (
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "prompt_tokens_details",
        "completion_tokens_details",
    ):
        value = getattr(usage, field, None)
        if isinstance(value, (str, int, float, bool, dict, list)):
            fields[field] = value
    return fields or None


def generate(model, **kwargs):
    model_name = model.lower()
    if model_name.startswith("local:"):
        return generate_openai_compatible_local(model, **kwargs)
    elif model_name.startswith("deepseek"):
        return generate_deepseek(model, **kwargs)
    elif "gpt" in model_name:
        return generate_openai(model, **kwargs)
    elif model_name.startswith("grok") or model_name.startswith("xai/"):
        return generate_xai(model, **kwargs)
    elif "claude" in model_name:
        return generate_authropic(model, **kwargs)
    else:
        return generate_vertexai(model, **kwargs)


# openai
def generate_openai(model: str, prompt: str, json_mode: bool = True, **kwargs):
    if OpenAI is None:
        raise RuntimeError("The openai package is required for the OpenAI provider.")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response_format = {"type": "text"}
    if json_mode:
        response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
        model=model,
    )

    txt = response.choices[0].message.content or ""
    return GeneratedText(txt, _usage_dict(getattr(response, "usage", None)))


def generate_deepseek(model: str, prompt: str, json_mode: bool = True, **kwargs):
    """Generate through DeepSeek's OpenAI-compatible Chat Completions endpoint."""
    if OpenAI is None:
        raise RuntimeError("The openai package is required for the DeepSeek provider.")
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    response_format = {"type": "text"}
    if json_mode:
        response_format = {"type": "json_object"}

    thinking = os.environ.get("DEEPSEEK_THINKING", "disabled").strip().lower()
    if thinking not in {"enabled", "disabled"}:
        raise ValueError("DEEPSEEK_THINKING must be 'enabled' or 'disabled'.")

    request_kwargs = {
        "messages": [{"role": "user", "content": prompt}],
        "response_format": response_format,
        "model": model,
        "extra_body": {"thinking": {"type": thinking}},
    }
    if thinking == "enabled":
        request_kwargs["reasoning_effort"] = os.environ.get(
            "DEEPSEEK_REASONING_EFFORT", "high"
        )

    response = client.chat.completions.create(**request_kwargs)
    txt = response.choices[0].message.content or ""
    return GeneratedText(txt, _usage_dict(getattr(response, "usage", None)))


def generate_xai(model: str, prompt: str, json_mode: bool = True, **kwargs):
    """Generate through xAI's OpenAI-compatible Chat Completions endpoint."""
    if OpenAI is None:
        raise RuntimeError("The openai package is required for the xAI provider.")
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )

    response_format = {"type": "text"}
    if json_mode:
        response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
        model=model,
    )
    txt = response.choices[0].message.content or ""
    return GeneratedText(txt, _usage_dict(getattr(response, "usage", None)))


def _stable_request_seed(model: str, prompt: str) -> int:
    """Derive a repeatable request seed from the episode seed and prompt."""
    episode_seed = os.environ.get("EXPERIMENT_SEED", "0")
    digest = hashlib.sha256(f"{episode_seed}\0{model}\0{prompt}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def generate_openai_compatible_local(
    model: str,
    prompt: str,
    json_mode: bool = True,
    temperature: float = 0.7,
    **kwargs,
):
    """Call a pinned open model through an OpenAI-compatible local endpoint.

    This implementation intentionally uses the standard library so the local
    MLX or vLLM route does not depend on the OpenAI Python package.
    """
    config = get_model_config(model)
    base_url = str(config["base_url"]).rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    max_tokens = int(
        os.environ.get("LOCAL_LLM_MAX_OUTPUT_TOKENS", config["max_output_tokens"])
    )
    payload: dict[str, Any] = {
        "model": config["endpoint_model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(temperature),
        "max_tokens": max_tokens,
        "stream": False,
    }
    if config["supports_seed"]:
        payload["seed"] = _stable_request_seed(model, prompt)
    if json_mode and config["supports_response_format"]:
        response_schema = kwargs.get("response_schema")
        if response_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "werewolf_action",
                    "schema": response_schema,
                    "strict": True,
                },
            }
        else:
            payload["response_format"] = {"type": "json_object"}

    api_key = os.environ.get("LOCAL_LLM_API_KEY", "local-no-key")
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    timeout = float(os.environ.get("LOCAL_LLM_TIMEOUT_SECONDS", "300"))
    started = time.monotonic()
    try:
        with urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Local LLM HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Local LLM endpoint unavailable at {endpoint}: {exc}") from exc

    try:
        content = response_payload["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Malformed local LLM response from {endpoint}: {response_payload}"
        ) from exc
    metadata = {
        "provider": "openai_compatible_local",
        "endpoint": endpoint,
        "model_alias": config["alias"],
        "served_model": config["endpoint_model"],
        "served_revision": config["endpoint_revision"],
        "quantization": config["endpoint_quantization"],
        "backend": config["backend"],
        "server_version": os.environ.get("LOCAL_LLM_SERVER_VERSION"),
        "temperature": float(temperature),
        "max_tokens": max_tokens,
        "request_seed": payload.get("seed"),
        "latency_seconds": time.monotonic() - started,
        "json_instruction_only": bool(json_mode and not config["supports_response_format"]),
        "structured_output": payload.get("response_format", {}).get("type"),
    }
    return GeneratedText(
        str(content),
        _usage_dict(response_payload.get("usage")),
        provider_metadata=metadata,
    )


# anthropic
def generate_authropic(model: str, prompt: str, **kwargs):
    # For local development, run `gcloud auth application-default login` first to
    # create the application default credentials, which will be picked up
    # automatically here.
    import google.auth
    from anthropic import AnthropicVertex

    _, project_id = google.auth.default()
    client = AnthropicVertex(region="us-east5", project_id=project_id)

    response = client.messages.create(
        model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
    )

    return response.content[0].text


# vertexai
def generate_vertexai(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    json_mode: bool = True,
    json_schema: dict[str, Any] | None = None,
    **kwargs,
) -> str:
    """Generates text content using Vertex AI."""

    # For local development, run `gcloud auth application-default login` first to
    # create the application default credentials, which will be picked up
    # automatically here.
    import google.auth
    import vertexai
    from vertexai.preview import generative_models

    credentials, project_id = google.auth.default()

    vertexai.init(
        project=project_id,
        location="us-central1",
        credentials=credentials,
    )
    model_endpoint = generative_models.GenerativeModel(model)

    # 1.5 flash doesn't support constrained decoding as of 6/5/2024, so we
    # disable json_schema for it. Otherwise, the library will throw an unsupported
    # error.
    if "flash" in model:
        json_schema = None

    response_mimetype = None
    if json_mode or json_schema is not None:
        response_mimetype = "application/json"
    config = generative_models.GenerationConfig(
        temperature=temperature,
        response_mime_type=response_mimetype,
        response_schema=json_schema,
    )

    # Safety config.
    safety_config = [
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
        ),
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
        ),
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
        ),
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]
    response = model_endpoint.generate_content(
        prompt,
        generation_config=config,
        stream=False,
        safety_settings=safety_config,
    )
    assert isinstance(response, generative_models.GenerationResponse)

    return response.text
