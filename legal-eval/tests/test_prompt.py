"""Tests for eval prompt parsing."""

from __future__ import annotations

import pytest

from legaleval.data.schema import EvalExample
from legaleval.models.prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
    parse_model_response,
)


@pytest.fixture
def example() -> EvalExample:
    return EvalExample(
        id="test-001",
        contract_excerpt="The liability cap is one million dollars.",
        category="Cap On Liability",
        present=True,
        gold_spans=["liability cap is one million dollars"],
        contract_title="Test Contract",
    )


def test_build_user_prompt_includes_category_and_excerpt(example: EvalExample) -> None:
    prompt = build_user_prompt(example)
    assert example.category in prompt
    assert example.contract_excerpt in prompt
    assert example.contract_title in prompt


def test_system_prompt_requires_json_only() -> None:
    assert "JSON only" in SYSTEM_PROMPT
    assert '"present"' in SYSTEM_PROMPT


def test_parse_valid_json() -> None:
    raw = (
        '{"present": true, "span": "liability cap", '
        '"confidence": 0.9, "reasoning": "Explicit cap language."}'
    )
    prediction, error = parse_model_response(raw)
    assert error is None
    assert prediction is not None
    assert prediction.present is True
    assert prediction.span == "liability cap"


def test_parse_fenced_json() -> None:
    raw = """```json
{"present": false, "span": null, "confidence": 0.8, "reasoning": "Not found."}
```"""
    prediction, error = parse_model_response(raw)
    assert error is None
    assert prediction is not None
    assert prediction.present is False
    assert prediction.span is None


def test_parse_invalid_json_returns_error() -> None:
    prediction, error = parse_model_response("not json at all")
    assert prediction is None
    assert error is not None


def test_parse_present_without_span_returns_error() -> None:
    raw = '{"present": true, "span": null, "confidence": 0.5, "reasoning": "x"}'
    prediction, error = parse_model_response(raw)
    assert prediction is None
    assert "span" in (error or "").lower()
