from __future__ import annotations

from typing import Any

from prompt_ledger.platform.config import load_platform_yaml
from prompt_ledger.platform.models import RewardBreakdown


def load_default_weights() -> dict[str, float]:
    raw = load_platform_yaml("reward_formula.yaml")
    return {k: float(v) for k, v in (raw.get("weights") or {}).items()}


def compute_standard_reward(
    *,
    correctness: float,
    citations: float,
    latency: float,
    cost: float,
    compliance: float,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """reward-service formula: 0.4 correctness + 0.2 citations + ..."""
    w = weights or load_default_weights()
    breakdown = {
        "correctness": correctness,
        "citations": citations,
        "latency": latency,
        "cost": cost,
        "compliance": compliance,
    }
    total = sum(w.get(k, 0.0) * breakdown[k] for k in breakdown)
    return {
        "reward": round(min(1.0, max(0.0, total)), 4),
        "weights": w,
        "breakdown": breakdown,
        "formula": load_platform_yaml("reward_formula.yaml").get("formula", "").strip(),
    }


def from_trajectory_breakdown(rb: RewardBreakdown) -> dict[str, Any]:
    return compute_standard_reward(
        correctness=rb.correctness,
        citations=rb.citation_quality,
        latency=rb.latency,
        cost=rb.cost,
        compliance=rb.policy_compliance,
    )
