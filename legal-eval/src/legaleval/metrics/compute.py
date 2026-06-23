"""Join raw run logs with gold labels and compute all metric dimensions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from legaleval.data.cuad import EvalExample, read_eval_set_jsonl
from legaleval.metrics.presence import presence_metrics
from legaleval.metrics.span import span_grounding_metrics
from legaleval.paths import (
    project_root,
    run_metrics_path,
    run_raw_dir,
)
from legaleval.models.runner import CallLogRow

DEFAULT_BOOTSTRAP_N = 1000


@dataclass(frozen=True)
class JoinedRow:
    example_id: str
    category: str
    model: str
    gold_present: bool
    gold_spans: list[str]
    contract_excerpt: str
    pred_present: bool | None
    pred_span: str | None
    has_api_error: bool
    has_parse_error: bool


def raw_results_dir(run_id: str) -> Path:
    return run_raw_dir(run_id)


def metrics_output_path(run_id: str) -> Path:
    return run_metrics_path(run_id)


def load_call_log_rows(path: Path) -> list[CallLogRow]:
    rows: list[CallLogRow] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(CallLogRow.model_validate_json(line))
    return rows


def load_raw_run(run_id: str) -> dict[str, list[CallLogRow]]:
    run_dir = raw_results_dir(run_id)
    if not run_dir.exists():
        raise FileNotFoundError(f"Raw results not found: {run_dir}")
    results: dict[str, list[CallLogRow]] = {}
    for path in sorted(run_dir.glob("*.jsonl")):
        results[path.stem] = load_call_log_rows(path)
    if not results:
        raise FileNotFoundError(f"No model jsonl files in {run_dir}")
    return results


def join_row(log: CallLogRow, gold: EvalExample) -> JoinedRow:
    has_api_error = log.error is not None
    has_parse_error = log.parse_error is not None and not has_api_error
    pred_present: bool | None = None
    pred_span: str | None = None
    if log.parsed is not None and not has_api_error and not has_parse_error:
        pred_present = bool(log.parsed.get("present"))
        pred_span = log.parsed.get("span")
    return JoinedRow(
        example_id=log.example_id,
        category=log.category,
        model=log.model,
        gold_present=gold.present,
        gold_spans=list(gold.gold_spans),
        contract_excerpt=gold.contract_excerpt,
        pred_present=pred_present,
        pred_span=pred_span,
        has_api_error=has_api_error,
        has_parse_error=has_parse_error,
    )


def join_run_with_gold(
    raw_by_model: dict[str, list[CallLogRow]],
    gold_by_id: dict[str, EvalExample],
) -> dict[str, list[JoinedRow]]:
    joined: dict[str, list[JoinedRow]] = {}
    for model_name, logs in raw_by_model.items():
        rows: list[JoinedRow] = []
        for log in logs:
            gold = gold_by_id.get(log.example_id)
            if gold is None:
                raise KeyError(f"Missing gold example for id={log.example_id!r}")
            rows.append(join_row(log, gold))
        joined[model_name] = rows
    return joined


def reliability_metrics(rows: list[JoinedRow]) -> dict[str, Any]:
    total = len(rows)
    api_errors = sum(1 for row in rows if row.has_api_error)
    parse_errors = sum(1 for row in rows if row.has_parse_error)
    scored = sum(1 for row in rows if row.pred_present is not None)
    return {
        "total": total,
        "api_errors": api_errors,
        "parse_errors": parse_errors,
        "scored": scored,
        "api_error_rate": round(api_errors / total, 6) if total else 0.0,
        "parse_error_rate": round(parse_errors / total, 6) if total else 0.0,
        "combined_error_rate": round((api_errors + parse_errors) / total, 6) if total else 0.0,
    }


def _presence_rows(rows: list[JoinedRow]) -> list[JoinedRow]:
    return [row for row in rows if row.pred_present is not None]


def _tp_presence_rows(rows: list[JoinedRow]) -> list[JoinedRow]:
    return [
        row
        for row in rows
        if row.pred_present is True and row.gold_present is True and row.pred_span
    ]


def compute_model_metrics(
    rows: list[JoinedRow],
    *,
    n_bootstrap: int = DEFAULT_BOOTSTRAP_N,
    seed: int = 42,
) -> dict[str, Any]:
    scored = _presence_rows(rows)
    gold = [row.gold_present for row in scored]
    pred = [bool(row.pred_present) for row in scored]

    presence_overall = presence_metrics(
        gold, pred, n_bootstrap=n_bootstrap, seed=seed
    )
    presence_overall["n_excluded"] = len(rows) - len(scored)

    by_category: dict[str, Any] = {}
    categories = sorted({row.category for row in scored})
    for category in categories:
        cat_rows = [row for row in scored if row.category == category]
        by_category[category] = presence_metrics(
            [row.gold_present for row in cat_rows],
            [bool(row.pred_present) for row in cat_rows],
            n_bootstrap=n_bootstrap,
            seed=seed,
        )

    tp_rows = _tp_presence_rows(scored)
    span_overall = span_grounding_metrics(
        predicted_spans=[row.pred_span for row in tp_rows],  # type: ignore[misc]
        gold_spans_list=[row.gold_spans for row in tp_rows],
        contract_excerpts=[row.contract_excerpt for row in tp_rows],
        n_bootstrap=n_bootstrap,
        seed=seed,
    )

    span_by_category: dict[str, Any] = {}
    for category in categories:
        cat_tp = [row for row in tp_rows if row.category == category]
        if not cat_tp:
            span_by_category[category] = span_grounding_metrics(
                predicted_spans=[],
                gold_spans_list=[],
                contract_excerpts=[],
                n_bootstrap=n_bootstrap,
                seed=seed,
            )
            continue
        span_by_category[category] = span_grounding_metrics(
            predicted_spans=[row.pred_span for row in cat_tp],  # type: ignore[misc]
            gold_spans_list=[row.gold_spans for row in cat_tp],
            contract_excerpts=[row.contract_excerpt for row in cat_tp],
            n_bootstrap=n_bootstrap,
            seed=seed,
        )

    return {
        "presence": {
            "overall": presence_overall,
            "by_category": by_category,
        },
        "span_grounding": {
            "overall": span_overall,
            "by_category": span_by_category,
        },
        "reliability": reliability_metrics(rows),
    }


def compute_run_metrics(
    run_id: str,
    eval_set_path: Path,
    *,
    n_bootstrap: int = DEFAULT_BOOTSTRAP_N,
    seed: int = 42,
) -> dict[str, Any]:
    gold_examples = read_eval_set_jsonl(eval_set_path)
    gold_by_id = {example.id: example for example in gold_examples}
    raw_by_model = load_raw_run(run_id)
    joined = join_run_with_gold(raw_by_model, gold_by_id)

    return {
        "run_id": run_id,
        "eval_set": str(eval_set_path),
        "n_bootstrap": n_bootstrap,
        "models": {
            model: compute_model_metrics(
                rows, n_bootstrap=n_bootstrap, seed=seed
            )
            for model, rows in sorted(joined.items())
        },
    }


def write_metrics_json(metrics: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
        handle.write("\n")
    return output_path


def metrics_to_summary_table(metrics: dict[str, Any]) -> pd.DataFrame:
    """Build a tidy pandas summary — one row per model x category x dimension."""
    records: list[dict[str, Any]] = []

    for model, model_metrics in metrics["models"].items():
        records.append(_summary_record(model, "overall", "presence", model_metrics))
        records.append(
            _summary_record(model, "overall", "span_grounding", model_metrics)
        )
        records.append(
            _summary_record(model, "overall", "reliability", model_metrics)
        )

        for category in model_metrics["presence"]["by_category"]:
            records.append(
                _category_presence_record(model, category, model_metrics)
            )
            records.append(
                _category_span_record(model, category, model_metrics)
            )

    return pd.DataFrame(records)


def _summary_record(
    model: str, scope: str, dimension: str, model_metrics: dict[str, Any]
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "model": model,
        "scope": scope,
        "dimension": dimension,
    }
    if dimension == "presence":
        overall = model_metrics["presence"]["overall"]
        record.update(
            {
                "precision": overall["precision"],
                "recall": overall["recall"],
                "f1": overall["f1"],
                "f1_ci_low": _ci_low(overall.get("f1_ci_95")),
                "f1_ci_high": _ci_high(overall.get("f1_ci_95")),
                "tp": overall["confusion_matrix"]["tp"],
                "fp": overall["confusion_matrix"]["fp"],
                "fn": overall["confusion_matrix"]["fn"],
                "tn": overall["confusion_matrix"]["tn"],
                "n": overall["n"],
                "n_excluded": overall.get("n_excluded"),
            }
        )
    elif dimension == "span_grounding":
        overall = model_metrics["span_grounding"]["overall"]
        record.update(
            {
                "n_tp_presence": overall["n_tp_presence"],
                "hallucination_rate": overall["hallucination_rate"],
                "substring_grounded_rate": overall["substring_grounded_rate"],
                "mean_jaccard": overall["mean_jaccard"],
                "jaccard_ci_low": _ci_low(overall.get("mean_jaccard_ci_95")),
                "jaccard_ci_high": _ci_high(overall.get("mean_jaccard_ci_95")),
                "jaccard_median": overall["jaccard_distribution"]["median"],
            }
        )
    elif dimension == "reliability":
        rel = model_metrics["reliability"]
        record.update(
            {
                "total": rel["total"],
                "api_error_rate": rel["api_error_rate"],
                "parse_error_rate": rel["parse_error_rate"],
                "combined_error_rate": rel["combined_error_rate"],
                "scored": rel["scored"],
            }
        )
    return record


def _category_presence_record(
    model: str, category: str, model_metrics: dict[str, Any]
) -> dict[str, Any]:
    cat = model_metrics["presence"]["by_category"][category]
    return {
        "model": model,
        "scope": category,
        "dimension": "presence",
        "precision": cat["precision"],
        "recall": cat["recall"],
        "f1": cat["f1"],
        "f1_ci_low": _ci_low(cat.get("f1_ci_95")),
        "f1_ci_high": _ci_high(cat.get("f1_ci_95")),
        "tp": cat["confusion_matrix"]["tp"],
        "fp": cat["confusion_matrix"]["fp"],
        "fn": cat["confusion_matrix"]["fn"],
        "tn": cat["confusion_matrix"]["tn"],
        "n": cat["n"],
    }


def _category_span_record(
    model: str, category: str, model_metrics: dict[str, Any]
) -> dict[str, Any]:
    cat = model_metrics["span_grounding"]["by_category"][category]
    return {
        "model": model,
        "scope": category,
        "dimension": "span_grounding",
        "n_tp_presence": cat["n_tp_presence"],
        "hallucination_rate": cat["hallucination_rate"],
        "substring_grounded_rate": cat["substring_grounded_rate"],
        "mean_jaccard": cat["mean_jaccard"],
        "jaccard_ci_low": _ci_low(cat.get("mean_jaccard_ci_95")),
        "jaccard_ci_high": _ci_high(cat.get("mean_jaccard_ci_95")),
        "jaccard_median": cat["jaccard_distribution"]["median"],
    }


def _ci_low(ci: dict[str, float] | None) -> float | None:
    return ci["low"] if ci else None


def _ci_high(ci: dict[str, float] | None) -> float | None:
    return ci["high"] if ci else None


def run_metrics(
    run_id: str,
    eval_set_path: Path,
    *,
    n_bootstrap: int = DEFAULT_BOOTSTRAP_N,
    seed: int = 42,
    print_summary: bool = True,
) -> tuple[dict[str, Any], Path]:
    metrics = compute_run_metrics(
        run_id,
        eval_set_path,
        n_bootstrap=n_bootstrap,
        seed=seed,
    )
    output_path = write_metrics_json(metrics, metrics_output_path(run_id))
    if print_summary:
        table = metrics_to_summary_table(metrics)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)
        print(table.to_string(index=False))
    return metrics, output_path
