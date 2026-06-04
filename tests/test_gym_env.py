from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_gym_reset_step_done() -> None:
    from prompt_ledger.platform.gym_env import episode_done, reset, step

    ep = reset("tax")
    eid = ep["episode_id"]
    assert ep["observation"]["environment"] == "tax"
    r = step(eid, "rag_retriever")
    assert "reward" in r
    assert episode_done(eid) is False
    step(eid, "finish")
    assert episode_done(eid) is True


def test_reward_formula() -> None:
    from prompt_ledger.platform.reward_formula import compute_standard_reward

    out = compute_standard_reward(
        correctness=1.0,
        citations=1.0,
        latency=0.9,
        cost=0.8,
        compliance=1.0,
    )
    assert out["reward"] >= 0.9
    assert out["weights"]["correctness"] == 0.4


def test_long_horizon_task() -> None:
    from prompt_ledger.platform.long_horizon import run_long_horizon_task

    result = run_long_horizon_task("tax_research_pack")
    assert result["steps_executed"] >= 1
    assert result["total_reward"] > 0


def test_supervisor_multi_agent() -> None:
    from prompt_ledger.platform.multi_agent import run_supervisor_task

    out = run_supervisor_task("legal", "Review clause", agents=["legal_agent", "citation_agent"])
    assert len(out["sub_results"]) >= 1
