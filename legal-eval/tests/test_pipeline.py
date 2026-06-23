"""Tests for pipeline orchestration, manifest, and report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legaleval.data.cuad import EvalExample
from legaleval.manifest import build_manifest, sha256_file, write_manifest
from legaleval.paths import run_root
from legaleval.pipeline import ensure_eval_set, generate_run_id
from legaleval.report.generate import eval_set_stats, generate_report, write_report


def test_generate_run_id_unique() -> None:
    assert generate_run_id() != generate_run_id()


def test_ensure_eval_set_uses_existing(tmp_path: Path) -> None:
    path = tmp_path / "eval.jsonl"
    example = EvalExample(
        id="x",
        contract_excerpt="text",
        category="Anti-Assignment",
        present=True,
        gold_spans=["text"],
        contract_title="T",
    )
    path.write_text(example.model_dump_json() + "\n", encoding="utf-8")
    ensure_eval_set(path, rebuild=False)
    assert path.exists()


def test_manifest_records_hash_and_models(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eval_path = tmp_path / "eval.jsonl"
    eval_path.write_text('{"id":"a","contract_excerpt":"x","category":"c","present":true,"gold_spans":["x"],"contract_title":"T"}\n', encoding="utf-8")
    models_path = tmp_path / "models.yaml"
    models_path.write_text(
        "models: {}\n"
        "judge:\n"
        "  provider: anthropic\n"
        "  model_id: test\n"
        "  env_key: K\n",
        encoding="utf-8",
    )

    manifest = build_manifest(
        run_id="run-test",
        run_date_utc="2026-01-01T00:00:00Z",
        eval_set_path=eval_path,
        seeds={"eval_set": 42, "bootstrap": 42, "judge_validation": 42},
        steps_completed=["data", "models"],
        models_config=models_path,
    )
    assert manifest["eval_set"]["sha256"] == sha256_file(eval_path)
    assert manifest["models_yaml"]["pinned"]["judge"]["model_id"] == "test"

    out = write_manifest(manifest, tmp_path / "manifest.json")
    assert out.exists()


def test_eval_set_stats() -> None:
    examples = [
        EvalExample(id="a", contract_excerpt="x", category="Cat A", present=True, gold_spans=["x"], contract_title="T"),
        EvalExample(id="b", contract_excerpt="y", category="Cat A", present=False, gold_spans=[], contract_title="T"),
        EvalExample(id="c", contract_excerpt="z", category="Cat B", present=True, gold_spans=["z"], contract_title="T"),
    ]
    stats = eval_set_stats(examples)
    assert stats["n_examples"] == 3
    assert stats["present"] == 2
    assert stats["absent"] == 1


def test_generate_report_from_fixture_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_id = "report-test"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)

    eval_path = tmp_path / "eval.jsonl"
    eval_path.write_text(
        EvalExample(
            id="e1",
            contract_excerpt="Assignment requires consent.",
            category="Anti-Assignment",
            present=True,
            gold_spans=["Assignment requires consent"],
            contract_title="C1",
        ).model_dump_json()
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "run_id": run_id,
        "run_date_utc": "2026-01-01T00:00:00Z",
        "seeds": {"eval_set": 42, "bootstrap": 42, "judge_validation": 42},
        "eval_set": {"sha256": sha256_file(eval_path)},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    metrics = {
        "models": {
            "stub": {
                "presence": {
                    "overall": {
                        "f1": 0.8,
                        "f1_ci_95": {"low": 0.7, "high": 0.9},
                    }
                },
                "span_grounding": {
                    "overall": {
                        "mean_jaccard": 0.6,
                        "mean_jaccard_ci_95": {"low": 0.5, "high": 0.7},
                        "hallucination_rate": 0.1,
                    }
                },
                "reliability": {"combined_error_rate": 0.05},
            }
        }
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")

    validation = {
        "sample_size": 60,
        "agreement": {
            "cohens_kappa": 0.75,
            "passes_threshold": True,
            "accuracy": 0.9,
            "n_scored": 60,
        },
    }
    (run_dir / "judge").mkdir()
    (run_dir / "judge" / "validation.json").write_text(json.dumps(validation), encoding="utf-8")

    calibration = {"models": {"stub": {"ece": 0.12}}}
    (run_dir / "calibration").mkdir()
    (run_dir / "calibration" / "ece.json").write_text(json.dumps(calibration), encoding="utf-8")

    errors_summary = {
        "models": {
            "stub": {
                "counts_by_bucket": {"missed_present": 2, "parse_fail": 1},
            }
        }
    }
    (run_dir / "errors_summary.json").write_text(json.dumps(errors_summary), encoding="utf-8")

    (run_dir / "raw").mkdir()
    (run_dir / "raw" / "stub.jsonl").write_text("", encoding="utf-8")

    import legaleval.paths as paths_mod
    import legaleval.report.generate as gen_mod
    import legaleval.metrics.compute as compute_mod

    monkeypatch.setattr(paths_mod, "run_root", lambda rid: tmp_path / rid)
    monkeypatch.setattr(paths_mod, "run_manifest_path", lambda rid: tmp_path / rid / "manifest.json")
    monkeypatch.setattr(paths_mod, "run_metrics_path", lambda rid: tmp_path / rid / "metrics.json")
    monkeypatch.setattr(paths_mod, "run_judge_validation_path", lambda rid: tmp_path / rid / "judge" / "validation.json")
    monkeypatch.setattr(paths_mod, "run_calibration_ece_path", lambda rid: tmp_path / rid / "calibration" / "ece.json")
    monkeypatch.setattr(paths_mod, "run_errors_summary_path", lambda rid: tmp_path / rid / "errors_summary.json")
    monkeypatch.setattr(paths_mod, "run_report_path", lambda rid: tmp_path / rid / "REPORT.md")
    monkeypatch.setattr(compute_mod, "raw_results_dir", lambda rid: tmp_path / rid / "raw")
    monkeypatch.setattr(gen_mod, "run_manifest_path", paths_mod.run_manifest_path)
    monkeypatch.setattr(gen_mod, "run_metrics_path", paths_mod.run_metrics_path)
    monkeypatch.setattr(gen_mod, "run_judge_validation_path", paths_mod.run_judge_validation_path)
    monkeypatch.setattr(gen_mod, "run_calibration_ece_path", paths_mod.run_calibration_ece_path)
    monkeypatch.setattr(gen_mod, "run_errors_summary_path", paths_mod.run_errors_summary_path)
    monkeypatch.setattr(gen_mod, "run_report_path", paths_mod.run_report_path)

    report = generate_report(run_id, eval_set_path=eval_path)
    assert "Judge validation" in report
    assert "Cohen's κ" in report
    assert "Findings" in report
    assert "Anti-Assignment" in report

    path = write_report(run_id, eval_set_path=eval_path)
    assert path.exists()
