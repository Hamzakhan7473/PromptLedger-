from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from prompt_ledger.approval import assert_approved_for_promotion
from prompt_ledger.load import read_yaml, write_yaml
from prompt_ledger.manifest import set_pin
from prompt_ledger.paths import manifest_path


def promote_environment(
    *,
    target: str,
    sync_from: str | None = None,
    manifest: Path | None = None,
    dry_run: bool = False,
    require_approval: bool = False,
    set_pins: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Promote prompt pins. Returns (new_manifest, diff) where diff is None if dry_run."""

    if require_approval:
        assert_approved_for_promotion(target, sync_from)

    path = manifest or manifest_path()
    before = read_yaml(path)
    after = deepcopy(before)
    envs: dict[str, Any] = after.setdefault("environments", {})
    if target not in envs:
        raise KeyError(f"Unknown environment {target!r} in manifest")

    if sync_from:
        if sync_from not in envs:
            raise KeyError(f"Unknown sync_from environment {sync_from!r}")
        envs[target] = dict(envs[sync_from])

    if set_pins:
        for prompt_id, version in set_pins.items():
            set_pin(after, environment=target, prompt_id=prompt_id, version=version)

    diff = _manifest_pin_diff(before, after, target)
    if not dry_run:
        write_yaml(path, after)
    return after, diff


def _manifest_pin_diff(before: dict, after: dict, env: str) -> dict[str, Any]:
    b = (before.get("environments") or {}).get(env) or {}
    a = (after.get("environments") or {}).get(env) or {}
    added = {k: a[k] for k in a if k not in b}
    removed = {k: b[k] for k in b if k not in a}
    changed = {k: {"from": b[k], "to": a[k]} for k in a if k in b and a[k] != b[k]}
    return {"environment": env, "added": added, "removed": removed, "changed": changed}
