"""Tests for eval metrics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legaleval.data.schema import EvalExample
from legaleval.metrics.bootstrap import bootstrap_f1_ci, bootstrap_percentile_ci
from legaleval.metrics.compute import (
    JoinedRow,
    compute_model_metrics,
    compute_run_metrics,
    join_run_with_gold,
    metrics_to_summary_table,
    write_metrics_json,
)
from legaleval.metrics.presence import confusion_counts, precision_recall_f1
from legaleval.metrics.span import (
    best_gold_jaccard,
    span_grounding_metrics,
    span_in_contract,
    token_jaccard,
)
from legaleval.models.runner import CallLogRow


def _example(
    example_id: str,
    *,
    present: bool,
    excerpt: str,
    gold_spans: list[str] | None = None,
    category: str = "Anti-Assignment",
) -> EvalExample:
    return EvalExample(
        id=example_id,
        contract_excerpt=excerpt,
        category=category,
        present=present,
        gold_spans=gold_spans or [],
        contract_title=f"Contract-{example_id}",
    )


def _log(
    example_id: str,
    *,
    category: str = "Anti-Assignment",
    parsed: dict | None = None,
    parse_error: str | None = None,
    error: str | None = None,
) -> CallLogRow:
    return CallLogRow(
        run_id="test-run",
        example_id=example_id,
        category=category,
        contract_title=f"Contract-{example_id}",
        provider="stub",
        model="stub-model",
        model_id="stub",
        parsed=parsed,
        parse_error=parse_error,
        error=error,
    )


def test_confusion_counts_tp_fp_fn_tn() -> None:
    gold = [True, True, False, False]
    pred = [True, False, True, False]
    counts = confusion_counts(gold, pred)
    assert counts == {"tp": 1, "fp": 1, "fn": 1, "tn": 1}


def test_precision_recall_f1() -> None:
    scores = precision_recall_f1([True, True, False], [True, False, False])
    assert scores["precision"] == 1.0
    assert scores["recall"] == 0.5
    assert scores["f1"] == pytest.approx(2 / 3)


def test_token_jaccard_and_substring() -> None:
    assert token_jaccard("assignment requires consent", "Assignment requires consent.") > 0.5
    assert span_in_contract("requires consent", "Assignment requires consent.")
    assert not span_in_contract("totally fabricated clause", "Assignment requires consent.")


def test_best_gold_jaccard_picks_max() -> None:
    score = best_gold_jaccard(
        "requires consent",
        ["unrelated text", "Assignment requires consent"],
    )
    assert score > 0.5


def test_span_grounding_hallucination() -> None:
    excerpt = "Assignment requires consent."
    metrics = span_grounding_metrics(
        predicted_spans=["fabricated clause", "requires consent"],
        gold_spans_list=[["Assignment requires consent"], ["Assignment requires consent"]],
        contract_excerpts=[excerpt, excerpt],
        n_bootstrap=100,
        seed=1,
    )
    assert metrics["n_tp_presence"] == 2
    assert metrics["hallucination_count"] == 1
    assert metrics["hallucination_rate"] == 0.5
    assert metrics["mean_jaccard"] > 0.0
    assert "mean_jaccard_ci_95" in metrics


def test_bootstrap_f1_ci_is_ordered() -> None:
    gold = [True, True, False, False, True, False]
    pred = [True, False, True, False, True, False]
    ci = bootstrap_f1_ci(gold, pred, n_bootstrap=200, seed=0)
    assert ci is not None
    assert ci[0] <= ci[1]


def test_bootstrap_percentile_ci() -> None:
    ci = bootstrap_percentile_ci([0.2, 0.4, 0.6, 0.8], n_bootstrap=200, seed=0)
    assert ci is not None
    assert ci[0] <= 0.5 <= ci[1]


@pytest.fixture
def synthetic_joined_rows() -> list[JoinedRow]:
    """TP, FP, FN, TN, hallucinated span, parse fail, API error."""
    return [
        JoinedRow(
            example_id="tp-good",
            category="Anti-Assignment",
            model="stub-model",
            gold_present=True,
            gold_spans=["Assignment requires consent"],
            contract_excerpt="Assignment requires consent.",
            pred_present=True,
            pred_span="Assignment requires consent",
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="tp-hallucinated",
            category="Anti-Assignment",
            model="stub-model",
            gold_present=True,
            gold_spans=["Assignment requires consent"],
            contract_excerpt="Assignment requires consent.",
            pred_present=True,
            pred_span="invented clause text",
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="fp",
            category="Cap On Liability",
            model="stub-model",
            gold_present=False,
            gold_spans=[],
            contract_excerpt="No liability language here.",
            pred_present=True,
            pred_span="liability cap",
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="fn",
            category="Audit Rights",
            model="stub-model",
            gold_present=True,
            gold_spans=["annual audit"],
            contract_excerpt="Audits may occur annually.",
            pred_present=False,
            pred_span=None,
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="tn",
            category="Audit Rights",
            model="stub-model",
            gold_present=False,
            gold_spans=[],
            contract_excerpt="No audit language.",
            pred_present=False,
            pred_span=None,
            has_api_error=False,
            has_parse_error=False,
        ),
        JoinedRow(
            example_id="parse-fail",
            category="Audit Rights",
            model="stub-model",
            gold_present=True,
            gold_spans=["annual audit"],
            contract_excerpt="Audits may occur annually.",
            pred_present=None,
            pred_span=None,
            has_api_error=False,
            has_parse_error=True,
        ),
        JoinedRow(
            example_id="api-error",
            category="Audit Rights",
            model="stub-model",
            gold_present=False,
            gold_spans=[],
            contract_excerpt="No audit language.",
            pred_present=None,
            pred_span=None,
            has_api_error=True,
            has_parse_error=False,
        ),
    ]


def test_compute_model_metrics_dimensions_separate(
    synthetic_joined_rows: list[JoinedRow],
) -> None:
    metrics = compute_model_metrics(
        synthetic_joined_rows, n_bootstrap=200, seed=0
    )

    presence = metrics["presence"]["overall"]
    assert presence["confusion_matrix"] == {"tp": 2, "fp": 1, "fn": 1, "tn": 1}
    assert presence["n"] == 5
    assert presence["n_excluded"] == 2
    assert "f1_ci_95" in presence

    span = metrics["span_grounding"]["overall"]
    assert span["n_tp_presence"] == 2
    assert span["hallucination_count"] == 1
    assert span["hallucination_rate"] == 0.5
    assert span["jaccard_distribution"]["n"] == 2
    assert "mean_jaccard_ci_95" in span

    reliability = metrics["reliability"]
    assert reliability["total"] == 7
    assert reliability["api_errors"] == 1
    assert reliability["parse_errors"] == 1
    assert reliability["combined_error_rate"] == pytest.approx(2 / 7)


def test_metrics_summary_table_has_separate_rows(
    synthetic_joined_rows: list[JoinedRow],
) -> None:
    model_metrics = compute_model_metrics(synthetic_joined_rows, n_bootstrap=100)
    payload = {
        "run_id": "test",
        "eval_set": "eval.jsonl",
        "n_bootstrap": 100,
        "models": {"stub-model": model_metrics},
    }
    table = metrics_to_summary_table(payload)
    dimensions = set(table["dimension"])
    assert dimensions == {"presence", "span_grounding", "reliability"}
    assert "f1" in table.columns
    assert "mean_jaccard" in table.columns
    assert "parse_error_rate" in table.columns


def test_end_to_end_compute_run_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eval_path = tmp_path / "eval_set.jsonl"
    examples = [
        _example("ex-tp", present=True, excerpt="Assignment requires consent.", gold_spans=["Assignment requires consent"]),
        _example("ex-fn", present=True, excerpt="Audits may occur annually.", gold_spans=["annual audit"]),
        _example("ex-tn", present=False, excerpt="No relevant clause."),
    ]
    eval_path.write_text(
        "\n".join(example.model_dump_json() for example in examples) + "\n",
        encoding="utf-8",
    )

    raw_dir = tmp_path / "raw" / "run-e2e"
    raw_dir.mkdir(parents=True)
    logs = [
        _log("ex-tp", parsed={"present": True, "span": "Assignment requires consent", "confidence": 0.9, "reasoning": "ok"}),
        _log("ex-fn", parsed={"present": False, "span": None, "confidence": 0.8, "reasoning": "miss"}),
        _log("ex-tn", parsed={"present": False, "span": None, "confidence": 0.7, "reasoning": "absent"}),
    ]
    raw_path = raw_dir / "stub-model.jsonl"
    raw_path.write_text(
        "\n".join(log.model_dump_json() for log in logs) + "\n",
        encoding="utf-8",
    )

    import legaleval.metrics.compute as compute_mod

    monkeypatch.setattr(compute_mod, "raw_results_dir", lambda run_id: tmp_path / "raw" / run_id)
    monkeypatch.setattr(compute_mod, "metrics_output_path", lambda run_id: tmp_path / "metrics" / f"{run_id}.json")

    metrics = compute_run_metrics("run-e2e", eval_path, n_bootstrap=100, seed=0)
    out = write_metrics_json(metrics, tmp_path / "metrics" / "run-e2e.json")

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["models"]["stub-model"]["presence"]["overall"]["confusion_matrix"]["tp"] == 1
    assert loaded["models"]["stub-model"]["presence"]["overall"]["confusion_matrix"]["fn"] == 1
    assert loaded["models"]["stub-model"]["span_grounding"]["overall"]["n_tp_presence"] == 1


def test_join_run_with_gold() -> None:
    gold = {
        "a": _example("a", present=True, excerpt="text a", gold_spans=["text a"]),
    }
    raw = {"m": [_log("a", parsed={"present": True, "span": "text a", "confidence": 1.0, "reasoning": "x"})]}
    joined = join_run_with_gold(raw, gold)
    assert joined["m"][0].pred_present is True
    assert joined["m"][0].gold_present is True
