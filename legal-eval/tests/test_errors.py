"""Tests for failure taxonomy and error reports."""

from __future__ import annotations

from pathlib import Path

from legaleval.report.errors import (
    ErrorType,
    classify_error,
    classify_model_errors,
    count_by_category_and_bucket,
    render_error_report,
    write_error_report,
)
from legaleval.report.records import EnrichedRow


def _row(
    example_id: str,
    *,
    category: str = "Anti-Assignment",
    gold_present: bool = True,
    gold_spans: list[str] | None = None,
    excerpt: str = "Assignment requires consent.",
    pred_present: bool | None = True,
    pred_span: str | None = "Assignment requires consent",
    confidence: float | None = 0.9,
    reasoning: str | None = "test",
    parse_error: bool = False,
    api_error: bool = False,
) -> EnrichedRow:
    return EnrichedRow(
        example_id=example_id,
        category=category,
        contract_title=f"C-{example_id}",
        model="stub",
        contract_excerpt=excerpt,
        gold_present=gold_present,
        gold_spans=gold_spans or ["Assignment requires consent"],
        pred_present=pred_present,
        pred_span=pred_span,
        confidence=confidence,
        reasoning=reasoning,
        has_api_error=api_error,
        has_parse_error=parse_error,
        parse_error="bad json" if parse_error else None,
        api_error="timeout" if api_error else None,
        raw_text=None,
    )


def test_classify_missed_present() -> None:
    err = classify_error(
        _row("fn", gold_present=True, pred_present=False, confidence=0.85)
    )
    assert err is not None
    assert err.error_type == ErrorType.MISSED_PRESENT


def test_classify_false_present() -> None:
    err = classify_error(
        _row("fp", gold_present=False, pred_present=True, pred_span="x", confidence=0.9)
    )
    assert err is not None
    assert err.error_type == ErrorType.FALSE_PRESENT


def test_classify_hallucinated_span() -> None:
    err = classify_error(
        _row(
            "hall",
            pred_span="fabricated clause not in text",
            confidence=0.88,
        )
    )
    assert err is not None
    assert err.error_type == ErrorType.HALLUCINATED_SPAN


def test_classify_wrong_span() -> None:
    err = classify_error(
        _row(
            "wrong",
            pred_span="requires consent",
            gold_spans=["Assignment requires consent"],
            confidence=0.7,
        )
    )
    assert err is not None
    assert err.error_type == ErrorType.CORRECT_PRESENT_WRONG_SPAN


def test_classify_parse_fail() -> None:
    err = classify_error(_row("parse", parse_error=True, pred_present=None))
    assert err is not None
    assert err.error_type == ErrorType.PARSE_FAIL


def test_correct_prediction_not_error() -> None:
    assert classify_error(_row("ok")) is None


def test_count_by_category_and_bucket() -> None:
    errors = classify_model_errors(
        [
            _row("fn1", gold_present=True, pred_present=False, category="Audit Rights"),
            _row("fn2", gold_present=True, pred_present=False, category="Audit Rights"),
            _row("fp1", gold_present=False, pred_present=True, pred_span="x"),
        ]
    )
    counts = count_by_category_and_bucket(errors)
    assert counts[ErrorType.MISSED_PRESENT.value]["Audit Rights"] == 2
    assert counts[ErrorType.FALSE_PRESENT.value]["Anti-Assignment"] == 1


def test_render_and_write_report(tmp_path: Path) -> None:
    errors = classify_model_errors(
        [
            _row("fn", gold_present=True, pred_present=False, confidence=0.95, reasoning="missed"),
            _row("fp", gold_present=False, pred_present=True, pred_span="wrong bit", confidence=0.92),
            _row("hall", pred_span="not in contract at all", confidence=0.99),
            _row("wrong", pred_span="requires consent", gold_spans=["Assignment requires consent"]),
            _row("parse", parse_error=True, pred_present=None),
        ]
    )
    md = render_error_report("stub", errors, worst_per_bucket=2)
    assert "missed_present" in md
    assert "false_present" in md
    assert "hallucinated_span" in md
    assert "correct_present_wrong_span" in md
    assert "parse_fail" in md
    assert "**Reasoning:**" in md

    path = write_error_report("stub", errors, output_dir=tmp_path, worst_per_bucket=2)
    assert path.exists()
    assert path.name == "stub.md"
