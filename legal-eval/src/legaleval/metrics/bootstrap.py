"""Bootstrap confidence intervals for metric estimates."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np


def bootstrap_percentile_ci(
    values: Sequence[float],
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float] | None:
    """Return (low, high) percentile CI for the mean of values."""
    if not values:
        return None
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    means = np.empty(n_bootstrap, dtype=float)
    n = len(arr)
    for i in range(n_bootstrap):
        sample = arr[rng.integers(0, n, size=n)]
        means[i] = float(sample.mean())
    alpha = (1.0 - ci) / 2.0
    low, high = np.percentile(means, [100 * alpha, 100 * (1 - alpha)])
    return float(low), float(high)


def bootstrap_f1_ci(
    gold: Sequence[bool],
    pred: Sequence[bool],
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float] | None:
    """Example-level bootstrap CI for F1."""
    if not gold:
        return None
    rng = np.random.default_rng(seed)
    gold_arr = np.asarray(gold, dtype=bool)
    pred_arr = np.asarray(pred, dtype=bool)
    n = len(gold_arr)
    f1_scores = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        g = gold_arr[idx]
        p = pred_arr[idx]
        f1_scores[i] = _f1_from_bools(g, p)
    alpha = (1.0 - ci) / 2.0
    low, high = np.percentile(f1_scores, [100 * alpha, 100 * (1 - alpha)])
    return float(low), float(high)


def bootstrap_stat_ci(
    values: Sequence[float],
    stat_fn: Callable[[Sequence[float]], float],
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float] | None:
    """Bootstrap CI for an arbitrary scalar statistic over resampled values."""
    if not values:
        return None
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    stats = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        sample = arr[rng.integers(0, n, size=n)]
        stats[i] = stat_fn(sample.tolist())
    alpha = (1.0 - ci) / 2.0
    low, high = np.percentile(stats, [100 * alpha, 100 * (1 - alpha)])
    return float(low), float(high)


def _f1_from_bools(gold: np.ndarray, pred: np.ndarray) -> float:
    tp = int(np.sum(gold & pred))
    fp = int(np.sum(~gold & pred))
    fn = int(np.sum(gold & ~pred))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)
