from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_ledger.manifest import load_manifest
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.paths import repo_root


def manifest_env_diff(
    manifest: dict[str, Any],
    env_a: str,
    env_b: str,
) -> dict[str, Any]:
    envs = manifest.get("environments") or {}
    pins_a = envs.get(env_a) or {}
    pins_b = envs.get(env_b) or {}
    if not isinstance(pins_a, dict) or not isinstance(pins_b, dict):
        raise ValueError("invalid environment pins")
    all_ids = sorted(set(pins_a) | set(pins_b))
    rows: list[dict[str, Any]] = []
    for pid in all_ids:
        va, vb = pins_a.get(pid), pins_b.get(pid)
        if va != vb:
            rows.append(
                {
                    "prompt_id": pid,
                    env_a: va,
                    env_b: vb,
                    "changed": va is not None and vb is not None and va != vb,
                    "only_in_a": va is not None and vb is None,
                    "only_in_b": vb is not None and va is None,
                },
            )
    return {"env_a": env_a, "env_b": env_b, "diffs": rows}


def prompt_text_diff(
    prompt_id: str,
    version_a: str,
    version_b: str,
    *,
    registry_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root()
    reg = discover_registry(registry_root or (root / "prompts" / "registry"))
    if prompt_id not in reg:
        raise KeyError(f"unknown prompt_id {prompt_id!r}")
    pack = reg[prompt_id]
    va = get_version(pack, version_a)
    vb = get_version(pack, version_b)
    return {
        "prompt_id": prompt_id,
        "version_a": version_a,
        "version_b": version_b,
        "system_changed": va.system != vb.system,
        "user_changed": va.user != vb.user,
        "system_a": va.system,
        "system_b": vb.system,
        "user_a": va.user,
        "user_b": vb.user,
    }


def staging_production_prompt_diffs(
    manifest: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    m = manifest or load_manifest()
    env_diff = manifest_env_diff(m, "staging", "production")
    out: list[dict[str, Any]] = []
    for row in env_diff["diffs"]:
        pid = row["prompt_id"]
        va, vb = row.get("staging"), row.get("production")
        if va and vb and va != vb:
            out.append(prompt_text_diff(pid, str(va), str(vb)))
    return out
