"""Tests for calibration (ECE and reliability bins)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legaleval.calibration.ece import (
    compute_calibration_bins,
    expected_calibration_error,
)
from legaleval.calibration.plot import plot_reliability_curve
from legaleval.calibration.run import calibrate_model, write_ece_json
from legaleval.report.records import EnrichedRow


def _row(
    example_id: str,
    *,
    gold_present: bool,
    pred_present: bool | None,
    confidence: float | None,
    parse_error: bool = False,
) -> EnrichedRow:
    return EnrichedRow(
        example_id=example_id,
        category="Anti-Assignment",
        contract_title="T",
        model="stub",
        contract_excerpt="text",
        gold_present=gold_present,
        gold_spans=[],
        pred_present=pred_present,
        pred_span=None,
        confidence=confidence,
        reasoning=None,
        has_api_error=False,
        has_parse_error=parse_error,
        parse_error="err" if parse_error else None,
        api_error=None,
        raw_text=None,
    )


def test_well_calibrated_low_ece() -> None:
    confidences = [0.05] * 10 + [0.95] * 10
    outcomes = [False] * 10 + [True] * 10
    bins = compute_calibration_bins(confidences, outcomes, n_bins=10)
    ece = expected_calibration_error(bins)
    assert ece < 0.1


def test_miscalibrated_positive_ece() -> None:
    confidences = [0.9] * 10
    outcomes = [False] * 10
    bins = compute_calibration_bins(confidences, outcomes, n_bins=10)
    ece = expected_calibration_error(bins)
    assert ece > 0.5


def test_calibrate_model_writes_plot_and_ece(tmp_path: Path) -> None:
    rows = [
        _row("a", gold_present=True, pred_present=True, confidence=0.9),
        _row("b", gold_present=False, pred_present=False, confidence=0.8),
        _row("c", gold_present=True, pred_present=False, confidence=0.95),
        _row("d", gold_present=False, pred_present=True, confidence=0.85),
    ]
    result = calibrate_model("stub", rows, output_dir=tmp_path)
    assert (tmp_path / "stub.png").exists()
    assert result["ece"] >= 0.0
    assert result["n_calibrated"] == 4

    payload = {"run_id": "r", "eval_set": "e.jsonl", "models": {"stub": result}}
    ece_path = write_ece_json(payload, tmp_path / "ece.json")
    loaded = json.loads(ece_path.read_text(encoding="utf-8"))
    assert loaded["models"]["stub"]["ece"] == result["ece"]


def test_plot_reliability_curve_empty_bins(tmp_path: Path) -> None:
    bins = compute_calibration_bins([], [], n_bins=10)
    path = plot_reliability_curve(bins, model="empty", ece=0.0, output_path=tmp_path / "empty.png")
    assert path.exists()
