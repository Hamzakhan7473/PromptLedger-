"""Tests for Deep Agents harness helpers."""

from __future__ import annotations

import os
from concurrent.futures import TimeoutError as FuturesTimeoutError
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from legaleval.agents.config import (
    DEFAULT_AGENT_INVOKE_TIMEOUT_S,
    DEFAULT_AGENT_RECURSION_LIMIT,
    LEGALEVAL_EXCLUDED_MIDDLEWARE,
    LEGALEVAL_EXCLUDED_TOOLS,
    agent_invoke_config,
    agent_invoke_timeout_s,
    register_legaleval_harness_profile,
)
from legaleval.agents.harness import (
    build_clause_agent,
    extract_agent_response_text,
    orchestrator_tool_names,
)
from legaleval.agents.model_strings import to_deepagents_model
from legaleval.agents.runner import execute_agent_example, invoke_agent_with_limits
from legaleval.agents.tokens import (
    TokenUsageTracker,
    TrackingModelClient,
    combine_agent_token_counts,
    sum_orchestrator_message_tokens,
)
from legaleval.agents.tools import make_clause_tools
from legaleval.data.schema import EvalExample
from legaleval.models.runner import CallLogRow, ModelConfig, RawResponse


def test_to_deepagents_model_openai() -> None:
    config = ModelConfig(
        name="openai",
        provider="openai",
        model_id="gpt-5.4-mini",
        env_key="OPENAI_API_KEY",
    )
    assert to_deepagents_model(config) == "openai:gpt-5.4-mini"


def test_to_deepagents_model_google() -> None:
    config = ModelConfig(
        name="google",
        provider="google",
        model_id="gemini-2.5-flash",
        env_key="GOOGLE_API_KEY",
    )
    assert to_deepagents_model(config) == "google_genai:gemini-2.5-flash"


def test_extract_agent_response_text() -> None:
    result = {
        "messages": [
            AIMessage(
                content='{"present": true, "span": "foo", "confidence": 0.9, "reasoning": "ok"}',
            ),
        ],
    }
    text = extract_agent_response_text(result)
    assert '"present": true' in text


def test_register_legaleval_harness_profile_merges_exclusions() -> None:
    from deepagents.profiles.harness.harness_profiles import _get_harness_profile

    model_spec = "openai:gpt-4o-mini-legaleval-test"
    register_legaleval_harness_profile(model_spec)
    profile = _get_harness_profile(model_spec)
    assert profile is not None
    assert LEGALEVAL_EXCLUDED_TOOLS.issubset(profile.excluded_tools)
    assert LEGALEVAL_EXCLUDED_MIDDLEWARE.issubset(profile.excluded_middleware)
    assert profile.general_purpose_subagent is not None
    assert profile.general_purpose_subagent.enabled is False


def test_agent_limits_read_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEGAL_EVAL_AGENT_RECURSION_LIMIT", "17")
    monkeypatch.setenv("LEGAL_EVAL_AGENT_INVOKE_TIMEOUT_S", "42")
    assert agent_invoke_config()["recursion_limit"] == 17
    assert agent_invoke_timeout_s() == 42.0


def test_agent_limits_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LEGAL_EVAL_AGENT_RECURSION_LIMIT", raising=False)
    monkeypatch.delenv("LEGAL_EVAL_AGENT_INVOKE_TIMEOUT_S", raising=False)
    assert agent_invoke_config()["recursion_limit"] == DEFAULT_AGENT_RECURSION_LIMIT
    assert agent_invoke_timeout_s() == DEFAULT_AGENT_INVOKE_TIMEOUT_S


def test_build_clause_agent_excludes_defaults_from_model_view() -> None:
    os.environ.setdefault("OPENAI_API_KEY", "sk-test")

    class FakeClient:
        provider = "openai"
        name = "openai"
        model_id = "gpt-4o-mini"

        def complete(self, prompt: str, system: str) -> RawResponse:
            return RawResponse(text="{}", latency_ms=1.0, input_tokens=1, output_tokens=1)

        def close(self) -> None:
            return None

    example_ref: list[EvalExample] = [
        EvalExample(
            id="ex-1",
            contract_excerpt="Sample excerpt",
            category="Termination",
            present=False,
            gold_spans=[],
            contract_title="Acme MSA",
        ),
    ]
    agent = build_clause_agent("openai:gpt-4o-mini", FakeClient(), example_ref)
    tool_names = orchestrator_tool_names(agent)
    assert "task" in tool_names
    assert "extract_clause" in tool_names
    assert "validate_extraction" in tool_names
    assert "write_todos" not in tool_names  # TodoListMiddleware excluded via harness profile

    from deepagents.middleware._tool_exclusion import _ToolExclusionMiddleware

    profile_tools = LEGALEVAL_EXCLUDED_TOOLS
    middleware = _ToolExclusionMiddleware(excluded=profile_tools)
    visible = sorted(name for name in tool_names if name not in profile_tools)
    assert visible == ["extract_clause", "task", "validate_extraction"]
    assert middleware._excluded == profile_tools


def test_make_clause_tools_use_bound_example_not_llm_args() -> None:
    class FakeClient:
        provider = "openai"
        name = "openai"
        model_id = "gpt-4o-mini"
        prompts: list[str] = []

        def complete(self, prompt: str, system: str) -> RawResponse:
            self.prompts.append(prompt)
            return RawResponse(text='{"present": false}', latency_ms=1.0)

    example = EvalExample(
        id="ex-1",
        contract_excerpt="BOUND EXCERPT TEXT",
        category="Termination",
        present=False,
        gold_spans=[],
        contract_title="Acme MSA",
    )
    client = FakeClient()
    extract_clause, validate_extraction = make_clause_tools(client, [example])
    extract_clause()
    validate_extraction('{"present": false}')
    assert "BOUND EXCERPT TEXT" in client.prompts[0]
    assert "BOUND EXCERPT TEXT" in client.prompts[1]
    assert "Termination" in client.prompts[0]


def test_token_logging_from_tools_and_orchestrator_messages() -> None:
    tracker = TokenUsageTracker()
    tracker.add(RawResponse(text="a", latency_ms=1.0, input_tokens=100, output_tokens=20))
    tracker.add(RawResponse(text="b", latency_ms=1.0, input_tokens=50, output_tokens=10))

    result = {
        "messages": [
            AIMessage(
                content="x",
                usage_metadata={"input_tokens": 30, "output_tokens": 5, "total_tokens": 35},
            ),
        ],
    }
    orch_in, orch_out = sum_orchestrator_message_tokens(result)
    row_in, row_out, row_total = combine_agent_token_counts(tracker, orch_in, orch_out)
    assert row_in == 180
    assert row_out == 35
    assert row_total == 215


def test_execute_agent_example_populates_token_fields() -> None:
    example = EvalExample(
        id="ex-1",
        contract_excerpt="text",
        category="Termination",
        present=False,
        gold_spans=[],
        contract_title="Contract",
    )
    token_tracker = TokenUsageTracker()

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content='{"present": false, "span": null, "confidence": 0.5, "reasoning": "none"}',
                usage_metadata={"input_tokens": 7, "output_tokens": 2, "total_tokens": 9},
            ),
        ],
    }

    class FakeInnerClient:
        provider = "openai"
        name = "openai"
        model_id = "gpt-4o-mini"

        def complete(self, prompt: str, system: str) -> RawResponse:
            return RawResponse(text="{}", latency_ms=1.0)

        def close(self) -> None:
            return None

    client = TrackingModelClient(FakeInnerClient(), token_tracker)
    config = ModelConfig(
        name="openai",
        provider="openai",
        model_id="gpt-4o-mini",
        env_key="OPENAI_API_KEY",
    )
    example_ref: list[EvalExample] = []

    row = execute_agent_example(
        mock_agent,
        example,
        run_id="run-1",
        config=config,
        client=client,
        token_tracker=token_tracker,
        example_ref=example_ref,
        recursion_limit=9,
        timeout_s=30.0,
    )

    assert isinstance(row, CallLogRow)
    assert row.input_tokens == 7
    assert row.output_tokens == 2
    assert row.total_tokens == 9
    assert row.error is None
    mock_agent.invoke.assert_called_once()
    _args, kwargs = mock_agent.invoke.call_args
    assert kwargs["config"] == {"recursion_limit": 9}


def test_invoke_agent_with_limits_applies_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import legaleval.agents.runner as runner_module

    agent = MagicMock()
    mock_future = MagicMock()
    mock_future.result.side_effect = FuturesTimeoutError()
    mock_pool = MagicMock()
    mock_pool.__enter__.return_value = mock_pool
    mock_pool.submit.return_value = mock_future
    monkeypatch.setattr(runner_module, "ThreadPoolExecutor", lambda *a, **k: mock_pool)

    with pytest.raises(TimeoutError, match="wall-clock timeout"):
        invoke_agent_with_limits(agent, {"messages": []}, timeout_s=0.01)
