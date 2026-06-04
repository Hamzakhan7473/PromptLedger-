from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompt_ledger.platform.config import load_platform_yaml
from prompt_ledger.platform.environments import RLEnvironment


@dataclass(frozen=True)
class ModelRoute:
    model_key: str
    provider: str
    model_id: str
    max_tokens: int


def load_models() -> dict[str, dict[str, Any]]:
    raw = load_platform_yaml("models.yaml")
    return dict(raw.get("models") or {})


def select_model(
    env: RLEnvironment,
    *,
    cost_sensitive: bool = False,
) -> ModelRoute:
    raw = load_platform_yaml("models.yaml")
    models = load_models()
    chosen = raw.get("router", {}).get("default", "claude-sonnet")

    for rule in raw.get("router", {}).get("routing") or []:
        match = rule.get("match") or {}
        if match.get("environment") == env.key:
            chosen = rule.get("model", chosen)
            break
        if match.get("cost_sensitive") and cost_sensitive:
            chosen = rule.get("model", chosen)
            break

    cfg = models.get(chosen) or models.get("gpt-4o") or {}
    return ModelRoute(
        model_key=chosen,
        provider=str(cfg.get("provider", "stub")),
        model_id=str(cfg.get("model_id", chosen)),
        max_tokens=int(cfg.get("max_tokens", 4096)),
    )


def list_models() -> list[dict[str, Any]]:
    return [{"id": k, **v} for k, v in load_models().items()]
