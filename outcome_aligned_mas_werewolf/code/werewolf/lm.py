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

import dataclasses
from typing import Any, Callable, Dict, List, Optional

import jinja2
from werewolf import utils
from werewolf.utils import Deserializable
from werewolf import apis
from werewolf.config import RETRIES


@dataclasses.dataclass
class LmLog(Deserializable):
    prompt: str
    raw_resp: str
    result: Any
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_json(cls, data: Dict[Any, Any]):
        return cls(**data)


def format_prompt(prompt_template, worldstate) -> str:
    return jinja2.Template(prompt_template).render(worldstate)


def generate(
    prompt_template: str,
    response_schema: Dict[str, Any],
    worldstate: Dict[str, Any],
    model: str,
    temperature: float = 1.0,
    allowed_values: Optional[List[Any]] = None,
    result_key: Optional[str] = None,
    result_validator: Optional[Callable[[Any], Optional[str]]] = None,
) -> tuple[Any, LmLog]:
    """Generates text from the language model and parses the result.

    Args:
        prompt_template: The Jinja template for the prompt.
        response_schema: The schema for the expected response.
        worldstate: The world state to be rendered into the prompt.
        model: The language model to use.
        temperature: The sampling temperature for the language model.
        allowed_values: An optional list of allowed values for the result. If
          provided, the generation will retry until a result within the allowed
          values is obtained.
        result_key: An optional key to extract a specific value from the parsed
          result. If not provided, the entire parsed result is returned.

    Returns:
        A tuple containing the result (or None if unsuccessful) and the LmLog.
    """

    base_prompt = format_prompt(prompt_template, worldstate)
    prompt = base_prompt
    raw_responses = []
    errors = []
    validation_failures = []
    last_invalid_result = None
    last_provider_metadata = {}
    for _ in range(RETRIES):
        raw_resp = None
        try:
            raw_resp = apis.generate(
                model=model,
                prompt=prompt,
                response_schema=response_schema,
                temperature=temperature,
                disable_recitation=True,
                disable_safety_check=True,
            )
            raw_resp_text = str(raw_resp)
            result = utils.parse_json(raw_resp_text)
            usage = getattr(raw_resp, "usage", None)
            metadata = dict(getattr(raw_resp, "provider_metadata", {}) or {})
            last_provider_metadata = metadata
            if usage:
                metadata["usage"] = usage
            log = LmLog(
                prompt=prompt,
                raw_resp=raw_resp_text,
                result=result,
                metadata=metadata,
            )

            validation_error = result_validator(result) if result_validator else None
            if validation_error:
                last_invalid_result = result
                validation_failures.append(validation_error)
                prompt = (
                    f"{base_prompt}\n\nVALIDATION ERROR: {validation_error} "
                    "Reply again with one complete JSON object that follows every "
                    "field and coverage requirement exactly."
                )
                raw_responses.append(raw_resp_text)
                temperature = min(1.0, temperature + 0.2)
                continue

            extracted_result = result.get(result_key) if result and result_key else result

            if allowed_values is None or extracted_result in allowed_values:
                return extracted_result, log

            if allowed_values:
                last_invalid_result = result
                validation_failures.append(
                    f"{result_key or 'result'} must be one of {allowed_values}."
                )
                prompt = (
                    f"{base_prompt}\n\n"
                    "VALIDATION ERROR: your previous answer selected an invalid "
                    "value. Reply with JSON only and choose exactly one value from "
                    f"this legal list: {allowed_values}."
                )

        except Exception as e:
            error_text = str(e).lower()
            if (
                "402" in error_text
                or "payment required" in error_text
                or "insufficient balance" in error_text
            ):
                raise RuntimeError(
                    "Model-provider balance is insufficient; stopping this episode "
                    "without retrying."
                ) from e
            if (
                "401" in error_text
                or "invalid_api_key" in error_text
                or "incorrect api key" in error_text
            ):
                env_name = (
                    "XAI_API_KEY"
                    if model.lower().startswith("grok")
                    or model.lower().startswith("xai/")
                    else "DEEPSEEK_API_KEY"
                    if model.lower().startswith("deepseek")
                    else "OPENAI_API_KEY"
                )
                raise RuntimeError(
                    f"Model-provider authentication failed. Set {env_name} to a current "
                    "valid key and retry; do not store the key in requirements.txt."
                ) from e
            errors.append(f"{type(e).__name__}: {e}")
            print(f"Retrying due to Exception: {e}")
        temperature = min(1.0, temperature + 0.2)
        raw_responses.append(str(raw_resp) if raw_resp else "")

    final_metadata = dict(last_provider_metadata)
    if validation_failures:
        final_metadata["validation_failures"] = validation_failures
    if last_invalid_result is not None:
        final_metadata["last_invalid_result"] = last_invalid_result
    if errors:
        final_metadata["generation_errors"] = errors
    return None, LmLog(
        prompt=prompt,
        raw_resp="-------".join(raw_responses) or "\n".join(errors),
        result=None,
        metadata=final_metadata,
    )
