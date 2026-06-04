from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.audit import run_audit
from prompt_ledger.platform.config import load_platform_yaml
from prompt_ledger.platform.models import ToolCall
from prompt_ledger.scenarios import _load_fixture


@dataclass(frozen=True)
class ToolSpec:
    key: str
    label: str
    backend: str
    description: str


def load_tools() -> dict[str, ToolSpec]:
    raw = load_platform_yaml("tools.yaml")
    return {
        k: ToolSpec(
            key=k,
            label=str(v["label"]),
            backend=str(v.get("backend", "stub")),
            description=str(v.get("description", "")),
        )
        for k, v in (raw.get("tools") or {}).items()
    }


def list_tools() -> list[dict[str, str]]:
    return [
        {"id": t.key, "label": t.label, "backend": t.backend, "description": t.description}
        for t in load_tools().values()
    ]


_FIXTURE_BY_PROMPT = {
    "legal.contract_review": "tests/fixtures/rag/legal_policy_chunks.json",
    "finance.transaction_classification": "tests/fixtures/rag/finance_policy_chunks.json",
    "healthcare.clinical_guidance": "tests/fixtures/rag/healthcare_guidelines.json",
    "general.policy_support": "tests/fixtures/rag/general_policy_chunks.json",
}


def execute_tool(
    tool_id: str,
    *,
    prompt_id: str,
    repo_root: Path,
    task: str,
) -> ToolCall:
    started = time.perf_counter()
    spec = load_tools().get(tool_id)
    if not spec:
        return ToolCall(
            tool=tool_id,
            input={"task": task},
            output={"error": f"unknown tool {tool_id}"},
            latency_ms=0,
        )

    output: dict[str, Any] = {}
    if tool_id == "rag_retriever":
        rel = _FIXTURE_BY_PROMPT.get(prompt_id)
        if rel:
            chunks = _load_fixture((repo_root / rel).resolve())
            output = {"chunks": len(chunks), "preview": str(chunks)[:500]}
        else:
            output = {"chunks": 0, "preview": ""}
    elif tool_id == "citation_engine":
        findings = run_audit()
        relevant = [f for f in findings if f.prompt_id in (prompt_id, "*")]
        output = {
            "finding_count": len(relevant),
            "errors": sum(1 for f in relevant if f.severity == "error"),
        }
    elif tool_id == "calculator":
        output = {"result": "stub", "expression": task[:80]}
    elif tool_id in ("document_search", "excel_generator", "powerpoint_generator", "browser_agent", "code_interpreter"):
        output = {"status": "stub_ok", "tool": tool_id}
    else:
        output = {"status": "noop"}

    elapsed = (time.perf_counter() - started) * 1000
    return ToolCall(tool=tool_id, input={"task": task, "prompt_id": prompt_id}, output=output, latency_ms=elapsed)
