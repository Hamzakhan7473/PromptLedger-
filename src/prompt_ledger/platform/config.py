from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml
from prompt_ledger.paths import repo_root


def platform_config_dir() -> Path:
    return repo_root() / "platform" / "config"


def load_platform_yaml(name: str) -> dict[str, Any]:
    return read_yaml(platform_config_dir() / name)
