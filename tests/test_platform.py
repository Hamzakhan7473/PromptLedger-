from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROMPT_LEDGER_ROOT", str(Path(__file__).resolve().parents[1]))


def test_list_environments() -> None:
    from prompt_ledger.platform.environments import list_environments

    ids = {e["id"] for e in list_environments()}
    assert ids == {
        "tax",
        "legal",
        "financial_modeling",
        "contract_review",
        "research",
    }


def test_agent_run_legal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TRAJECTORY_DB_PATH", str(tmp_path / "t.db"))
    from prompt_ledger.platform.orchestrator import run_agent_task

    result = run_agent_task("legal", "Review payment terms", persist=True)
    assert result["trajectory_id"]
    assert result["reward"]["total"] > 0
    assert "rag_retriever" in result["tools_invoked"]


def test_evaluate_and_datasets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TRAJECTORY_DB_PATH", str(tmp_path / "t.db"))
    from prompt_ledger.platform.dataset import build_rl_datasets
    from prompt_ledger.platform.evaluation import evaluate_trajectories
    from prompt_ledger.platform.orchestrator import run_agent_task

    run_agent_task("contract_review", "Indemnity cap review")
    metrics = evaluate_trajectories()
    assert metrics["count"] >= 1
    build_rl_datasets(output_dir=tmp_path / "ds")
    assert (tmp_path / "ds" / "sft.jsonl").is_file()
