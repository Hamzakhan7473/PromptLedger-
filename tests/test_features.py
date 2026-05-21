from __future__ import annotations

import json
import os
from pathlib import Path


os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_validate_manifest_passes() -> None:
    from prompt_ledger.manifest import validate_manifest

    issues = [i for i in validate_manifest() if i.severity == "error"]
    assert issues == []


def test_promote_dry_run() -> None:
    from prompt_ledger.promote import promote_environment

    after, diff = promote_environment(
        target="production",
        sync_from="staging",
        dry_run=True,
    )
    assert "environments" in after
    assert diff is not None


def test_approval_workflow() -> None:
    from prompt_ledger.approval import (
        approve,
        load_approval,
        request_approval,
    )
    from prompt_ledger.paths import repo_root

    path = repo_root() / ".promptledger" / "approval.yaml"
    if path.exists():
        path.unlink()

    request_approval(
        target_environment="production",
        sync_from="staging",
        requested_by="test",
    )
    rec = approve(approved_by="reviewer")
    assert rec.status == "approved"
    assert load_approval() is not None

    path.unlink(missing_ok=True)


def test_evidence_export(tmp_path: Path) -> None:
    from prompt_ledger.evidence import export_evidence

    out = tmp_path / "evidence.json"
    export_evidence(out, promoter="ci")
    data = json.loads(out.read_text())
    assert "audit" in data
    assert "scenarios" in data


def test_empty_context_scenario() -> None:
    from prompt_ledger.paths import repo_root
    from prompt_ledger.scenarios import run_scenario_file

    path = repo_root() / "tests" / "scenarios" / "legal_empty_context.yaml"
    res = run_scenario_file(path)
    assert res.ok, res.errors


def test_pack_verify() -> None:
    from prompt_ledger.packs import verify_pack
    from prompt_ledger.paths import repo_root

    issues = verify_pack(repo_root() / "packs" / "finance-assistant")
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], issues
