"""Generate the deliverable REPORT.md from pipeline JSON outputs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from legaleval.data.cuad import EvalExample, read_eval_set_jsonl
from legaleval.judge.validate import MIN_KAPPA
from legaleval.paths import (
    run_calibration_ece_path,
    run_errors_summary_path,
    run_judge_validation_path,
    run_manifest_path,
    run_metrics_path,
    run_report_path,
)
from legaleval.report.errors import ClassifiedError, ErrorType, classify_model_errors
from legaleval.report.records import enrich_run
from legaleval.metrics.compute import load_raw_run


def eval_set_stats(examples: list[EvalExample]) -> dict[str, Any]:
    by_category: dict[str, Counter[bool]] = {}
    for example in examples:
        by_category.setdefault(example.category, Counter())[example.present] += 1

    categories = sorted(by_category)
    return {
        "n_examples": len(examples),
        "n_categories": len(categories),
        "categories": categories,
        "present": sum(1 for example in examples if example.present),
        "absent": sum(1 for example in examples if not example.present),
        "by_category": {
            category: {
                "present": counts[True],
                "absent": counts[False],
                "total": counts[True] + counts[False],
            }
            for category, counts in sorted(by_category.items())
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_ci(low: float | None, high: float | None) -> str:
    if low is None or high is None:
        return "n/a"
    return f"[{low:.3f}, {high:.3f}]"


def _pick_failure_examples(
    errors: list[ClassifiedError], limit: int = 3
) -> list[ClassifiedError]:
    if not errors:
        return []
    by_bucket: dict[ErrorType, list[ClassifiedError]] = {}
    for err in errors:
        by_bucket.setdefault(err.error_type, []).append(err)
    picked: list[ClassifiedError] = []
    for bucket in ErrorType:
        bucket_errors = by_bucket.get(bucket, [])
        if not bucket_errors:
            continue
        worst = max(bucket_errors, key=lambda err: err.severity)
        picked.append(worst)
        if len(picked) >= limit:
            break
    return picked[:limit]


def _format_failure_example(err: ClassifiedError) -> list[str]:
    row = err.row
    lines = [
        f"**{err.error_type.value}** — `{row.example_id}` ({row.category})",
        f"- Gold present: {row.gold_present}; predicted present: {row.pred_present}",
        f"- Predicted span: {row.pred_span!r}",
        f"- Confidence: {row.confidence}",
    ]
    if row.reasoning:
        lines.append(f"- Reasoning: {row.reasoning}")
    excerpt = row.contract_excerpt
    if len(excerpt) > 280:
        excerpt = excerpt[:277] + "..."
    lines.append(f"- Excerpt: _{excerpt}_")
    return lines


def generate_report(
    run_id: str,
    *,
    eval_set_path: Path,
) -> str:
    manifest = _load_json(run_manifest_path(run_id))
    metrics = _load_json(run_metrics_path(run_id))
    validation = _load_json(run_judge_validation_path(run_id))
    calibration = _load_json(run_calibration_ece_path(run_id))
    errors_summary = _load_json(run_errors_summary_path(run_id))

    examples = read_eval_set_jsonl(eval_set_path)
    stats = eval_set_stats(examples)

    agreement = validation["agreement"]
    kappa = agreement.get("cohens_kappa")
    kappa_pass = agreement.get("passes_threshold", False)

    lines: list[str] = [
        "# Legal-Eval Report",
        "",
        f"**Run ID:** `{run_id}`  ",
        f"**Run date (UTC):** {manifest['run_date_utc']}  ",
        f"**Eval set SHA-256:** `{manifest['eval_set']['sha256'][:16]}…`",
        "",
        "## Judge validation",
        "",
    ]

    if kappa is None:
        lines.append(
            "_Judge validation did not produce a kappa score (all calls failed)._"
        )
    else:
        status = "PASSED" if kappa_pass else "**FAILED**"
        lines.extend(
            [
                f"- **Status:** {status} (κ ≥ {MIN_KAPPA} required)",
                f"- **Cohen's κ:** {kappa:.4f}",
                f"- **Accuracy vs CUAD reference:** {agreement.get('accuracy')}",
                f"- **Sample size:** {agreement.get('n_scored')} scored / "
                f"{validation.get('sample_size', 'n/a')} sampled",
                "",
                (
                    "_Judge decisions are trustworthy for borderline span adjudication._"
                    if kappa_pass
                    else "_**Do not trust judge-mediated span scores** until κ ≥ "
                    f"{MIN_KAPPA}._"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "## Task & dataset",
            "",
            "Models read a contract excerpt and return structured JSON: "
            "`present`, `span`, `confidence`, `reasoning`. "
            "Gold labels come from **CUAD v1** (Atticus Project) — "
            "41 legal clause categories, lawyer-review annotations.",
            "",
            f"- **Eval examples:** {stats['n_examples']}",
            f"- **Categories in eval set:** {stats['n_categories']}",
            f"- **Present / absent balance:** {stats['present']} present, "
            f"{stats['absent']} absent "
            f"({stats['present'] / stats['n_examples']:.0%} / "
            f"{stats['absent'] / stats['n_examples']:.0%})",
            "",
            "| Category | Present | Absent |",
            "|----------|---------|--------|",
        ]
    )

    for category, counts in stats["by_category"].items():
        lines.append(
            f"| {category} | {counts['present']} | {counts['absent']} |"
        )

    lines.extend(
        [
            "",
            "## Per-model results",
            "",
            "| Model | Presence F1 (95% CI) | Mean span Jaccard (95% CI) | "
            "Hallucination rate | Parse error rate | ECE |",
            "|-------|--------------------|-----------------------------|"
            "|---------------------|------------------|-----|",
        ]
    )

    for model, model_metrics in sorted(metrics["models"].items()):
        presence = model_metrics["presence"]["overall"]
        span = model_metrics["span_grounding"]["overall"]
        reliability = model_metrics["reliability"]
        cal = calibration["models"].get(model, {})
        f1_ci = _fmt_ci(
            (presence.get("f1_ci_95") or {}).get("low"),
            (presence.get("f1_ci_95") or {}).get("high"),
        )
        jaccard_ci = _fmt_ci(
            (span.get("mean_jaccard_ci_95") or {}).get("low"),
            (span.get("mean_jaccard_ci_95") or {}).get("high"),
        )
        parse_rate = reliability.get("combined_error_rate", 0.0)
        lines.append(
            f"| {model} | {presence['f1']:.3f} {f1_ci} | "
            f"{span['mean_jaccard']:.3f} {jaccard_ci} | "
            f"{span['hallucination_rate']:.3f} | {parse_rate:.3f} | "
            f"{cal.get('ece', 'n/a')} |"
        )

    lines.extend(["", "## Failure taxonomy", ""])

    for model, summary in sorted(errors_summary["models"].items()):
        lines.append(f"### {model}")
        lines.append("")
        lines.append("| Bucket | Count |")
        lines.append("|--------|-------|")
        for bucket, count in sorted(summary["counts_by_bucket"].items()):
            lines.append(f"| {bucket} | {count} |")
        lines.append("")

    lines.extend(["", "### Concrete failure examples", ""])

    raw_by_model = load_raw_run(run_id)
    gold_by_id = {example.id: example for example in examples}
    enriched = enrich_run(raw_by_model, gold_by_id)
    example_models = list(enriched.keys())[:2]
    shown = 0
    for model in example_models:
        errors = classify_model_errors(enriched[model])
        for err in _pick_failure_examples(errors, limit=3):
            lines.extend(_format_failure_example(err))
            lines.append("")
            shown += 1
            if shown >= 3:
                break
        if shown >= 3:
            break

    if shown == 0:
        lines.append("_No failure examples available for this run._")
        lines.append("")

    lines.extend(
        [
            "## Findings",
            "",
            "_Write three true statements about model behavior observed in this run. "
            "Go beyond the numbers — describe systematic failure modes, category-specific "
            "weaknesses, or calibration patterns._",
            "",
            "1. **Statement 1:** ",
            "   > _e.g. Model X systematically misses `Anti-Assignment` clauses when "
            "they appear only as a cross-reference…_",
            "",
            "2. **Statement 2:** ",
            "   > _e.g. High-confidence false positives cluster in categories with "
            "overlapping legal language…_",
            "",
            "3. **Statement 3:** ",
            "   > _e.g. Span hallucination rate increases on excerpts >6k chars, "
            "suggesting context truncation effects…_",
            "",
            "## Reproducibility",
            "",
            f"- Full manifest: `results/{run_id}/manifest.json`",
            f"- Pinned models: see `models_yaml.pinned` in manifest",
            f"- Seeds: `{json.dumps(manifest['seeds'])}`",
            "",
        ]
    )

    return "\n".join(lines)


def write_report(
    run_id: str,
    *,
    eval_set_path: Path,
    output_path: Path | None = None,
) -> Path:
    content = generate_report(run_id, eval_set_path=eval_set_path)
    path = output_path or run_report_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
