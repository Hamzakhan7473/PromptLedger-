"""Reliability diagram plotting for calibration analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from legaleval.calibration.ece import CalibrationBin


def plot_reliability_curve(
    bins: list[CalibrationBin],
    *,
    model: str,
    ece: float,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plotted = [bin_ for bin_ in bins if bin_.count > 0]
    if not plotted:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "No calibration data", ha="center", va="center")
        ax.set_title(f"Reliability — {model} (ECE=n/a)")
    else:
        confidences = [bin_.mean_confidence for bin_ in plotted]
        accuracies = [bin_.empirical_accuracy for bin_ in plotted]
        counts = [bin_.count for bin_ in plotted]

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect calibration")
        ax.plot(confidences, accuracies, marker="o", linewidth=2, label="Model")
        for x, y, n in zip(confidences, accuracies, counts, strict=True):
            ax.annotate(str(n), (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Mean predicted confidence (decile bin)")
        ax.set_ylabel("Empirical accuracy (presence)")
        ax.set_title(f"Reliability — {model} (ECE={ece:.4f})")
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
