from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    env = os.environ.get("PROMPT_LEDGER_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "governance" / "governance.yaml").exists():
            return parent
    return Path.cwd()


def governance_path() -> Path:
    return repo_root() / "governance" / "governance.yaml"


def manifest_path() -> Path:
    return repo_root() / "prompts" / "manifest.yaml"


def registry_dir() -> Path:
    return repo_root() / "prompts" / "registry"


def schemas_dir() -> Path:
    return repo_root() / "schemas"
