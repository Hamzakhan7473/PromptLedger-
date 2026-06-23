"""Span grounding metrics for true-positive presence cases."""

from __future__ import annotations

import re
from typing import Any

from legaleval.metrics.bootstrap import bootstrap_percentile_ci


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def token_jaccard(predicted: str, gold: str) -> float:
    pred_tokens = tokenize(predicted)
    gold_tokens = tokenize(gold)
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    intersection = pred_tokens & gold_tokens
    union = pred_tokens | gold_tokens
    return len(intersection) / len(union)


def best_gold_jaccard(predicted_span: str, gold_spans: list[str]) -> float:
    if not gold_spans:
        return 0.0
    return max(token_jaccard(predicted_span, gold) for gold in gold_spans)


def span_in_contract(predicted_span: str, contract_excerpt: str) -> bool:
    return predicted_span in contract_excerpt


def jaccard_distribution(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {
            "n": 0,
            "min": None,
            "p25": None,
            "median": None,
            "p75": None,
            "max": None,
        }
    sorted_vals = sorted(values)
    n = len(sorted_vals)

    def percentile(p: float) -> float:
        idx = min(n - 1, max(0, int(round(p * (n - 1)))))
        return round(sorted_vals[idx], 6)

    return {
        "n": n,
        "min": round(sorted_vals[0], 6),
        "p25": percentile(0.25),
        "median": percentile(0.5),
        "p75": percentile(0.75),
        "max": round(sorted_vals[-1], 6),
    }


def span_grounding_metrics(
    *,
    predicted_spans: list[str],
    gold_spans_list: list[list[str]],
    contract_excerpts: list[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute span metrics over true-positive presence rows only."""
    if not (
        len(predicted_spans) == len(gold_spans_list) == len(contract_excerpts)
    ):
        raise ValueError("Span grounding inputs must have equal length")

    jaccards: list[float] = []
    hallucinated = 0
    for pred_span, gold_spans, excerpt in zip(
        predicted_spans, gold_spans_list, contract_excerpts, strict=True
    ):
        in_contract = span_in_contract(pred_span, excerpt)
        if not in_contract:
            hallucinated += 1
        jaccards.append(best_gold_jaccard(pred_span, gold_spans))

    n = len(predicted_spans)
    mean_jaccard = sum(jaccards) / n if n else 0.0
    ci = bootstrap_percentile_ci(jaccards, n_bootstrap=n_bootstrap, seed=seed)

    result: dict[str, Any] = {
        "n_tp_presence": n,
        "hallucination_count": hallucinated,
        "hallucination_rate": round(hallucinated / n, 6) if n else 0.0,
        "substring_grounded_count": n - hallucinated,
        "substring_grounded_rate": round((n - hallucinated) / n, 6) if n else 0.0,
        "mean_jaccard": round(mean_jaccard, 6),
        "jaccard_distribution": jaccard_distribution(jaccards),
        "jaccard_values": [round(v, 6) for v in jaccards],
    }
    if ci is not None:
        result["mean_jaccard_ci_95"] = {"low": round(ci[0], 6), "high": round(ci[1], 6)}
    return result
