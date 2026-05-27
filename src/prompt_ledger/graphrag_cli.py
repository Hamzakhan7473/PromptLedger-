from __future__ import annotations

import os
from pathlib import Path

from prompt_ledger.paths import repo_root


def resolve_graphrag_invocation(args: list[str]) -> tuple[list[str], Path | None]:
    """Return argv and optional working directory for GraphRAG subprocesses."""
    root = repo_root()
    candidates: list[Path] = []
    env_bin = os.environ.get("GRAPHRAG_BIN")
    if env_bin:
        candidates.append(Path(env_bin))
    candidates.extend(
        [
            root / "bin" / "graphrag",
            root / "graphrag" / "graphrag",
        ],
    )
    for candidate in candidates:
        if candidate.is_file():
            return [str(candidate), *args], None

    graphrag_dir = root / "graphrag"
    if (graphrag_dir / "go.mod").is_file():
        return ["go", "run", "./cmd/graphrag", *args], graphrag_dir

    raise FileNotFoundError("graphrag binary or Go module not found")
