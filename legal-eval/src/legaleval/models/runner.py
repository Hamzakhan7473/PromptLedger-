"""Provider-agnostic model clients and eval run logging."""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx
import yaml
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from legaleval.data.cuad import EvalExample, read_eval_set_jsonl
from legaleval.models.bedrock import (
    build_tool_config,
    converse_usage_tokens,
    extract_text_content,
    extract_tool_input,
    tool_input_to_text,
)
from legaleval.models.prompt import (
    SYSTEM_PROMPT,
    ModelPrediction,
    build_user_prompt,
    parse_model_response,
)

DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.0
RETRY_ATTEMPTS = 4


class BedrockAccessDeniedError(RuntimeError):
    """Non-retryable Bedrock model access failure."""


class RawResponse(BaseModel):
    text: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class ModelConfig(BaseModel):
    name: str
    provider: str
    model_id: str
    env_key: str = ""
    base_url: str | None = None
    region: str | None = None
    provider_path: str | None = None
    bedrock_text_mode: bool = False
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE

    @property
    def resolved_provider_path(self) -> str:
        return self.provider_path or self.provider


class CallLogRow(BaseModel):
    run_id: str
    example_id: str
    category: str
    contract_title: str
    provider: str
    model: str
    model_id: str
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    raw_text: str | None = None
    parsed: dict[str, Any] | None = None
    parse_error: str | None = None
    error: str | None = None


class ModelClient(ABC):
    """Provider-agnostic completion interface."""

    provider: str

    def __init__(
        self,
        *,
        name: str,
        model_id: str,
        api_key: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        base_url: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.name = name
        self.model_id = model_id
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = base_url
        self._http = http_client or httpx.Client(timeout=120.0)

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True,
    )
    def complete(self, prompt: str, system: str) -> RawResponse:
        return self._complete(prompt, system)

    @abstractmethod
    def _complete(self, prompt: str, system: str) -> RawResponse:
        raise NotImplementedError

    def close(self) -> None:
        self._http.close()


class AnthropicClient(ModelClient):
    provider = "anthropic"

    def _complete(self, prompt: str, system: str) -> RawResponse:
        started = time.perf_counter()
        response = self._http.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model_id,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()
        latency_ms = (time.perf_counter() - started) * 1000
        usage = payload.get("usage") or {}
        text = "".join(
            block.get("text", "")
            for block in payload.get("content", [])
            if block.get("type") == "text"
        )
        return RawResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            total_tokens=_sum_tokens(usage),
        )


class OpenAIClient(ModelClient):
    provider = "openai"

    def _complete(self, prompt: str, system: str) -> RawResponse:
        started = time.perf_counter()
        response = self._http.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json",
            },
            json={
                "model": self.model_id,
                "max_completion_tokens": self.max_tokens,
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()
        latency_ms = (time.perf_counter() - started) * 1000
        usage = payload.get("usage") or {}
        text = payload["choices"][0]["message"]["content"]
        return RawResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
        )


class GoogleClient(ModelClient):
    provider = "google"

    def _complete(self, prompt: str, system: str) -> RawResponse:
        started = time.perf_counter()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_id}:generateContent"
        )
        response = self._http.post(
            url,
            headers={
                "content-type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                    "responseMimeType": "application/json",
                },
            },
        )
        response.raise_for_status()
        payload = response.json()
        latency_ms = (time.perf_counter() - started) * 1000
        usage = payload.get("usageMetadata") or {}
        text = _google_response_text(payload)
        return RawResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=usage.get("promptTokenCount"),
            output_tokens=usage.get("candidatesTokenCount"),
            total_tokens=usage.get("totalTokenCount"),
        )


class OpenAICompatibleClient(ModelClient):
    provider = "openai_compatible"

    def _complete(self, prompt: str, system: str) -> RawResponse:
        if not self.base_url:
            raise ValueError("openai_compatible provider requires base_url")
        started = time.perf_counter()
        base = self.base_url.rstrip("/")
        response = self._http.post(
            f"{base}/v1/chat/completions",
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json",
            },
            json={
                "model": self.model_id,
                "max_completion_tokens": self.max_tokens,
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()
        latency_ms = (time.perf_counter() - started) * 1000
        usage = payload.get("usage") or {}
        text = payload["choices"][0]["message"]["content"]
        return RawResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
        )


class BedrockClient(ModelClient):
    """Amazon Bedrock Runtime Converse client with forced tool-use output."""

    provider = "bedrock"

    def __init__(
        self,
        *,
        name: str,
        model_id: str,
        region: str,
        provider_path: str = "bedrock",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        bedrock_client: Any | None = None,
        text_mode: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            model_id=model_id,
            api_key="",
            max_tokens=max_tokens,
            temperature=temperature,
        )
        self.region = region
        self.resolved_provider_path = provider_path
        self.text_mode = text_mode
        if bedrock_client is not None:
            self._bedrock = bedrock_client
        else:
            import boto3

            self._bedrock = boto3.client("bedrock-runtime", region_name=region)

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_not_exception_type(BedrockAccessDeniedError),
        reraise=True,
    )
    def complete(self, prompt: str, system: str) -> RawResponse:
        return self._complete(prompt, system)

    def _complete(self, prompt: str, system: str) -> RawResponse:
        started = time.perf_counter()
        request: dict[str, Any] = {
            "modelId": self.model_id,
            "system": [{"text": system}],
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }
        if not self.text_mode:
            request["toolConfig"] = build_tool_config(force_tool=True)
        try:
            response = self._converse(request)
        except ClientError as exc:
            raise _bedrock_client_error(exc, model_id=self.model_id, region=self.region) from exc

        latency_ms = (time.perf_counter() - started) * 1000
        if self.text_mode:
            text = extract_text_content(response)
        else:
            tool_input = extract_tool_input(response)
            text = tool_input_to_text(tool_input)
        input_tokens, output_tokens, total_tokens = converse_usage_tokens(response)
        return RawResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )

    def _converse(self, request: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._bedrock.converse(**request)
        except ClientError as exc:
            if self.text_mode or "toolConfig" not in request:
                raise
            if not _tool_choice_rejected(exc):
                raise
            fallback = dict(request)
            fallback["toolConfig"] = build_tool_config(force_tool=False)
            return self._bedrock.converse(**fallback)

    def close(self) -> None:
        self._http.close()


_CLIENT_BY_PROVIDER: dict[str, type[ModelClient]] = {
    "anthropic": AnthropicClient,
    "openai": OpenAIClient,
    "google": GoogleClient,
    "openai_compatible": OpenAICompatibleClient,
    "bedrock": BedrockClient,
}


from legaleval.paths import project_root, run_raw_dir


def load_models_config(path: Path | None = None) -> dict[str, ModelConfig]:
    config_path = path or (project_root() / "models.yaml")
    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    defaults = raw.get("defaults") or {}
    default_max_tokens = defaults.get("max_tokens", DEFAULT_MAX_TOKENS)
    default_temperature = defaults.get("temperature", DEFAULT_TEMPERATURE)

    configs: dict[str, ModelConfig] = {}
    for name, entry in raw["models"].items():
        configs[name] = ModelConfig(
            name=name,
            provider=entry["provider"],
            model_id=entry["model_id"],
            env_key=entry.get("env_key", ""),
            base_url=entry.get("base_url"),
            region=entry.get("region"),
            provider_path=entry.get("provider_path"),
            bedrock_text_mode=bool(entry.get("bedrock_text_mode", False)),
            max_tokens=entry.get("max_tokens", default_max_tokens),
            temperature=entry.get("temperature", default_temperature),
        )
    return configs


def resolve_model_names(models_arg: str, configs: dict[str, ModelConfig]) -> list[str]:
    if models_arg.strip().lower() == "all":
        return sorted(configs)
    selected = [name.strip() for name in models_arg.split(",") if name.strip()]
    unknown = [name for name in selected if name not in configs]
    if unknown:
        raise ValueError(f"Unknown model(s): {', '.join(unknown)}")
    return selected


def create_client(config: ModelConfig) -> ModelClient:
    client_cls = _CLIENT_BY_PROVIDER.get(config.provider)
    if client_cls is None:
        raise ValueError(f"Unsupported provider: {config.provider}")

    if config.provider == "bedrock":
        if not config.region:
            raise ValueError(f"bedrock provider requires region for model {config.name!r}")
        return BedrockClient(
            name=config.name,
            model_id=config.model_id,
            region=config.region,
            provider_path=config.resolved_provider_path,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            text_mode=config.bedrock_text_mode,
        )

    if not config.env_key:
        raise ValueError(f"Missing env_key for model {config.name!r}")
    api_key = os.environ.get(config.env_key, "")
    if not api_key:
        raise ValueError(f"Missing API key environment variable: {config.env_key}")

    return client_cls(
        name=config.name,
        model_id=config.model_id,
        api_key=api_key,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        base_url=config.base_url,
    )


def _base_log_row(
    *,
    run_id: str,
    example: EvalExample,
    client: ModelClient,
) -> CallLogRow:
    return CallLogRow(
        run_id=run_id,
        example_id=example.id,
        category=example.category,
        contract_title=example.contract_title,
        provider=client.provider,
        model=client.name,
        model_id=client.model_id,
    )


def _error_row(
    *,
    run_id: str,
    example: EvalExample,
    config: ModelConfig,
    error: str,
) -> CallLogRow:
    return CallLogRow(
        run_id=run_id,
        example_id=example.id,
        category=example.category,
        contract_title=example.contract_title,
        provider=config.provider,
        model=config.name,
        model_id=config.model_id,
        error=error,
    )


def execute_example(
    client: ModelClient,
    example: EvalExample,
    *,
    run_id: str,
) -> CallLogRow:
    row = _base_log_row(run_id=run_id, example=example, client=client)
    prompt = build_user_prompt(example)
    try:
        response = client.complete(prompt, SYSTEM_PROMPT)
    except Exception as exc:  # noqa: BLE001 - record all failures
        row.error = f"{type(exc).__name__}: {exc}"
        return row

    row.latency_ms = round(response.latency_ms, 2)
    row.input_tokens = response.input_tokens
    row.output_tokens = response.output_tokens
    row.total_tokens = response.total_tokens
    row.raw_text = response.text

    prediction, parse_error = parse_model_response(response.text)
    if prediction is not None:
        row.parsed = prediction.model_dump()
    if parse_error is not None:
        row.parse_error = parse_error
    return row


def append_log_row(handle, row: CallLogRow) -> None:
    handle.write(row.model_dump_json() + "\n")
    handle.flush()


def run_model_on_eval_set(
    config: ModelConfig,
    examples: list[EvalExample],
    *,
    run_id: str,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    client: ModelClient | None = None
    try:
        client = create_client(config)
    except Exception as exc:  # noqa: BLE001
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                append_log_row(
                    handle,
                    _error_row(
                        run_id=run_id,
                        example=example,
                        config=config,
                        error=f"{type(exc).__name__}: {exc}",
                    ),
                )
        return

    try:
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                row = execute_example(client, example, run_id=run_id)
                append_log_row(handle, row)
    finally:
        client.close()


def run_eval(
    *,
    models: str,
    eval_set_path: Path,
    run_id: str,
    models_config_path: Path | None = None,
) -> Path:
    configs = load_models_config(models_config_path)
    selected = resolve_model_names(models, configs)
    examples = read_eval_set_jsonl(eval_set_path)
    output_dir = run_raw_dir(run_id)

    for model_name in selected:
        run_model_on_eval_set(
            configs[model_name],
            examples,
            run_id=run_id,
            output_path=output_dir / f"{model_name}.jsonl",
        )

    return output_dir


def _sum_tokens(usage: dict[str, Any]) -> int | None:
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_tokens is None and output_tokens is None:
        return None
    return int(input_tokens or 0) + int(output_tokens or 0)


def _google_response_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        raise ValueError("Google response missing candidates")
    parts = candidates[0].get("content", {}).get("parts") or []
    return "".join(part.get("text", "") for part in parts)


def _bedrock_client_error(
    exc: ClientError,
    *,
    model_id: str,
    region: str,
) -> Exception:
    code = exc.response.get("Error", {}).get("Code", "")
    if code == "AccessDeniedException":
        return BedrockAccessDeniedError(
            "Bedrock AccessDeniedException: enable model access for "
            f"{model_id!r} in the Amazon Bedrock console (Model access) "
            f"for region {region!r}, then retry."
        )
    return exc


def _tool_choice_rejected(exc: ClientError) -> bool:
    code = exc.response.get("Error", {}).get("Code", "")
    if code != "ValidationException":
        return False
    message = exc.response.get("Error", {}).get("Message", "").lower()
    return "toolchoice" in message or "tool choice" in message
