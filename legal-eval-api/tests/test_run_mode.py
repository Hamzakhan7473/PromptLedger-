"""Tests for run mode on create run requests."""

from legal_eval_api.schemas import CreateRunRequest


def test_create_run_defaults_to_eval() -> None:
    request = CreateRunRequest(dataset_id="ds1", models=["openai"])
    assert request.mode == "eval"


def test_create_run_agent_mode() -> None:
    request = CreateRunRequest(dataset_id="ds1", models=["openai"], mode="agent")
    assert request.mode == "agent"
