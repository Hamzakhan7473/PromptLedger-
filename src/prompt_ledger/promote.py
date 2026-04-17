from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml, write_yaml
from prompt_ledger.paths import manifest_path


def promote_environment(
    *,
    target: str,
    sync_from: str | None = None,
    manifest: Path | None = None,
) -> dict[str, Any]:
    """Promote prompt pins (e.g. copy staging pins into production)."""

    path = manifest or manifest_path()
    data = read_yaml(path)
    envs: dict[str, Any] = data.setdefault("environments", {})
    if target not in envs:
        raise KeyError(f"Unknown environment {target!r} in manifest")

    if sync_from:
        if sync_from not in envs:
            raise KeyError(f"Unknown sync_from environment {sync_from!r}")
        envs[target] = dict(envs[sync_from])
    write_yaml(path, data)
    return data
