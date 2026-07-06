"""Run calibration analysis for all models in a raw eval run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from legaleval.calibration.ece import (
    compute_calibration_bins,
    expected_calibration_error,
    bins_to_dict,
)
from legaleval.calibration.plot import plot_reliability_curve
from legaleval.data.schema import read_eval_set_jsonl
from legaleval.metrics.compute import load_raw_run
from legaleval.paths import run_calibration_dir, run_calibration_ece_path
from legaleval.report.records import EnrichedRow, enrich_run


def calibration_dir(run_id: str | None = None) -> Path:
    if run_id is None:
        from legaleval.paths import project_root
        return project_root() / "results" / "calibration"
    return run_calibration_dir(run_id)


def ece_json_path(run_id: str | None = None) -> Path:
    if run_id is None:
        return calibration_dir() / "ece.json"
    return run_calibration_ece_path(run_id)


def _calibration_points(rows: list[EnrichedRow]) -> tuple[list[float], list[bool]]:
    confidences: list[float] = []
    outcomes: list[bool] = []
    for row in rows:
        if row.confidence is None or row.pred_present is None:
            continue
        if row.has_api_error or row.has_parse_error:
            continue
        confidences.append(row.confidence)
        outcomes.append(row.pred_present == row.gold_present)
    return confidences, outcomes


def calibrate_model(
    model: str,
    rows: list[EnrichedRow],
    *,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    out_dir = output_dir or calibration_dir()
    confidences, outcomes = _calibration_points(rows)
    bins = compute_calibration_bins(confidences, outcomes)
    ece = expected_calibration_error(bins)

    plot_path = out_dir / f"{model}.png"
    plot_reliability_curve(bins, model=model, ece=ece, output_path=plot_path)

    return {
        "model": model,
        "ece": ece,
        "n_calibrated": len(confidences),
        "n_excluded": len(rows) - len(confidences),
        "bins": bins_to_dict(bins),
        "plot_path": str(plot_path),
    }


def run_calibration(
    run_id: str,
    eval_set_path: Path,
    *,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    gold_examples = read_eval_set_jsonl(eval_set_path)
    gold_by_id = {example.id: example for example in gold_examples}
    raw_by_model = load_raw_run(run_id)
    enriched = enrich_run(raw_by_model, gold_by_id)

    out_dir = output_dir or calibration_dir(run_id)
    per_model: dict[str, Any] = {}
    for model, rows in sorted(enriched.items()):
        per_model[model] = calibrate_model(model, rows, output_dir=out_dir)

    payload = {
        "run_id": run_id,
        "eval_set": str(eval_set_path),
        "models": per_model,
    }
    return payload


def write_ece_json(payload: dict[str, Any], path: Path | None = None) -> Path:
    output = path or ece_json_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    slim = {
        "run_id": payload["run_id"],
        "eval_set": payload["eval_set"],
        "models": {
            model: {
                "ece": data["ece"],
                "n_calibrated": data["n_calibrated"],
                "n_excluded": data["n_excluded"],
                "bins": data["bins"],
                "plot_path": data["plot_path"],
            }
            for model, data in payload["models"].items()
        },
    }
    with output.open("w", encoding="utf-8") as handle:
        json.dump(slim, handle, indent=2)
        handle.write("\n")
    return output
