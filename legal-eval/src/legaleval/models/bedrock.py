"""Amazon Bedrock Runtime Converse helpers (tool-use structured output)."""

from __future__ import annotations

import json
from typing import Any

CLAUSE_PREDICTION_TOOL_NAME = "clause_prediction"

CLAUSE_PREDICTION_TOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "present": {
            "type": "boolean",
            "description": (
                "True only if the clause category is substantively addressed "
                "in the excerpt."
            ),
        },
        "span": {
            "type": "string",
            "description": (
                "Exact verbatim quote from the excerpt when present=true; "
                "empty string when present=false."
            ),
        },
        "confidence": {
            "type": "number",
            "description": "Certainty from 0.0 (guess) to 1.0 (certain).",
        },
        "reasoning": {
            "type": "string",
            "description": "Brief justification (1-3 sentences).",
        },
    },
    "required": ["present", "confidence", "reasoning"],
}


def build_tool_config(*, force_tool: bool = True) -> dict[str, Any]:
    """Tool configuration for Converse API structured clause predictions."""
    config: dict[str, Any] = {
        "tools": [
            {
                "toolSpec": {
                    "name": CLAUSE_PREDICTION_TOOL_NAME,
                    "description": (
                        "Record whether a clause category is present in the "
                        "contract excerpt and cite the supporting span."
                    ),
                    "inputSchema": {"json": CLAUSE_PREDICTION_TOOL_SCHEMA},
                }
            }
        ],
    }
    if force_tool:
        config["toolChoice"] = {"any": {}}
    return config


def extract_tool_input(response: dict[str, Any]) -> dict[str, Any]:
    """Parse the clause_prediction tool input from a Converse response."""
    message = response.get("output", {}).get("message") or {}
    content = message.get("content") or []
    for block in content:
        tool_use = block.get("toolUse")
        if not tool_use:
            continue
        if tool_use.get("name") != CLAUSE_PREDICTION_TOOL_NAME:
            continue
        tool_input = tool_use.get("input")
        if not isinstance(tool_input, dict):
            raise ValueError(
                f"tool {CLAUSE_PREDICTION_TOOL_NAME!r} input is not an object"
            )
        return tool_input
    raise ValueError(
        f"Bedrock response missing {CLAUSE_PREDICTION_TOOL_NAME!r} toolUse block"
    )


def tool_input_to_text(tool_input: dict[str, Any]) -> str:
    """Normalize tool input to JSON text for the shared parse pipeline."""
    payload = dict(tool_input)
    span = payload.get("span")
    if span == "":
        payload["span"] = None
    return json.dumps(payload, ensure_ascii=False)


def extract_text_content(response: dict[str, Any]) -> str:
    """Extract plain-text assistant content from a Converse response."""
    message = response.get("output", {}).get("message") or {}
    content = message.get("content") or []
    parts = [block["text"] for block in content if isinstance(block.get("text"), str)]
    if not parts:
        raise ValueError("Bedrock response missing text content")
    return "".join(parts)


def converse_usage_tokens(response: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    usage = response.get("usage") or {}
    input_tokens = usage.get("inputTokens")
    output_tokens = usage.get("outputTokens")
    total_tokens = usage.get("totalTokens")
    return (
        int(input_tokens) if input_tokens is not None else None,
        int(output_tokens) if output_tokens is not None else None,
        int(total_tokens) if total_tokens is not None else None,
    )
