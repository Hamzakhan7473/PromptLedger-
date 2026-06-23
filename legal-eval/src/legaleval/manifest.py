"""Reproducibility manifest for eval runs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from legaleval.paths import models_config_path, run_manifest_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_models_yaml(path: Path | None = None) -> dict[str, Any]:
    config_path = path or models_config_path()
    with config_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def extract_model_routing(models_yaml: dict[str, Any]) -> dict[str, Any]:
    """Per-model routing metadata (distinguishes e.g. Claude via Bedrock vs Anthropic)."""
    routing: dict[str, Any] = {}
    for name, entry in sorted((models_yaml.get("models") or {}).items()):
        routing[name] = {
            "provider_path": entry.get("provider_path", entry["provider"]),
            "provider": entry["provider"],
            "model_id": entry["model_id"],
        }
        if entry.get("region"):
            routing[name]["region"] = entry["region"]
    judge = models_yaml.get("judge")
    if judge:
        routing["judge"] = {
            "provider_path": judge.get("provider_path", judge["provider"]),
            "provider": judge["provider"],
            "model_id": judge["model_id"],
        }
        if judge.get("region"):
            routing["judge"]["region"] = judge["region"]
    return routing


def build_manifest(
    *,
    run_id: str,
    run_date_utc: str,
    eval_set_path: Path,
    seeds: dict[str, int],
    steps_completed: list[str],
    models_config: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config_path = models_config or models_config_path()
    pinned = load_models_yaml(config_path)
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "run_date_utc": run_date_utc,
        "seeds": seeds,
        "eval_set": {
            "path": str(eval_set_path),
            "sha256": sha256_file(eval_set_path),
        },
        "models_yaml": {
            "path": str(config_path),
            "sha256": sha256_file(config_path),
            "pinned": pinned,
        },
        "model_routing": extract_model_routing(pinned),
        "steps_completed": steps_completed,
    }
    if extra:
        manifest.update(extra)
    return manifest


def write_manifest(manifest: dict[str, Any], path: Path | None = None) -> Path:
    output = path or run_manifest_path(manifest["run_id"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    return output
