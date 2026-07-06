"""Tests for judge adjudication and validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legaleval.data.schema import EvalExample
from legaleval.judge.adjudicate import adjudicate_case
from legaleval.judge.borderline import (
    BorderlineCase,
    borderline_cases_from_rows,
    is_borderline_jaccard,
)
from legaleval.judge.config import load_judge_config
from legaleval.judge.prompt import parse_judge_response
from legaleval.judge.validate import (
    MIN_KAPPA,
    build_validation_pool,
    compute_agreement,
    reference_span_correct,
    run_validation,
    stratified_sample,
    validate_and_exit,
    ValidationResult,
)
from legaleval.metrics.compute import JoinedRow
from legaleval.models.runner import ModelClient, RawResponse


class StubJudgeClient(ModelClient):
    provider = "stub"

    def __init__(self, *, span_correct: bool) -> None:
        super().__init__(name="judge", model_id="stub-judge", api_key="test")
        self._span_correct = span_correct

    def _complete(self, prompt: str, system: str) -> RawResponse:
        return RawResponse(
            text=json.dumps(
                {
                    "span_correct": self._span_correct,
                    "rationale": "stub",
                }
            ),
            latency_ms=5.0,
        )


class RuleMirrorJudge(ModelClient):
    """Judge that mirrors the gold reference rule (for high-kappa validation tests)."""

    provider = "stub"

    def __init__(self) -> None:
        super().__init__(name="judge", model_id="rule", api_key="x")

    def _complete(self, prompt: str, system: str) -> RawResponse:
        predicted = prompt.split("Model predicted span:")[1].split("---")[1].strip()
        gold = prompt.split("Gold reference span")[1].split("---")[1].strip()
        excerpt = prompt.split("Contract excerpt:")[1].split("---")[1].strip()
        correct = reference_span_correct(predicted, [gold], excerpt)
        return RawResponse(
            text=json.dumps({"span_correct": correct, "rationale": "mirrors reference"}),
            latency_ms=1.0,
        )


def _example(
    example_id: str,
    *,
    present: bool,
    excerpt: str,
    gold_spans: list[str],
    category: str = "Anti-Assignment",
) -> EvalExample:
    return EvalExample(
        id=example_id,
        contract_excerpt=excerpt,
        category=category,
        present=present,
        gold_spans=gold_spans,
        contract_title=f"Contract-{example_id}",
    )


def test_is_borderline_jaccard() -> None:
    assert is_borderline_jaccard(0.5)
    assert is_borderline_jaccard(0.2)
    assert is_borderline_jaccard(0.7)
    assert not is_borderline_jaccard(0.19)
    assert not is_borderline_jaccard(0.71)


def test_borderline_cases_from_rows() -> None:
    rows = [
        JoinedRow(
            example_id="a",
            category="Anti-Assignment",
            model="m",
            gold_present=True,
            gold_spans=["Assignment requires consent"],
            contract_excerpt="Assignment requires consent.",
            pred_present=True,
            pred_span="requires consent",
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="b",
            category="Anti-Assignment",
            model="m",
            gold_present=True,
            gold_spans=["Assignment requires consent"],
            contract_excerpt="Assignment requires consent.",
            pred_present=True,
            pred_span="Assignment requires consent",
            has_api_error=False,
            has_parse_error=False,
        ),
    ]
    borderline = borderline_cases_from_rows(rows)
    assert len(borderline) == 1
    assert borderline[0].example_id == "a"


def test_parse_judge_response() -> None:
    decision, err = parse_judge_response(
        '{"span_correct": true, "rationale": "Same clause."}'
    )
    assert err is None
    assert decision is not None
    assert decision.span_correct is True


def test_reference_span_correct() -> None:
    gold = ["Assignment requires consent"]
    excerpt = "Assignment requires consent."
    assert reference_span_correct("Assignment requires consent", gold, excerpt)
    assert not reference_span_correct("totally wrong", gold, excerpt)


def test_build_validation_pool_and_stratified_sample() -> None:
    examples = [
        _example(
            "e1",
            present=True,
            excerpt="Assignment requires consent. Liability cap is one million.",
            gold_spans=["Assignment requires consent"],
            category="Anti-Assignment",
        ),
        _example(
            "e2",
            present=True,
            excerpt="Audits may occur annually under section four.",
            gold_spans=["Audits may occur annually"],
            category="Audit Rights",
        ),
    ]
    pool = build_validation_pool(examples)
    assert len(pool) >= 4
    sample = stratified_sample(pool, sample_size=4, seed=1)
    assert len(sample) == 4


def test_compute_agreement_perfect() -> None:
    results = [
        ValidationResult(
            example_id="a",
            category="c",
            token_jaccard=0.5,
            reference_span_correct=True,
            judge_span_correct=True,
            judge_rationale="ok",
            agrees_with_reference=True,
            stratum="gray",
        ),
        ValidationResult(
            example_id="b",
            category="c",
            token_jaccard=0.3,
            reference_span_correct=False,
            judge_span_correct=False,
            judge_rationale="no",
            agrees_with_reference=True,
            stratum="gray",
        ),
    ]
    agreement = compute_agreement(results)
    assert agreement["accuracy"] == 1.0
    assert agreement["cohens_kappa"] == 1.0
    assert agreement["passes_threshold"] is True


def test_compute_agreement_fails_kappa() -> None:
    results = [
        ValidationResult(
            example_id="a",
            category="c",
            token_jaccard=0.5,
            reference_span_correct=True,
            judge_span_correct=False,
            judge_rationale="no",
            agrees_with_reference=False,
            stratum="gray",
        ),
        ValidationResult(
            example_id="b",
            category="c",
            token_jaccard=0.3,
            reference_span_correct=False,
            judge_span_correct=True,
            judge_rationale="yes",
            agrees_with_reference=False,
            stratum="gray",
        ),
    ]
    agreement = compute_agreement(results)
    assert agreement["cohens_kappa"] is not None
    assert agreement["cohens_kappa"] < MIN_KAPPA
    assert agreement["passes_threshold"] is False


def test_validate_and_exit_passes_with_rule_mirror_judge(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.jsonl"
    examples = [
        _example(
            f"v{i}",
            present=True,
            excerpt="Assignment requires consent. Extra clause text here.",
            gold_spans=["Assignment requires consent"],
            category="Anti-Assignment",
        )
        for i in range(5)
    ]
    eval_path.write_text(
        "\n".join(ex.model_dump_json() for ex in examples) + "\n",
        encoding="utf-8",
    )
    exit_code = validate_and_exit(
        eval_path, sample_size=8, seed=0, client=RuleMirrorJudge()
    )
    assert exit_code == 0


def test_validate_and_exit_fails_with_inverted_judge(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.jsonl"
    examples = [
        _example(
            f"v{i}",
            present=True,
            excerpt="Assignment requires consent. Extra clause text here.",
            gold_spans=["Assignment requires consent"],
            category="Anti-Assignment",
        )
        for i in range(8)
    ]
    eval_path.write_text(
        "\n".join(ex.model_dump_json() for ex in examples) + "\n",
        encoding="utf-8",
    )
    exit_code = validate_and_exit(
        eval_path, sample_size=8, seed=0, client=StubJudgeClient(span_correct=False)
    )
    assert exit_code == 1


def test_adjudicate_case_records_parse_failure() -> None:
    class BadJudge(ModelClient):
        provider = "stub"

        def __init__(self) -> None:
            super().__init__(name="judge", model_id="bad", api_key="x")

        def _complete(self, prompt: str, system: str) -> RawResponse:
            return RawResponse(text="not json", latency_ms=1.0)

    case = BorderlineCase(
        example_id="x",
        category="Anti-Assignment",
        contract_excerpt="Assignment requires consent.",
        contract_title="T",
        gold_spans=["Assignment requires consent"],
        predicted_span="requires consent",
        token_jaccard=0.5,
        model="m",
    )
    row = adjudicate_case(BadJudge(), case, run_id="r1")
    assert row.parse_error is not None
    assert row.span_correct is None


def test_load_judge_config() -> None:
    config = load_judge_config()
    assert config.name == "judge"
    assert "TODO" in config.model_id


def test_run_validation_writes_agreement_fields(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.jsonl"
    eval_path.write_text(
        _example(
            "one",
            present=True,
            excerpt="Assignment requires consent.",
            gold_spans=["Assignment requires consent"],
        ).model_dump_json()
        + "\n",
        encoding="utf-8",
    )
    payload = run_validation(eval_path, sample_size=4, seed=0, client=RuleMirrorJudge())
    assert "agreement" in payload
    assert payload["agreement"]["cohens_kappa"] is not None
