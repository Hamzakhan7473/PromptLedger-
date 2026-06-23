"""Presence classification metrics."""

from __future__ import annotations

from typing import Any

from legaleval.metrics.bootstrap import bootstrap_f1_ci


def confusion_counts(gold: list[bool], pred: list[bool]) -> dict[str, int]:
    tp = sum(1 for g, p in zip(gold, pred, strict=True) if g and p)
    fp = sum(1 for g, p in zip(gold, pred, strict=True) if not g and p)
    fn = sum(1 for g, p in zip(gold, pred, strict=True) if g and not p)
    tn = sum(1 for g, p in zip(gold, pred, strict=True) if not g and not p)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall_f1(gold: list[bool], pred: list[bool]) -> dict[str, float]:
    counts = confusion_counts(gold, pred)
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )
    return {
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def presence_metrics(
    gold: list[bool],
    pred: list[bool],
    *,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    counts = confusion_counts(gold, pred)
    scores = precision_recall_f1(gold, pred)
    ci = bootstrap_f1_ci(gold, pred, n_bootstrap=n_bootstrap, seed=seed)
    result: dict[str, Any] = {
        **scores,
        "confusion_matrix": counts,
        "n": len(gold),
    }
    if ci is not None:
        result["f1_ci_95"] = {"low": round(ci[0], 6), "high": round(ci[1], 6)}
    return result
