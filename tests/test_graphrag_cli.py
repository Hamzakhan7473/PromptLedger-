from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_resolve_graphrag_go_run_when_no_binary() -> None:
    from prompt_ledger.graphrag_cli import resolve_graphrag_invocation

    cmd, cwd = resolve_graphrag_invocation(["validate", "-h"])
    assert cmd[0] == "go"
    assert cwd is not None
    assert cwd.name == "graphrag"


def test_resolve_graphrag_env_binary(monkeypatch, tmp_path: Path) -> None:
    from prompt_ledger import graphrag_cli
    from prompt_ledger.graphrag_cli import resolve_graphrag_invocation

    fake = tmp_path / "graphrag"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("GRAPHRAG_BIN", str(fake))
    cmd, cwd = resolve_graphrag_invocation(["index", "-stub"])
    assert cmd[0] == str(fake)
    assert cwd is None
