from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prompt_ledger.audit import run_audit
from prompt_ledger.manifest import load_manifest, validate_manifest
from prompt_ledger.paths import governance_path, repo_root
from prompt_ledger.scenarios import run_all_scenarios


def _git_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_evidence(
    *,
    environment: str = "production",
    scenarios_dir: Path | None = None,
    promoter: str | None = None,
) -> dict[str, Any]:
    root = repo_root()
    gov_path = governance_path()
    manifest = load_manifest()
    audit_findings = run_audit()
    scenario_results = run_all_scenarios(scenarios_dir or (root / "tests" / "scenarios"))
    manifest_issues = validate_manifest(manifest=manifest)

    from prompt_ledger.approval import load_approval

    approval = load_approval()
    approval_dict = asdict(approval) if approval else None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "git_commit": _git_commit(root),
        "governance_sha256": _sha256_file(gov_path) if gov_path.is_file() else None,
        "environment": environment,
        "promoter": promoter,
        "manifest_pins": (manifest.get("environments") or {}).get(environment),
        "audit": {
            "passed": len([f for f in audit_findings if f.severity == "error"]) == 0,
            "findings": [asdict(f) for f in audit_findings],
        },
        "manifest_validation": {
            "passed": len([i for i in manifest_issues if i.severity == "error"]) == 0,
            "issues": [asdict(i) for i in manifest_issues],
        },
        "scenarios": {
            "passed": all(r.ok for r in scenario_results),
            "results": [
                {"id": r.scenario_id, "ok": r.ok, "errors": r.errors}
                for r in scenario_results
            ],
        },
        "approval": approval_dict,
    }


def export_evidence(path: Path, **kwargs: Any) -> Path:
    payload = build_evidence(**kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
