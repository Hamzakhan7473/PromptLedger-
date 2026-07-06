"""Tests for model runner and eval execution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legaleval.data.schema import EvalExample
from legaleval.models.runner import (
    CallLogRow,
    ModelClient,
    ModelConfig,
    RawResponse,
    execute_example,
    load_models_config,
    resolve_model_names,
    run_eval,
    run_model_on_eval_set,
)
from legaleval.paths import run_raw_dir


class StubClient(ModelClient):
    provider = "stub"

    def __init__(self, text: str) -> None:
        super().__init__(
            name="stub",
            model_id="stub-model",
            api_key="test-key",
        )
        self._text = text

    def _complete(self, prompt: str, system: str) -> RawResponse:
        return RawResponse(text=self._text, latency_ms=12.5, input_tokens=10, output_tokens=5)


@pytest.fixture
def example() -> EvalExample:
    return EvalExample(
        id="test-001",
        contract_excerpt="Assignment requires consent.",
        category="Anti-Assignment",
        present=True,
        gold_spans=["Assignment requires consent"],
        contract_title="Stub Contract",
    )


@pytest.fixture
def models_yaml(tmp_path: Path) -> Path:
    path = tmp_path / "models.yaml"
    path.write_text(
        """
defaults:
  max_tokens: 1024
  temperature: 0.0
models:
  stub:
    provider: anthropic
    model_id: TODO_STUB_MODEL
    env_key: STUB_API_KEY
  other:
    provider: openai
    model_id: TODO_OTHER_MODEL
    env_key: OTHER_API_KEY
""".strip(),
        encoding="utf-8",
    )
    return path


def test_load_models_config(models_yaml: Path) -> None:
    configs = load_models_config(models_yaml)
    assert set(configs) == {"stub", "other"}
    assert configs["stub"].provider == "anthropic"
    assert configs["stub"].max_tokens == 1024


def test_resolve_model_names_all(models_yaml: Path) -> None:
    configs = load_models_config(models_yaml)
    assert resolve_model_names("all", configs) == ["other", "stub"]


def test_execute_example_success(example: EvalExample) -> None:
    client = StubClient(
        '{"present": true, "span": "Assignment requires consent.", '
        '"confidence": 0.95, "reasoning": "Explicit assignment clause."}'
    )
    row = execute_example(client, example, run_id="run-test")
    assert row.error is None
    assert row.parse_error is None
    assert row.parsed is not None
    assert row.parsed["present"] is True
    assert row.latency_ms == 12.5
    assert row.input_tokens == 10


def test_execute_example_parse_failure(example: EvalExample) -> None:
    client = StubClient("definitely not json")
    row = execute_example(client, example, run_id="run-test")
    assert row.error is None
    assert row.parse_error is not None
    assert row.parsed is None


class FailingClient(ModelClient):
    provider = "failing"

    def __init__(self) -> None:
        super().__init__(name="failing", model_id="fail", api_key="x")

    def _complete(self, prompt: str, system: str) -> RawResponse:
        raise RuntimeError("API unavailable")


def test_execute_example_api_failure(example: EvalExample) -> None:
    client = FailingClient()
    row = execute_example(client, example, run_id="run-test")
    assert row.error is not None
    assert "API unavailable" in row.error


def test_run_model_records_missing_key_errors(
    example: EvalExample, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = ModelConfig(
        name="missing",
        provider="openai",
        model_id="TODO",
        env_key="DEFINITELY_MISSING_KEY_XYZ",
    )
    output = tmp_path / "missing.jsonl"
    monkeypatch.delenv("DEFINITELY_MISSING_KEY_XYZ", raising=False)
    run_model_on_eval_set(config, [example], run_id="run-1", output_path=output)

    rows = [CallLogRow.model_validate_json(line) for line in output.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0].error is not None


def test_run_eval_with_stub_client(
    example: EvalExample,
    models_yaml: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    eval_path = tmp_path / "eval_set.jsonl"
    eval_path.write_text(example.model_dump_json() + "\n", encoding="utf-8")

    def fake_create_client(config: ModelConfig) -> ModelClient:
        return StubClient(
            '{"present": false, "span": null, "confidence": 0.7, "reasoning": "Absent."}'
        )

    run_id = "test-run-abc"
    out_dir = run_raw_dir(run_id)
    monkeypatch.setattr("legaleval.paths.run_raw_dir", lambda _run_id: tmp_path / "raw" / _run_id)
    monkeypatch.setattr("legaleval.metrics.compute.run_raw_dir", lambda _run_id: tmp_path / "raw" / _run_id)
    monkeypatch.setattr("legaleval.models.runner.create_client", fake_create_client)

    output_dir = run_eval(
        models="stub",
        eval_set_path=eval_path,
        run_id=run_id,
        models_config_path=models_yaml,
    )

    log_path = output_dir / "stub.jsonl"
    assert log_path.exists()
    row = json.loads(log_path.read_text().strip())
    assert row["example_id"] == example.id
    assert row["parsed"]["present"] is False
    assert row["error"] is None
