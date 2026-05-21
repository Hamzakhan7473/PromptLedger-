from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml, write_yaml
from prompt_ledger.paths import manifest_path
from prompt_ledger.registry import discover_registry


@dataclass(frozen=True)
class ManifestIssue:
    severity: str
    code: str
    message: str
    prompt_id: str | None = None
    environment: str | None = None


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    return read_yaml(path or manifest_path())


def save_manifest(data: dict[str, Any], path: Path | None = None) -> Path:
    p = path or manifest_path()
    write_yaml(p, data)
    return p


def validate_manifest(
    *,
    manifest: dict[str, Any] | None = None,
    registry_root: Path | None = None,
) -> list[ManifestIssue]:
    root_manifest = manifest or load_manifest()
    from prompt_ledger.paths import repo_root

    root = repo_root()
    reg = discover_registry(registry_root or (root / "prompts" / "registry"))
    envs: dict[str, Any] = root_manifest.get("environments") or {}
    issues: list[ManifestIssue] = []

    if not envs:
        issues.append(
            ManifestIssue("error", "empty_environments", "manifest has no environments block"),
        )
        return issues

    for env_name, pins in envs.items():
        if not isinstance(pins, dict):
            issues.append(
                ManifestIssue(
                    "error",
                    "invalid_env",
                    f"environment {env_name!r} must be a mapping of prompt_id -> version",
                    environment=env_name,
                ),
            )
            continue
        for prompt_id, version in pins.items():
            if prompt_id not in reg:
                issues.append(
                    ManifestIssue(
                        "error",
                        "unknown_prompt",
                        f"unknown prompt_id {prompt_id!r}",
                        prompt_id=prompt_id,
                        environment=env_name,
                    ),
                )
                continue
            ver = str(version)
            if ver not in reg[prompt_id].versions:
                issues.append(
                    ManifestIssue(
                        "error",
                        "unknown_version",
                        f"unknown version {ver!r} for {prompt_id!r}",
                        prompt_id=prompt_id,
                        environment=env_name,
                    ),
                )
    return issues


def get_pin(manifest: dict[str, Any], environment: str, prompt_id: str) -> str | None:
    envs = manifest.get("environments") or {}
    pins = envs.get(environment)
    if not isinstance(pins, dict):
        return None
    v = pins.get(prompt_id)
    return str(v) if v is not None else None


def set_pin(
    manifest: dict[str, Any],
    *,
    environment: str,
    prompt_id: str,
    version: str,
) -> dict[str, Any]:
    envs = manifest.setdefault("environments", {})
    pins = envs.setdefault(environment, {})
    if not isinstance(pins, dict):
        raise ValueError(f"environment {environment!r} is not a pin map")
    pins[prompt_id] = version
    return manifest
