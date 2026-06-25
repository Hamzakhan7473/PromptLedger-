"""Load judge model configuration."""

from __future__ import annotations

from pathlib import Path

import yaml

from legaleval.models.runner import ModelConfig, project_root


def load_judge_config(path: Path | None = None) -> ModelConfig:
    config_path = path or (project_root() / "models.yaml")
    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if "judge" not in raw:
        raise ValueError(f"Missing 'judge' section in {config_path}")

    judge = raw["judge"]
    defaults = raw.get("defaults") or {}
    return ModelConfig(
        name="judge",
        provider=judge["provider"],
        model_id=judge["model_id"],
        env_key=judge.get("env_key", ""),
        base_url=judge.get("base_url"),
        region=judge.get("region"),
        provider_path=judge.get("provider_path"),
        bedrock_text_mode=bool(judge.get("bedrock_text_mode", False)),
        max_tokens=judge.get("max_tokens", defaults.get("max_tokens", 4096)),
        temperature=judge.get("temperature", defaults.get("temperature", 0.0)),
    )
