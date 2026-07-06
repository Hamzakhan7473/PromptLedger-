"""Failure taxonomy and human-readable error reports."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from legaleval.data.schema import read_eval_set_jsonl
from legaleval.metrics.compute import load_raw_run
from legaleval.metrics.span import best_gold_jaccard, span_in_contract
from legaleval.paths import project_root, run_errors_dir
from legaleval.report.records import EnrichedRow, enrich_run

SPAN_MATCH_THRESHOLD = 0.7
WORST_PER_BUCKET = 10


class ErrorType(str, Enum):
    MISSED_PRESENT = "missed_present"
    FALSE_PRESENT = "false_present"
    CORRECT_PRESENT_WRONG_SPAN = "correct_present_wrong_span"
    HALLUCINATED_SPAN = "hallucinated_span"
    PARSE_FAIL = "parse_fail"


@dataclass(frozen=True)
class ClassifiedError:
    row: EnrichedRow
    error_type: ErrorType
    severity: float
    token_jaccard: float | None = None


def classify_error(row: EnrichedRow) -> ClassifiedError | None:
    """Assign each failure to exactly one error bucket, or None if correct."""
    if row.has_api_error or row.has_parse_error:
        return ClassifiedError(row=row, error_type=ErrorType.PARSE_FAIL, severity=0.0)

    if row.pred_present is None:
        return ClassifiedError(
            row=row,
            error_type=ErrorType.PARSE_FAIL,
            severity=0.0,
        )

    if row.gold_present and row.pred_present is False:
        conf = row.confidence if row.confidence is not None else 0.0
        return ClassifiedError(
            row=row,
            error_type=ErrorType.MISSED_PRESENT,
            severity=conf,
        )

    if not row.gold_present and row.pred_present is True:
        conf = row.confidence if row.confidence is not None else 0.0
        return ClassifiedError(
            row=row,
            error_type=ErrorType.FALSE_PRESENT,
            severity=conf,
        )

    if row.pred_present and row.pred_span:
        if not span_in_contract(row.pred_span, row.contract_excerpt):
            conf = row.confidence if row.confidence is not None else 0.0
            return ClassifiedError(
                row=row,
                error_type=ErrorType.HALLUCINATED_SPAN,
                severity=conf,
            )

        if row.gold_present:
            jaccard = best_gold_jaccard(row.pred_span, row.gold_spans)
            if jaccard < SPAN_MATCH_THRESHOLD:
                return ClassifiedError(
                    row=row,
                    error_type=ErrorType.CORRECT_PRESENT_WRONG_SPAN,
                    severity=1.0 - jaccard,
                    token_jaccard=jaccard,
                )

    return None


def _worst_examples(errors: list[ClassifiedError], limit: int = WORST_PER_BUCKET) -> list[ClassifiedError]:
    return sorted(errors, key=lambda err: (-err.severity, err.row.example_id))[:limit]


def count_by_category_and_bucket(
    errors: list[ClassifiedError],
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for err in errors:
        counts[err.error_type.value][err.row.category] += 1
    return {bucket: dict(cats) for bucket, cats in counts.items()}


def errors_output_dir(run_id: str | None = None) -> Path:
    if run_id is None:
        return project_root() / "results" / "errors"
    return run_errors_dir(run_id)


def _truncate(text: str, limit: int = 600) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _format_example(err: ClassifiedError, rank: int) -> str:
    row = err.row
    lines = [
        f"### {rank}. `{row.example_id}` — {row.category}",
        "",
        f"**Contract:** {row.contract_title}",
        "",
        "**Excerpt:**",
        "```",
        _truncate(row.contract_excerpt),
        "```",
        "",
        f"**Gold:** present={row.gold_present}",
    ]
    if row.gold_spans:
        lines.append(f"  - spans: {row.gold_spans!r}")
    lines.append("")
    lines.append(
        f"**Prediction:** present={row.pred_present}, "
        f"span={row.pred_span!r}, confidence={row.confidence}"
    )
    if err.token_jaccard is not None:
        lines.append(f"  - token Jaccard vs gold: {err.token_jaccard:.4f}")
    if row.reasoning:
        lines.append("")
        lines.append(f"**Reasoning:** {row.reasoning}")
    if row.parse_error:
        lines.append("")
        lines.append(f"**Parse error:** {row.parse_error}")
    if row.api_error:
        lines.append("")
        lines.append(f"**API error:** {row.api_error}")
    lines.append("")
    return "\n".join(lines)


def render_error_report(
    model: str,
    errors: list[ClassifiedError],
    *,
    worst_per_bucket: int = WORST_PER_BUCKET,
) -> str:
    counts = count_by_category_and_bucket(errors)
    by_bucket: dict[ErrorType, list[ClassifiedError]] = defaultdict(list)
    for err in errors:
        by_bucket[err.error_type].append(err)

    lines = [
        f"# Error report — `{model}`",
        "",
        "## Summary (counts per bucket per category)",
        "",
        "| Bucket | Category | Count |",
        "|--------|----------|-------|",
    ]

    for bucket in ErrorType:
        bucket_counts = counts.get(bucket.value, {})
        if not bucket_counts:
            lines.append(f"| {bucket.value} | _none_ | 0 |")
            continue
        for category, count in sorted(bucket_counts.items()):
            lines.append(f"| {bucket.value} | {category} | {count} |")

    lines.append("")

    for bucket in ErrorType:
        bucket_errors = by_bucket.get(bucket, [])
        total = len(bucket_errors)
        lines.extend(
            [
                f"## {bucket.value} ({total} total)",
                "",
            ]
        )
        if not bucket_errors:
            lines.append("_No errors in this bucket._")
            lines.append("")
            continue

        worst = _worst_examples(bucket_errors, limit=worst_per_bucket)
        lines.append(f"### Worst {len(worst)} examples")
        lines.append("")
        for rank, err in enumerate(worst, start=1):
            lines.append(_format_example(err, rank))

    return "\n".join(lines)


def write_error_report(
    model: str,
    errors: list[ClassifiedError],
    output_dir: Path | None = None,
    *,
    worst_per_bucket: int = WORST_PER_BUCKET,
) -> Path:
    out_dir = output_dir or errors_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{model}.md"
    path.write_text(
        render_error_report(model, errors, worst_per_bucket=worst_per_bucket),
        encoding="utf-8",
    )
    return path


def classify_model_errors(rows: list[EnrichedRow]) -> list[ClassifiedError]:
    errors: list[ClassifiedError] = []
    for row in rows:
        classified = classify_error(row)
        if classified is not None:
            errors.append(classified)
    return errors


def run_error_reports(
    run_id: str,
    eval_set_path: Path,
    *,
    output_dir: Path | None = None,
    worst_per_bucket: int = WORST_PER_BUCKET,
) -> dict[str, Any]:
    gold_examples = read_eval_set_jsonl(eval_set_path)
    gold_by_id = {example.id: example for example in gold_examples}
    raw_by_model = load_raw_run(run_id)
    enriched = enrich_run(raw_by_model, gold_by_id)

    out_dir = output_dir or errors_output_dir(run_id)
    reports: dict[str, Any] = {}
    for model, rows in sorted(enriched.items()):
        errors = classify_model_errors(rows)
        report_path = write_error_report(
            model,
            errors,
            output_dir=out_dir,
            worst_per_bucket=worst_per_bucket,
        )
        reports[model] = {
            "report_path": str(report_path),
            "total_errors": len(errors),
            "counts_by_bucket": {
                bucket.value: sum(
                    1 for err in errors if err.error_type == bucket
                )
                for bucket in ErrorType
            },
            "counts_by_category": count_by_category_and_bucket(errors),
        }
    return {
        "run_id": run_id,
        "eval_set": str(eval_set_path),
        "models": reports,
    }
