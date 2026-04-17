from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_audit_passes() -> None:
    from prompt_ledger.audit import run_audit

    findings = run_audit()
    assert findings == []


def test_scenarios_pass() -> None:
    from prompt_ledger.paths import repo_root
    from prompt_ledger.scenarios import run_all_scenarios

    root = repo_root()
    results = run_all_scenarios(root / "tests" / "scenarios")
    assert all(r.ok for r in results), [r.errors for r in results if not r.ok]
