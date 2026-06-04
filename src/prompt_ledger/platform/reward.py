from __future__ import annotations

from prompt_ledger.audit import run_audit
from prompt_ledger.packs import verify_pack
from prompt_ledger.paths import repo_root
from prompt_ledger.platform.environments import RLEnvironment
from prompt_ledger.platform.models import RewardBreakdown, Trajectory


def compute_reward(traj: Trajectory, env: RLEnvironment) -> RewardBreakdown:
    """Score trajectory using governance signals (no live LLM judge in demo mode)."""
    weights = env.reward_weights or {}

    findings = run_audit()
    relevant = [f for f in findings if f.prompt_id in (traj.prompt_id, "*")]
    errors = sum(1 for f in relevant if f.severity == "error")
    policy = 1.0 if errors == 0 else max(0.0, 1.0 - errors * 0.25)

    pack_issues = verify_pack(repo_root() / env.pack_dir)
    pack_errors = sum(1 for i in pack_issues if i.severity == "error")
    correctness = 1.0 if pack_errors == 0 else 0.6

    has_rag = any(tc.tool == "rag_retriever" for s in traj.steps for tc in s.tool_calls)
    chunks = 0
    for s in traj.steps:
        for tc in s.tool_calls:
            if tc.tool == "rag_retriever":
                chunks = int(tc.output.get("chunks") or 0)
    citation = 1.0 if has_rag and chunks > 0 else (0.5 if has_rag else 0.2)

    total_tool_ms = sum(
        tc.latency_ms for s in traj.steps for tc in s.tool_calls
    )
    latency = 1.0 if total_tool_ms < 500 else max(0.3, 1.0 - total_tool_ms / 5000)
    cost = 0.85  # stub: favor efficient tool use in demo

    human = float(traj.metadata.get("human_feedback", 0.0) or 0.0)

    breakdown = RewardBreakdown(
        correctness=correctness,
        citation_quality=citation,
        cost=cost,
        latency=latency,
        policy_compliance=policy,
        human_feedback=human,
    )

    total = 0.0
    for key, weight in weights.items():
        val = getattr(breakdown, key, 0.0)
        total += weight * val
    if not weights:
        total = (
            correctness + citation + policy + cost + latency
        ) / 5.0
    breakdown.total = round(min(1.0, max(0.0, total)), 4)
    return breakdown
