"""PDF export for completed eval reports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from legaleval.paths import (
    run_judge_validation_path,
    run_manifest_path,
    run_metrics_path,
    run_report_path,
)


def _ascii_safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pinned_models(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    pinned = manifest.get("models_yaml", {}).get("pinned", {})
    if not isinstance(pinned, dict):
        return []
    models = pinned.get("models", {})
    if not isinstance(models, dict):
        return []
    rows: list[tuple[str, str]] = []
    for name, spec in models.items():
        if isinstance(spec, dict):
            rows.append((str(name), str(spec.get("model_id", "—"))))
    return sorted(rows, key=lambda row: row[0])


def _judge_model_id(manifest: dict[str, Any]) -> str | None:
    pinned = manifest.get("models_yaml", {}).get("pinned", {})
    if not isinstance(pinned, dict):
        return None
    judge = pinned.get("judge")
    if isinstance(judge, dict) and judge.get("model_id"):
        return str(judge["model_id"])
    return None


def _headline_metric_lines(metrics: dict[str, Any], model_names: list[str]) -> list[str]:
    lines: list[str] = []
    models = metrics.get("models", {})
    if not isinstance(models, dict):
        return lines
    for name in model_names:
        entry = models.get(name, {})
        if not isinstance(entry, dict):
            continue
        presence = entry.get("presence", {})
        span = entry.get("span_grounding", {})
        f1 = None
        jaccard = None
        if isinstance(presence, dict):
            overall = presence.get("overall", {})
            if isinstance(overall, dict):
                f1 = overall.get("f1")
        if isinstance(span, dict):
            overall = span.get("overall", {})
            if isinstance(overall, dict):
                jaccard = overall.get("mean_jaccard")
        f1_text = f"{float(f1):.3f}" if isinstance(f1, (int, float)) else "—"
        jaccard_text = f"{float(jaccard):.3f}" if isinstance(jaccard, (int, float)) else "—"
        lines.append(f"{name}: presence F1 {f1_text} · span Jaccard {jaccard_text}")
    return lines


def _pdf_line(pdf: FPDF, text: str, *, size: int = 9, style: str = "") -> None:
    pdf.set_font("Helvetica", style=style, size=size)
    pdf.multi_cell(0, 4.5 if size <= 9 else 6, _ascii_safe(text))
    pdf.ln(1)


def _write_cover_page(
    pdf: FPDF,
    *,
    run_id: str,
    manifest: dict[str, Any],
    metrics: dict[str, Any],
    judge_validation: dict[str, Any] | None,
) -> None:
    eval_set = manifest.get("eval_set", {})
    dataset_path = eval_set.get("path") if isinstance(eval_set, dict) else None
    dataset_sha = eval_set.get("sha256") if isinstance(eval_set, dict) else None
    run_date = str(manifest.get("run_date_utc", "—"))
    seeds = manifest.get("seeds", {})
    model_names = [name for name, _ in _pinned_models(manifest)]
    if not model_names and isinstance(metrics.get("models"), dict):
        model_names = sorted(str(name) for name in metrics["models"])

    _pdf_line(pdf, "Legal AI Evaluation — Shareable Trust Report", size=16, style="B")
    _pdf_line(
        pdf,
        "Evidence for enterprise buyers: reproducible methodology, pinned models, "
        "and headline accuracy metrics from a completed eval run.",
        size=10,
    )
    pdf.ln(2)

    _pdf_line(pdf, "Run summary", size=11, style="B")
    _pdf_line(pdf, f"Run ID: {run_id}")
    _pdf_line(pdf, f"Completed (UTC): {run_date}")
    dataset_label = str(dataset_path or metrics.get("eval_set") or "—")
    _pdf_line(pdf, f"Dataset: {dataset_label}")
    _pdf_line(pdf, f"Dataset SHA-256: {dataset_sha or '—'}")
    pdf.ln(2)

    _pdf_line(pdf, "Headline metrics", size=11, style="B")
    for line in _headline_metric_lines(metrics, model_names):
        _pdf_line(pdf, line)
    agreement = (judge_validation or {}).get("agreement", {})
    kappa = agreement.get("cohens_kappa") if isinstance(agreement, dict) else None
    if isinstance(kappa, (int, float)):
        _pdf_line(pdf, f"Judge agreement (Cohen's kappa): {float(kappa):.3f}")
    pdf.ln(2)

    _pdf_line(pdf, "Reproducibility & provenance", size=11, style="B")
    _pdf_line(
        pdf,
        "Every value below is recorded in manifest.json so a third party can "
        "replay or audit this evaluation.",
    )
    if isinstance(seeds, dict):
        for key in sorted(seeds):
            _pdf_line(pdf, f"Seed ({key}): {seeds[key]}")
    for name, model_id in _pinned_models(manifest):
        _pdf_line(pdf, f"Pinned model {name}: {model_id}")
    judge_id = _judge_model_id(manifest)
    if judge_id:
        _pdf_line(pdf, f"Pinned judge: {judge_id}")
    pdf.ln(2)
    _pdf_line(
        pdf,
        "Detailed per-category metrics, calibration, and failure taxonomy follow on "
        "subsequent pages.",
        size=8,
        style="I",
    )


def report_markdown_to_pdf(
    report_md: str,
    *,
    run_id: str,
    manifest: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    judge_validation: dict[str, Any] | None = None,
) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    if manifest is not None and metrics is not None:
        _write_cover_page(
            pdf,
            run_id=run_id,
            manifest=manifest,
            metrics=metrics,
            judge_validation=judge_validation,
        )
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(0, 8, _ascii_safe("Detailed evaluation report"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
    else:
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(0, 10, _ascii_safe(f"Legal Eval Report — {run_id}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)

    pdf.set_font("Helvetica", size=9)

    for line in report_md.splitlines():
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue
        if stripped.startswith("# "):
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.multi_cell(0, 6, _ascii_safe(stripped[2:]))
            pdf.set_font("Helvetica", size=9)
            continue
        if stripped.startswith("## "):
            pdf.set_font("Helvetica", style="B", size=10)
            pdf.multi_cell(0, 5, _ascii_safe(stripped[3:]))
            pdf.set_font("Helvetica", size=9)
            continue
        plain = re.sub(r"`([^`]+)`", r"\1", stripped)
        plain = re.sub(r"\*\*([^*]+)\*\*", r"\1", plain)
        plain = re.sub(r"\*([^*]+)\*", r"\1", plain)
        pdf.multi_cell(0, 4.5, _ascii_safe(plain))

    return bytes(pdf.output())


def load_run_report_pdf(run_id: str) -> bytes:
    report_path = run_report_path(run_id)
    if not report_path.exists():
        raise FileNotFoundError(f"Report not found for run {run_id}")

    manifest_path = run_manifest_path(run_id)
    metrics_path = run_metrics_path(run_id)
    validation_path = run_judge_validation_path(run_id)

    manifest = _load_json(manifest_path) if manifest_path.exists() else None
    metrics = _load_json(metrics_path) if metrics_path.exists() else None
    judge_validation = _load_json(validation_path) if validation_path.exists() else None

    report_md = report_path.read_text(encoding="utf-8")
    return report_markdown_to_pdf(
        report_md,
        run_id=run_id,
        manifest=manifest,
        metrics=metrics,
        judge_validation=judge_validation,
    )
