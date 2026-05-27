from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.audit import run_audit
from prompt_ledger.graphrag_bridge import context_from_index
from prompt_ledger.graphrag_cli import resolve_graphrag_invocation
from prompt_ledger.load import read_yaml
from prompt_ledger.manifest import get_pin, load_manifest, validate_manifest
from prompt_ledger.packs import verify_pack
from prompt_ledger.paths import repo_root
from prompt_ledger.promote import promote_environment
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.render import format_retrieved_context, render_prompt
from prompt_ledger.scenarios import _load_fixture, run_scenario_file


@dataclass(frozen=True)
class VerticalConfig:
    key: str
    label: str
    headline: str
    description: str
    prompt_id: str
    scenario_dir: str
    scenario_include: list[str]
    pack_dir: str
    corpus: str
    graphrag_question: str
    accent: str
    icon: str
    checks: list[str]


def demo_config_path() -> Path:
    return repo_root() / "demo" / "config.yaml"


def load_demo_config() -> dict[str, VerticalConfig]:
    raw = read_yaml(demo_config_path())
    out: dict[str, VerticalConfig] = {}
    for key, v in (raw.get("verticals") or {}).items():
        out[key] = VerticalConfig(
            key=key,
            label=str(v["label"]),
            headline=str(v["headline"]),
            description=str(v.get("description", "")).strip(),
            prompt_id=str(v["prompt_id"]),
            scenario_dir=str(v.get("scenario_dir", "tests/scenarios")),
            scenario_include=list(v.get("scenario_include") or []),
            pack_dir=str(v["pack_dir"]),
            corpus=str(v["corpus"]),
            graphrag_question=str(v.get("graphrag_question", "")),
            accent=str(v.get("accent", "#3d8bfd")),
            icon=str(v.get("icon", "•")),
            checks=list(v.get("checks") or []),
        )
    return out


def list_verticals() -> list[dict[str, Any]]:
    return [
        {
            "id": k,
            "label": v.label,
            "headline": v.headline,
            "accent": v.accent,
            "icon": v.icon,
            "prompt_id": v.prompt_id,
            "checks": v.checks,
        }
        for k, v in load_demo_config().items()
    ]


def _scenario_paths(v: VerticalConfig) -> list[Path]:
    root = repo_root()
    sdir = root / v.scenario_dir
    return [sdir / name for name in v.scenario_include]


def render_vertical_preview(v: VerticalConfig, *, environment: str = "staging") -> dict[str, Any]:
    root = repo_root()
    manifest = load_manifest()
    ver = get_pin(manifest, environment, v.prompt_id)
    if not ver:
        raise ValueError(f"no pin for {v.prompt_id} in {environment}")
    reg = discover_registry(root / "prompts" / "registry")
    pv = get_version(reg[v.prompt_id], ver)

    fixture_map = {
        "legal.contract_review": "tests/fixtures/rag/legal_policy_chunks.json",
        "finance.transaction_classification": "tests/fixtures/rag/finance_policy_chunks.json",
        "healthcare.clinical_guidance": "tests/fixtures/rag/healthcare_guidelines.json",
        "general.policy_support": "tests/fixtures/rag/general_policy_chunks.json",
    }
    variables_map = {
        "legal.contract_review": {"clause_text": "Late payment interest after grace period."},
        "finance.transaction_classification": {
            "transaction_json": '{"merchant":"Cafe","amount_usd":45,"attendees":2}',
        },
        "healthcare.clinical_guidance": {
            "clinical_question": "When should we evaluate post-operative fever?",
        },
        "general.policy_support": {
            "customer_question": "Can I get a refund on my annual plan?",
        },
    }

    fx_rel = fixture_map.get(v.prompt_id)
    retrieved = None
    if fx_rel:
        retrieved = format_retrieved_context(_load_fixture((root / fx_rel).resolve()))
    system_s, user_s = render_prompt(
        pv,
        retrieved_context=retrieved,
        variables=variables_map.get(v.prompt_id, {}),
    )
    return {
        "prompt_id": v.prompt_id,
        "version": ver,
        "environment": environment,
        "system": system_s,
        "user": user_s,
    }


def graphrag_index_path(vertical_key: str) -> Path:
    return repo_root() / ".data" / "demo" / f"{vertical_key}-index.json"


def bundled_graphrag_index(vertical_key: str) -> Path:
    return repo_root() / "demo" / "indexes" / f"{vertical_key}-index.json"


def ensure_graphrag_index(vertical_key: str) -> Path:
    """Use cached index, bundled demo index, or build via Go."""
    dest = graphrag_index_path(vertical_key)
    if dest.is_file():
        return dest
    bundled = bundled_graphrag_index(vertical_key)
    if bundled.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, dest)
        return dest
    built = build_graphrag_index(vertical_key)
    return Path(built["path"])


def build_graphrag_index(vertical_key: str) -> dict[str, Any]:
    v = load_demo_config()[vertical_key]
    root = repo_root()
    corpus = (root / v.corpus).resolve()
    if not corpus.is_file():
        raise FileNotFoundError(corpus)
    out = graphrag_index_path(vertical_key)
    out.parent.mkdir(parents=True, exist_ok=True)
    index_args = [
        "index",
        "-text",
        str(corpus),
        "-o",
        str(out),
        "-stub",
        "-algo",
        "hierarchical",
    ]
    cmd, cwd = resolve_graphrag_invocation(index_args)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__("os").environ, "PROMPT_LEDGER_ROOT": str(root)},
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return {"path": str(out), "stdout": proc.stdout.strip()}


def run_vertical_demo(vertical_key: str) -> dict[str, Any]:
    cfg = load_demo_config()
    if vertical_key not in cfg:
        raise KeyError(f"unknown vertical {vertical_key!r}")
    v = cfg[vertical_key]
    root = repo_root()

    scenario_results = []
    for path in _scenario_paths(v):
        scenario_results.append(asdict(run_scenario_file(path)))

    pack_issues = verify_pack(root / v.pack_dir)
    audit_findings = run_audit()
    relevant_audit = [
        asdict(f)
        for f in audit_findings
        if f.prompt_id in (v.prompt_id, "*")
    ]
    manifest_issues = [asdict(i) for i in validate_manifest()]

    promote_after, promote_diff = promote_environment(
        target="production",
        sync_from="staging",
        dry_run=True,
    )

    graphrag_block: dict[str, Any] = {"indexed": False}
    try:
        gr_path = ensure_graphrag_index(vertical_key)
        graphrag_block = {
            "indexed": True,
            "path": str(gr_path),
            "bundled": bundled_graphrag_index(vertical_key).is_file(),
            "context_preview": context_from_index(gr_path, question=v.graphrag_question)[:1200],
        }
    except (RuntimeError, FileNotFoundError) as e:
        graphrag_block = {"indexed": False, "error": str(e)}

    return {
        "vertical": vertical_key,
        "config": {
            "label": v.label,
            "headline": v.headline,
            "description": v.description,
            "accent": v.accent,
            "checks": v.checks,
            "prompt_id": v.prompt_id,
        },
        "preview": render_vertical_preview(v),
        "audit": {
            "passed": not any(f["severity"] == "error" for f in relevant_audit),
            "findings": relevant_audit,
        },
        "scenarios": {
            "passed": all(r["ok"] for r in scenario_results),
            "results": scenario_results,
        },
        "manifest": {
            "passed": not any(i["severity"] == "error" for i in manifest_issues),
            "issues": manifest_issues,
            "pins": load_manifest().get("environments", {}).get("staging", {}),
        },
        "pack": {
            "passed": not any(i.severity == "error" for i in pack_issues),
            "issues": [asdict(i) for i in pack_issues],
        },
        "promote": {"dry_run": True, "diff": promote_diff},
        "graphrag": graphrag_block,
        "evidence_summary": {
            "governance_checks": len(v.checks),
            "scenario_count": len(scenario_results),
        },
    }
