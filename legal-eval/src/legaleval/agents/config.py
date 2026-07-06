"""Deep Agents harness tuning for legal-eval clause extraction."""

from __future__ import annotations

import os

from deepagents import GeneralPurposeSubagentProfile, HarnessProfileConfig, register_harness_profile

# Built-in deepagents tools not used by extract → validate (see create_deep_agent docs,
# deepagents/graph.py). Excluded via HarnessProfile.excluded_tools + _ToolExclusionMiddleware.
LEGALEVAL_EXCLUDED_TOOLS: frozenset[str] = frozenset(
    {
        "write_todos",
        "ls",
        "read_file",
        "write_file",
        "edit_file",
        "glob",
        "grep",
        "execute",
    },
)

# Middleware stripped from main + subagent stacks (FilesystemMiddleware and
# SubAgentMiddleware are required scaffolding and cannot be excluded).
LEGALEVAL_EXCLUDED_MIDDLEWARE: frozenset[str] = frozenset(
    {
        "SummarizationMiddleware",
        "TodoListMiddleware",
    },
)

DEFAULT_AGENT_RECURSION_LIMIT = 25
DEFAULT_AGENT_INVOKE_TIMEOUT_S = 600.0

_REGISTERED_MODELS: set[str] = set()


def agent_recursion_limit(explicit: int | None = None) -> int:
    """LangGraph recursion_limit for a single agent.invoke call."""
    if explicit is not None:
        return explicit
    raw = os.environ.get("LEGAL_EVAL_AGENT_RECURSION_LIMIT")
    if raw is None or raw.strip() == "":
        return DEFAULT_AGENT_RECURSION_LIMIT
    return int(raw)


def agent_invoke_timeout_s(explicit: float | None = None) -> float:
    """Wall-clock timeout (seconds) for a single agent.invoke call."""
    if explicit is not None:
        return explicit
    raw = os.environ.get("LEGAL_EVAL_AGENT_INVOKE_TIMEOUT_S")
    if raw is None or raw.strip() == "":
        return DEFAULT_AGENT_INVOKE_TIMEOUT_S
    return float(raw)


def agent_invoke_config(*, recursion_limit: int | None = None) -> dict[str, object]:
    """RunnableConfig kwargs passed to CompiledStateGraph.invoke."""
    return {"recursion_limit": agent_recursion_limit(recursion_limit)}


def register_legaleval_harness_profile(model_spec: str) -> None:
    """Register per-model harness profile that trims deepagents defaults.

    Uses deepagents' register_harness_profile (HarnessProfileConfig.excluded_tools
    and excluded_middleware). Registrations merge additively if called repeatedly
    for the same model spec.
    """
    if model_spec in _REGISTERED_MODELS:
        return
    register_harness_profile(
        model_spec,
        HarnessProfileConfig(
            excluded_tools=LEGALEVAL_EXCLUDED_TOOLS,
            excluded_middleware=LEGALEVAL_EXCLUDED_MIDDLEWARE,
            general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
        ),
    )
    _REGISTERED_MODELS.add(model_spec)
