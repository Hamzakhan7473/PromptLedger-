"""Build per-run models.yaml from template + selected models."""

from __future__ import annotations

from pathlib import Path

import yaml

from legal_eval_api.config import MODELS_TEMPLATE


def build_models_config(
    selected_models: list[str],
    dest: Path,
    *,
    bedrock_overrides: dict[str, str] | None = None,
) -> Path:
    if not MODELS_TEMPLATE.exists():
        raise FileNotFoundError(f"Missing template: {MODELS_TEMPLATE}")

    with MODELS_TEMPLATE.open(encoding="utf-8") as handle:
        template = yaml.safe_load(handle)

    all_models = template.get("models") or {}
    filtered = {
        name: all_models[name]
        for name in selected_models
        if name in all_models
    }
    missing = [name for name in selected_models if name not in filtered]
    if missing:
        raise ValueError(f"Model(s) not in template: {', '.join(missing)}")

    payload = {
        "defaults": template.get("defaults") or {},
        "models": filtered,
        "judge": template["judge"],
    }

    overrides = bedrock_overrides or {}
    if overrides:
        for model in payload["models"].values():
            if model.get("provider") == "bedrock":
                if overrides.get("region"):
                    model["region"] = overrides["region"]
                if overrides.get("endpoint_url"):
                    model["endpoint_url"] = overrides["endpoint_url"]
        judge = payload.get("judge") or {}
        if judge.get("provider") == "bedrock":
            if overrides.get("region"):
                judge["region"] = overrides["region"]
            if overrides.get("endpoint_url"):
                judge["endpoint_url"] = overrides["endpoint_url"]
        payload["judge"] = judge

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, default_flow_style=False)
    return dest
