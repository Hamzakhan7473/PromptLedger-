"""Tests for legaleval.smoke reporting and exit codes."""

from __future__ import annotations

import io

import pytest

from legaleval.data.schema import EvalExample
from legaleval.models.runner import CallLogRow, ModelConfig
from legaleval.smoke import (
    SMOKE_EXAMPLE_LIMIT,
    SmokeExampleOutcome,
    SmokeModelOutcome,
    is_parse_ok,
    render_smoke_report,
    run_smoke,
    run_smoke_model,
    smoke_exit_code,
)


@pytest.fixture
def examples() -> list[EvalExample]:
    return [
        EvalExample(
            id=f"ex-{idx}",
            contract_excerpt=f"Excerpt {idx}",
            category="Cat",
            present=idx % 2 == 0,
            gold_spans=[f"span {idx}"] if idx % 2 == 0 else [],
            contract_title=f"Title {idx}",
        )
        for idx in range(1, 4)
    ]


@pytest.fixture
def anthropic_config() -> ModelConfig:
    return ModelConfig(
        name="anthropic",
        provider="anthropic",
        model_id="claude-test",
        env_key="ANTHROPIC_API_KEY",
    )


def _row(
    example: EvalExample,
    *,
    parsed: dict | None,
    error: str | None = None,
    parse_error: str | None = None,
    latency_ms: float | None = 100.0,
) -> CallLogRow:
    return CallLogRow(
        run_id="smoke",
        example_id=example.id,
        category=example.category,
        contract_title=example.contract_title,
        provider="stub",
        model="anthropic",
        model_id="claude-test",
        latency_ms=latency_ms,
        parsed=parsed,
        error=error,
        parse_error=parse_error,
    )


def test_is_parse_ok() -> None:
    example = EvalExample(
        id="x",
        contract_excerpt="a",
        category="c",
        present=True,
        gold_spans=["a"],
        contract_title="T",
    )
    ok = _row(
        example,
        parsed={
            "present": True,
            "span": "a",
            "confidence": 0.9,
            "reasoning": "ok",
        },
    )
    bad = _row(example, parsed=None, parse_error="bad json")
    assert is_parse_ok(ok) is True
    assert is_parse_ok(bad) is False


def test_run_smoke_model_with_stub_executor(
    examples: list[EvalExample],
    anthropic_config: ModelConfig,
) -> None:
    payloads = [
        {
            "present": True,
            "span": "Excerpt 1",
            "confidence": 0.9,
            "reasoning": "r1",
        },
        {
            "present": False,
            "span": None,
            "confidence": 0.8,
            "reasoning": "r2",
        },
        None,
    ]

    def fake_client_factory(_config: ModelConfig):
        class _Client:
            def close(self) -> None:
                return None

        return _Client()

    def fake_executor(_client, example, *, run_id: str) -> CallLogRow:
        payload = payloads[int(example.id.split("-")[1]) - 1]
        if payload is None:
            return _row(example, parsed=None, parse_error="invalid", latency_ms=50.0)
        return _row(example, parsed=payload, latency_ms=100.0)

    result = run_smoke_model(
        anthropic_config,
        examples,
        client_factory=fake_client_factory,
        executor=fake_executor,
    )
    assert result.parse_ok_count == 2
    assert result.mean_latency_ms == 83.3
    assert result.outcomes[0].parsed_fields == {
        "present": True,
        "span": "Excerpt 1",
        "confidence": 0.9,
    }


def test_run_smoke_model_client_error(
    examples: list[EvalExample],
    anthropic_config: ModelConfig,
) -> None:
    def fail_factory(_config: ModelConfig):
        raise ValueError("Missing API key environment variable: ANTHROPIC_API_KEY")

    result = run_smoke_model(
        anthropic_config,
        examples,
        client_factory=fail_factory,
    )
    assert result.parse_ok_count == 0
    assert result.client_error is not None
    assert all(not outcome.parse_ok for outcome in result.outcomes)


def test_render_smoke_report_and_exit_code(
    examples: list[EvalExample],
    anthropic_config: ModelConfig,
) -> None:
    good = SmokeModelOutcome(model_name="good", config=anthropic_config)
    for example in examples:
        good.outcomes.append(
            SmokeExampleOutcome(
                example_id=example.id,
                row=_row(
                    example,
                    parsed={
                        "present": True,
                        "span": "x",
                        "confidence": 0.5,
                        "reasoning": "r",
                    },
                ),
            )
        )

    bad = SmokeModelOutcome(model_name="bad", config=anthropic_config)
    bad.client_error = "ValueError: missing key"
    for example in examples:
        bad.outcomes.append(
            SmokeExampleOutcome(
                example_id=example.id,
                row=_row(example, parsed=None, error=bad.client_error),
            )
        )

    partial = SmokeModelOutcome(model_name="partial", config=anthropic_config)
    partial.outcomes.append(
        SmokeExampleOutcome(
            example_id=examples[0].id,
            row=_row(
                examples[0],
                parsed={
                    "present": False,
                    "span": None,
                    "confidence": 0.4,
                    "reasoning": "r",
                },
            ),
        )
    )
    for example in examples[1:]:
        partial.outcomes.append(
            SmokeExampleOutcome(
                example_id=example.id,
                row=_row(example, parsed=None, error="API down"),
            )
        )

    buf = io.StringIO()
    render_smoke_report(
        [good, partial, bad],
        example_limit=SMOKE_EXAMPLE_LIMIT,
        stream=buf,
    )
    text = buf.getvalue()
    assert "PASSED (1): good" in text
    assert "PARTIAL (1): partial" in text
    assert "NEEDS ATTENTION (1): bad" in text
    assert '"present": true' in text
    assert "parse_ok: 3/3" in text
    assert "parse_ok: 0/3" in text

    assert smoke_exit_code([good, partial, bad]) == 1
    assert smoke_exit_code([good, partial]) == 0


def test_run_smoke_all_models(
    examples: list[EvalExample],
    anthropic_config: ModelConfig,
) -> None:
    configs = {
        "alpha": anthropic_config.model_copy(update={"name": "alpha"}),
        "beta": ModelConfig(
            name="beta",
            provider="openai",
            model_id="gpt-test",
            env_key="OPENAI_API_KEY",
        ),
    }

    def fake_client_factory(_config: ModelConfig):
        class _Client:
            def close(self) -> None:
                return None

        return _Client()

    def fake_executor(_client, example, *, run_id: str) -> CallLogRow:
        return _row(
            example,
            parsed={
                "present": True,
                "span": "s",
                "confidence": 0.7,
                "reasoning": "r",
            },
        )

    results = run_smoke(
        examples=examples,
        configs=configs,
        client_factory=fake_client_factory,
        executor=fake_executor,
    )
    assert [r.model_name for r in results] == ["alpha", "beta"]
    assert all(r.parse_ok_count == 3 for r in results)
