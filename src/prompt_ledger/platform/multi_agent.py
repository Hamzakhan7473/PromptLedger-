from __future__ import annotations

from typing import Any

from prompt_ledger.platform.config import load_platform_yaml
from prompt_ledger.platform.orchestrator import run_agent_task


def load_supervisor_graph() -> dict[str, Any]:
    return load_platform_yaml("multi_agent.yaml")


def run_supervisor_task(
    environment: str,
    task: str,
    *,
    agents: list[str] | None = None,
) -> dict[str, Any]:
    """
    Multi-agent run (LangGraph + Temporal stub).
    Invokes orchestrator per selected sub-agent environment mapping.
    """
    graph = load_supervisor_graph()
    selected = agents or [a["id"] for a in graph.get("agents", [])]
    results: list[dict[str, Any]] = []

    env_map = {
        "tax_agent": "tax",
        "legal_agent": "legal",
        "retrieval_agent": "research",
        "excel_agent": "financial_modeling",
        "ppt_agent": "research",
        "citation_agent": environment,
        "verification_agent": environment,
    }

    for agent_id in selected[:4]:
        env_key = env_map.get(agent_id, environment)
        try:
            r = run_agent_task(env_key, f"[{agent_id}] {task}", persist=False)
            results.append({"agent": agent_id, "environment": env_key, "reward": r["reward"]})
        except KeyError:
            results.append({"agent": agent_id, "error": "environment not found"})

    return {
        "supervisor": graph.get("supervisor", {}),
        "orchestration": graph.get("orchestration", {}),
        "agents_invoked": selected,
        "sub_results": results,
        "final_output": results[-1] if results else {},
        "metadata": {
            "langgraph": "stub",
            "temporal": "stub",
            "celery": "stub",
        },
    }
