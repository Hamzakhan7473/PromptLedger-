from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_list_verticals() -> None:
    from prompt_ledger.demo import list_verticals

    ids = {v["id"] for v in list_verticals()}
    assert ids == {"legal", "fintech", "healthcare", "general"}


def test_run_legal_demo() -> None:
    from prompt_ledger.demo import run_vertical_demo

    result = run_vertical_demo("legal")
    assert result["scenarios"]["passed"]
    assert result["audit"]["passed"]
    assert result["preview"]["prompt_id"] == "legal.contract_review"


def test_healthcare_scenarios() -> None:
    from prompt_ledger.paths import repo_root
    from prompt_ledger.scenarios import run_scenario_file

    root = repo_root()
    for name in ("healthcare_clinical.yaml", "healthcare_empty_context.yaml"):
        res = run_scenario_file(root / "tests" / "scenarios" / name)
        assert res.ok, res.errors
