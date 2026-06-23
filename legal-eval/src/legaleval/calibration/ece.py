"""Expected Calibration Error and reliability binning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

DEFAULT_N_BINS = 10


@dataclass(frozen=True)
class CalibrationBin:
    bin_index: int
    confidence_low: float
    confidence_high: float
    mean_confidence: float
    empirical_accuracy: float
    count: int


def presence_correct(row_confidence: float, row_gold: bool, row_pred: bool) -> bool:
    return row_pred == row_gold


def compute_calibration_bins(
    confidences: list[float],
    outcomes: list[bool],
    *,
    n_bins: int = DEFAULT_N_BINS,
) -> list[CalibrationBin]:
    if len(confidences) != len(outcomes):
        raise ValueError("confidences and outcomes must have equal length")
    if not confidences:
        return []

    conf_arr = np.asarray(confidences, dtype=float)
    out_arr = np.asarray(outcomes, dtype=bool)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins: list[CalibrationBin] = []

    for idx in range(n_bins):
        low, high = float(bin_edges[idx]), float(bin_edges[idx + 1])
        if idx < n_bins - 1:
            mask = (conf_arr >= low) & (conf_arr < high)
        else:
            mask = (conf_arr >= low) & (conf_arr <= high)
        count = int(mask.sum())
        if count == 0:
            bins.append(
                CalibrationBin(
                    bin_index=idx,
                    confidence_low=low,
                    confidence_high=high,
                    mean_confidence=0.0,
                    empirical_accuracy=0.0,
                    count=0,
                )
            )
            continue
        mean_conf = float(conf_arr[mask].mean())
        emp_acc = float(out_arr[mask].mean())
        bins.append(
            CalibrationBin(
                bin_index=idx,
                confidence_low=low,
                confidence_high=high,
                mean_confidence=round(mean_conf, 6),
                empirical_accuracy=round(emp_acc, 6),
                count=count,
            )
        )
    return bins


def expected_calibration_error(bins: list[CalibrationBin]) -> float:
    total = sum(bin_.count for bin_ in bins)
    if total == 0:
        return 0.0
    ece = sum(
        (bin_.count / total) * abs(bin_.empirical_accuracy - bin_.mean_confidence)
        for bin_ in bins
        if bin_.count > 0
    )
    return round(ece, 6)


def bins_to_dict(bins: list[CalibrationBin]) -> list[dict[str, Any]]:
    return [
        {
            "bin_index": bin_.bin_index,
            "confidence_low": bin_.confidence_low,
            "confidence_high": bin_.confidence_high,
            "mean_confidence": bin_.mean_confidence,
            "empirical_accuracy": bin_.empirical_accuracy,
            "count": bin_.count,
        }
        for bin_ in bins
    ]
