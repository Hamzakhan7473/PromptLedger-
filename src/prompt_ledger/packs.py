from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml
from prompt_ledger.scenarios import run_all_scenarios


@dataclass(frozen=True)
class PackIssue:
    severity: str
    code: str
    message: str


def load_pack(pack_dir: Path) -> dict[str, Any]:
    meta = read_yaml(pack_dir / "pack.yaml")
    return meta


def verify_pack(pack_dir: Path, *, target_repo: Path | None = None) -> list[PackIssue]:
    """Verify pack layout and run pack scenarios against target repo root."""

    issues: list[PackIssue] = []
    pack_dir = pack_dir.resolve()
    meta_path = pack_dir / "pack.yaml"
    if not meta_path.is_file():
        return [PackIssue("error", "missing_pack_yaml", f"no pack.yaml in {pack_dir}")]

    meta = read_yaml(meta_path)
    name = meta.get("name", pack_dir.name)
    gov_rel = meta.get("governance")
    if gov_rel:
        gpath = pack_dir / gov_rel
        if not gpath.is_file():
            issues.append(
                PackIssue("error", "missing_governance", f"pack {name}: governance not found"),
            )

    scenario_dir = pack_dir / "scenarios"
    if not scenario_dir.is_dir():
        issues.append(
            PackIssue("error", "missing_scenarios", f"pack {name}: scenarios/ directory missing"),
        )
    else:
        files = list(scenario_dir.glob("*.yaml"))
        if not files:
            issues.append(
                PackIssue("warning", "no_scenarios", f"pack {name}: no scenario files matched"),
            )

    schemas = meta.get("required_schemas") or []
    for rel in schemas:
        if not (pack_dir / rel).is_file():
            issues.append(
                PackIssue("error", "missing_schema", f"pack {name}: schema {rel!r} missing"),
            )

    if scenario_dir.is_dir():
        results = run_all_scenarios(scenario_dir)
        for r in results:
            if not r.ok:
                issues.append(
                    PackIssue(
                        "error",
                        "scenario_failed",
                        f"{r.scenario_id}: {'; '.join(r.errors)}",
                    ),
                )

    return issues
