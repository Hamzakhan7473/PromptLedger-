"""Map harness model configs to Deep Agents model strings."""

from __future__ import annotations

from legaleval.models.runner import ModelConfig

_PROVIDER_PREFIX = {
    "openai": "openai",
    "google": "google_genai",
    "bedrock": "bedrock",
}

AGENT_SUPPORTED_PROVIDERS = frozenset(_PROVIDER_PREFIX)


def supports_agent_mode(config: ModelConfig) -> bool:
    return config.provider in AGENT_SUPPORTED_PROVIDERS


def to_deepagents_model(config: ModelConfig) -> str:
    prefix = _PROVIDER_PREFIX.get(config.provider)
    if not prefix:
        raise ValueError(
            f"Agent mode does not support provider {config.provider!r} "
            f"for model {config.name!r}.",
        )
    return f"{prefix}:{config.model_id}"
