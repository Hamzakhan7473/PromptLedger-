"""Deep Agents orchestrator with extract/validate subagents."""

from __future__ import annotations

from typing import Any

from legaleval.agents.config import register_legaleval_harness_profile
from legaleval.agents.tools import make_clause_tools
from legaleval.data.schema import EvalExample
from legaleval.models.prompt import build_user_prompt
from legaleval.models.runner import ModelClient

ORCHESTRATOR_SYSTEM = """You are a legal clause analysis orchestrator.

For each request:
1. Delegate extraction to the extractor subagent (draft JSON prediction).
2. Delegate validation to the validator subagent (check verbatim span + category fit).
3. Return ONE final JSON object only:
   {"present": <bool>, "span": <string or null>, "confidence": <0-1>, "reasoning": <string>}

Use subagents via the task tool. Do not skip validation.
Final response must be JSON only — no markdown, no prose outside the JSON object."""


def orchestrator_tool_names(agent: object) -> set[str]:
    """Return tool names registered on the main agent ToolNode (pre-exclusion)."""
    node = agent.nodes["tools"]  # type: ignore[attr-defined]
    while hasattr(node, "bound"):
        node = node.bound
    tools_by_name = getattr(node, "tools_by_name", None)
    if tools_by_name is None:
        return set()
    return set(tools_by_name)


def build_clause_agent(
    model: str,
    client: ModelClient,
    example_ref: list[EvalExample],
) -> Any:
    """Create a Deep Agents graph for one model configuration."""
    from deepagents import create_deep_agent
    from deepagents.middleware.subagents import SubAgent

    register_legaleval_harness_profile(model)
    extract_clause, validate_extraction = make_clause_tools(client, example_ref)
    tools = [extract_clause, validate_extraction]

    subagents: list[SubAgent] = [
        SubAgent(
            name="extractor",
            description=(
                "Drafts clause presence and verbatim span from contract excerpts. "
                "Use for the initial extraction step."
            ),
            system_prompt=(
                "You extract legal clause spans. The contract excerpt is already bound "
                "to extract_clause — call extract_clause with no arguments. Return the "
                "tool JSON output."
            ),
            tools=[extract_clause],
        ),
        SubAgent(
            name="validator",
            description=(
                "Validates draft extractions for verbatim spans and category fit. "
                "Use after extraction."
            ),
            system_prompt=(
                "You validate legal extractions. The contract excerpt is already bound "
                "to validate_extraction — call validate_extraction with the draft JSON "
                "string only. Return the tool JSON output."
            ),
            tools=[validate_extraction],
        ),
    ]

    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=ORCHESTRATOR_SYSTEM,
        subagents=subagents,
    )


def build_agent_user_message(example: EvalExample) -> str:
    return (
        f"{build_user_prompt(example)}\n\n"
        "Run the full agent workflow (extract → validate) and return the final JSON prediction."
    )


def extract_agent_response_text(result: dict[str, Any]) -> str:
    messages = result.get("messages") or []
    for message in reversed(messages):
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")
        if not content:
            continue
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
            joined = "".join(parts).strip()
            if joined:
                return joined
        return str(content)
    return ""
