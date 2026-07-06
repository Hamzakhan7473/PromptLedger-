"""Token accounting for agent-mode eval runs."""

from __future__ import annotations

from typing import Any

from legaleval.models.runner import ModelClient, RawResponse


class TokenUsageTracker:
    """Accumulates usage from ModelClient.complete calls inside agent tools."""

    def __init__(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.tool_call_count = 0

    def reset(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.tool_call_count = 0

    def add(self, response: RawResponse) -> None:
        self.tool_call_count += 1
        if response.input_tokens is not None:
            self.input_tokens += response.input_tokens
        if response.output_tokens is not None:
            self.output_tokens += response.output_tokens


class TrackingModelClient:
    """ModelClient wrapper that records token usage from tool-layer completions."""

    def __init__(self, client: ModelClient, tracker: TokenUsageTracker) -> None:
        self._client = client
        self._tracker = tracker
        self.provider = client.provider
        self.name = client.name
        self.model_id = client.model_id

    def complete(self, prompt: str, system: str) -> RawResponse:
        response = self._client.complete(prompt, system)
        self._tracker.add(response)
        return response

    def close(self) -> None:
        self._client.close()


def _message_usage(message: object) -> dict[str, Any] | None:
    usage = getattr(message, "usage_metadata", None)
    if usage is None and isinstance(message, dict):
        usage = message.get("usage_metadata")
    return usage if isinstance(usage, dict) else None


def sum_orchestrator_message_tokens(result: dict[str, Any]) -> tuple[int | None, int | None]:
    """Sum usage_metadata on AIMessages returned by agent.invoke.

    Coverage depends on the LangChain chat model populating usage_metadata on
    orchestrator/subagent model turns. Tool-layer completions are tracked
    separately via TrackingModelClient.
    """
    input_total = 0
    output_total = 0
    saw_usage = False
    for message in result.get("messages") or []:
        usage = _message_usage(message)
        if not usage:
            continue
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if input_tokens is None and output_tokens is None:
            continue
        saw_usage = True
        input_total += int(input_tokens or 0)
        output_total += int(output_tokens or 0)
    if not saw_usage:
        return None, None
    return input_total, output_total


def combine_agent_token_counts(
    tool_tracker: TokenUsageTracker,
    orchestrator_input: int | None,
    orchestrator_output: int | None,
) -> tuple[int | None, int | None, int | None]:
    """Merge tool + orchestrator token counts for CallLogRow fields."""
    tool_in = tool_tracker.input_tokens if tool_tracker.tool_call_count else None
    tool_out = tool_tracker.output_tokens if tool_tracker.tool_call_count else None

    if tool_in is None and orchestrator_input is None:
        input_tokens: int | None = None
    else:
        input_tokens = int(tool_in or 0) + int(orchestrator_input or 0)

    if tool_out is None and orchestrator_output is None:
        output_tokens: int | None = None
    else:
        output_tokens = int(tool_out or 0) + int(orchestrator_output or 0)

    if input_tokens is None and output_tokens is None:
        total_tokens = None
    else:
        total_tokens = int(input_tokens or 0) + int(output_tokens or 0)

    return input_tokens, output_tokens, total_tokens
