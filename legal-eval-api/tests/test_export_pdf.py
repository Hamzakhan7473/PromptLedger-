"""Tests for PDF export."""

from __future__ import annotations

import json
from pathlib import Path

from legal_eval_api.export_pdf import load_run_report_pdf, report_markdown_to_pdf


def test_report_markdown_to_pdf_without_metadata() -> None:
    md = "# Summary\n\n## Metrics\n\nPresence F1: **0.89**\n"
    pdf = report_markdown_to_pdf(md, run_id="test_run")
    assert pdf.startswith(b"%PDF")


def test_report_markdown_to_pdf_with_trust_cover() -> None:
    md = "# Summary\n\nBody text.\n"
    manifest = {
        "run_id": "test_run",
        "run_date_utc": "2026-01-15T12:00:00Z",
        "seeds": {"eval_set": 42, "bootstrap": 42},
        "eval_set": {"path": "eval_set.jsonl", "sha256": "abc123"},
        "models_yaml": {
            "pinned": {
                "models": {"model-a": {"model_id": "gpt-test"}},
                "judge": {"model_id": "judge-test"},
            },
        },
    }
    metrics = {
        "eval_set": "eval_set.jsonl",
        "models": {
            "model-a": {
                "presence": {"overall": {"f1": 0.89}},
                "span_grounding": {"overall": {"mean_jaccard": 0.72}},
            },
        },
    }
    judge_validation = {"agreement": {"cohens_kappa": 0.75}}
    pdf = report_markdown_to_pdf(
        md,
        run_id="test_run",
        manifest=manifest,
        metrics=metrics,
        judge_validation=judge_validation,
    )
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1200


def test_load_run_report_pdf_from_demo_bundle(tmp_path, monkeypatch) -> None:
    import legaleval.paths as paths_mod

    run_id = "demo"
    run_dir = tmp_path / "results" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "REPORT.md").write_text("# Demo report\n\n## Metrics\n\nDone.\n", encoding="utf-8")
    manifest = {
        "run_id": run_id,
        "run_date_utc": "2026-01-15T12:00:00Z",
        "seeds": {"eval_set": 42},
        "eval_set": {"path": "eval_set.jsonl", "sha256": "demo"},
        "models_yaml": {"pinned": {"models": {"model-a": {"model_id": "demo-a"}}}},
    }
    metrics = {
        "eval_set": "eval_set.jsonl",
        "models": {"model-a": {"presence": {"overall": {"f1": 0.8}}}},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")

    monkeypatch.setattr(paths_mod, "project_root", lambda: tmp_path)

    pdf = load_run_report_pdf(run_id)
    assert pdf.startswith(b"%PDF")
