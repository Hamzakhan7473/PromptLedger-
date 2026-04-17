from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml
from prompt_ledger.paths import governance_path, repo_root
from prompt_ledger.registry import PromptPack, PromptVersion, discover_registry


@dataclass(frozen=True)
class AuditFinding:
    severity: str  # "error" | "warning"
    prompt_id: str
    version: str
    code: str
    message: str


def _merge_governance(
    gov: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(gov)
    for k, v in overrides.items():
        if k == "required_markers" and isinstance(v, list) and v == []:
            merged[k] = []
            continue
        merged[k] = v
    return merged


def _check_banned(combined: str, banned: list[str]) -> list[str]:
    problems: list[str] = []
    lower = combined.lower()
    for phrase in banned:
        if phrase.lower() in lower:
            problems.append(f"Banned phrase: {phrase!r}")
    return problems


def _check_markers(combined: str, markers: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    for m in markers:
        pattern = m["pattern"]
        message = m.get("message", "Required marker missing")
        if not re.search(pattern, combined):
            problems.append(message)
    return problems


def _check_rag_templates(user: str, combined: str, rag: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    placeholder = rag.get("context_placeholder", "{retrieved_context}")
    if rag.get("require_placeholder_in_user", True):
        if placeholder not in user:
            problems.append(f"User template must include context placeholder {placeholder!r}")

    cite_cfg = rag.get("citation_instruction") or {}
    if cite_cfg.get("required"):
        haystack = combined.lower()
        if not any(s.lower() in haystack for s in cite_cfg.get("must_contain_any", [])):
            problems.append("Citation instruction must require citing retrieved material")

    refuse_cfg = rag.get("refuse_without_context") or {}
    if refuse_cfg.get("enabled"):
        haystack = combined.lower()
        if not any(s.lower() in haystack for s in refuse_cfg.get("must_contain_any", [])):
            problems.append("Must instruct refusal when context is insufficient")
    return problems


def _schema_exists(repo: Path, relative_schema: str) -> bool:
    path = (repo / relative_schema).resolve()
    try:
        path.relative_to(repo.resolve())
    except ValueError:
        return False
    return path.is_file()


def audit_version(
    pack: PromptPack,
    version: str,
    pv: PromptVersion,
    gov: dict[str, Any],
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    merged = _merge_governance(gov, pv.audit_overrides)
    combined = f"{pv.system}\n{pv.user}"

    rag = merged.get("rag") or {}
    for msg in _check_rag_templates(pv.user, combined, rag):
        findings.append(
            AuditFinding("error", pack.prompt_id, version, "rag_policy", msg),
        )

    for msg in _check_banned(combined, merged.get("banned_phrases", [])):
        findings.append(
            AuditFinding("error", pack.prompt_id, version, "banned_phrase", msg),
        )

    markers = merged.get("required_markers") or []
    if markers:
        for msg in _check_markers(combined, markers):
            findings.append(
                AuditFinding("error", pack.prompt_id, version, "required_marker", msg),
            )

    if pv.output_schema:
        root = repo_root()
        if not _schema_exists(root, pv.output_schema):
            findings.append(
                AuditFinding(
                    "error",
                    pack.prompt_id,
                    version,
                    "missing_schema",
                    f"Output schema not found: {pv.output_schema}",
                ),
            )
        else:
            import json

            json.loads((root / pv.output_schema).read_text(encoding="utf-8"))

    return findings


def run_audit(registry_root: Path | None = None) -> list[AuditFinding]:
    root = repo_root()
    reg = registry_root or (root / "prompts" / "registry")
    gov = read_yaml(governance_path())
    packs = discover_registry(reg)
    all_findings: list[AuditFinding] = []
    for pack in packs.values():
        for ver, pv in pack.versions.items():
            all_findings.extend(audit_version(pack, ver, pv, gov))
    return all_findings
