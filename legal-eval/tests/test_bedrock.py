"""Tests for Amazon Bedrock Converse client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from legaleval.data.cuad import EvalExample
from legaleval.models.bedrock import CLAUSE_PREDICTION_TOOL_NAME
from legaleval.models.runner import (
    BedrockClient,
    ModelConfig,
    create_client,
    execute_example,
)
from legaleval.manifest import build_manifest, extract_model_routing


def _valid_converse_response() -> dict:
    return {
        "output": {
            "message": {
                "content": [
                    {
                        "toolUse": {
                            "toolUseId": "tool-1",
                            "name": CLAUSE_PREDICTION_TOOL_NAME,
                            "input": {
                                "present": True,
                                "span": "Assignment requires consent.",
                                "confidence": 0.91,
                                "reasoning": "Explicit assignment restriction.",
                            },
                        }
                    }
                ]
            }
        },
        "usage": {
            "inputTokens": 120,
            "outputTokens": 45,
            "totalTokens": 165,
        },
    }


def _malformed_converse_response() -> dict:
    return {
        "output": {
            "message": {
                "content": [{"text": '{"present": true}'}]
            }
        },
        "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
    }


@pytest.fixture
def example() -> EvalExample:
    return EvalExample(
        id="bedrock-001",
        contract_excerpt="Assignment requires consent.",
        category="Anti-Assignment",
        present=True,
        gold_spans=["Assignment requires consent."],
        contract_title="Bedrock Contract",
    )


def test_bedrock_client_valid_tool_call(example: EvalExample) -> None:
    mock_runtime = MagicMock()
    mock_runtime.converse.return_value = _valid_converse_response()

    client = BedrockClient(
        name="bedrock_claude",
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1",
        bedrock_client=mock_runtime,
    )
    row = execute_example(client, example, run_id="run-bedrock")

    assert row.error is None
    assert row.parse_error is None
    assert row.provider == "bedrock"
    assert row.parsed is not None
    assert row.parsed["present"] is True
    assert row.parsed["span"] == "Assignment requires consent."
    assert row.input_tokens == 120
    assert row.output_tokens == 45
    assert row.total_tokens == 165

    request = mock_runtime.converse.call_args.kwargs
    assert request["modelId"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert request["toolConfig"]["toolChoice"] == {"any": {}}
    assert request["toolConfig"]["tools"][0]["toolSpec"]["name"] == CLAUSE_PREDICTION_TOOL_NAME


def test_bedrock_client_malformed_response(example: EvalExample) -> None:
    mock_runtime = MagicMock()
    mock_runtime.converse.return_value = _malformed_converse_response()

    client = BedrockClient(
        name="bedrock_claude",
        model_id="meta.llama3-70b-instruct-v1:0",
        region="us-west-2",
        bedrock_client=mock_runtime,
    )
    row = execute_example(client, example, run_id="run-bedrock")

    assert row.error is not None
    assert "toolUse" in row.error


def test_bedrock_access_denied_is_clear_and_not_retried(example: EvalExample) -> None:
    mock_runtime = MagicMock()
    mock_runtime.converse.side_effect = ClientError(
        {
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "Model access is not granted.",
            }
        },
        "Converse",
    )

    client = BedrockClient(
        name="bedrock_claude",
        model_id="TODO_BEDROCK_MODEL",
        region="us-east-1",
        bedrock_client=mock_runtime,
    )
    row = execute_example(client, example, run_id="run-bedrock")

    assert row.error is not None
    assert "AccessDeniedException" in row.error
    assert "Bedrock console" in row.error
    assert mock_runtime.converse.call_count == 1


def test_bedrock_tool_choice_fallback_on_validation_error(example: EvalExample) -> None:
    mock_runtime = MagicMock()
    mock_runtime.converse.side_effect = [
        ClientError(
            {
                "Error": {
                    "Code": "ValidationException",
                    "Message": "This model doesn't support toolConfig.toolChoice.any",
                }
            },
            "Converse",
        ),
        _valid_converse_response(),
    ]

    client = BedrockClient(
        name="bedrock_llama",
        model_id="meta.llama3-70b-instruct-v1:0",
        region="us-east-1",
        bedrock_client=mock_runtime,
    )
    row = execute_example(client, example, run_id="run-bedrock")

    assert row.error is None
    assert row.parsed is not None
    assert mock_runtime.converse.call_count == 2
    assert "toolChoice" not in mock_runtime.converse.call_args_list[1].kwargs["toolConfig"]


def test_create_bedrock_client_without_api_key() -> None:
    config = ModelConfig(
        name="bedrock_claude",
        provider="bedrock",
        model_id="TODO_BEDROCK_CLAUDE_MODEL",
        region="us-east-1",
        provider_path="bedrock",
    )
    client = create_client(config)
    assert isinstance(client, BedrockClient)
    assert client.region == "us-east-1"
    assert client.resolved_provider_path == "bedrock"


def test_create_bedrock_client_requires_region() -> None:
    config = ModelConfig(
        name="bedrock_claude",
        provider="bedrock",
        model_id="TODO_BEDROCK_CLAUDE_MODEL",
    )
    with pytest.raises(ValueError, match="region"):
        create_client(config)


def test_manifest_model_routing_distinguishes_provider_paths(tmp_path) -> None:
    models_path = tmp_path / "models.yaml"
    models_path.write_text(
        """
models:
  anthropic:
    provider: anthropic
    provider_path: anthropic
    model_id: claude-direct
    env_key: ANTHROPIC_API_KEY
  bedrock_claude:
    provider: bedrock
    provider_path: bedrock
    model_id: anthropic.claude-3-5-sonnet-20241022-v2:0
    region: us-east-1
judge:
  provider: anthropic
  provider_path: anthropic
  model_id: judge
  env_key: ANTHROPIC_API_KEY
""".strip(),
        encoding="utf-8",
    )
    eval_path = tmp_path / "eval.jsonl"
    eval_path.write_text(
        '{"id":"a","contract_excerpt":"x","category":"c","present":true,'
        '"gold_spans":["x"],"contract_title":"T"}\n',
        encoding="utf-8",
    )

    manifest = build_manifest(
        run_id="run-routing",
        run_date_utc="2026-01-01T00:00:00Z",
        eval_set_path=eval_path,
        seeds={"eval_set": 42},
        steps_completed=["models"],
        models_config=models_path,
    )

    routing = manifest["model_routing"]
    assert routing["anthropic"]["provider_path"] == "anthropic"
    assert routing["bedrock_claude"]["provider_path"] == "bedrock"
    assert routing["bedrock_claude"]["region"] == "us-east-1"
    assert routing["judge"]["provider_path"] == "anthropic"


def test_extract_model_routing_defaults_provider_path() -> None:
    routing = extract_model_routing(
        {
            "models": {
                "openai": {
                    "provider": "openai",
                    "model_id": "gpt-4o",
                    "env_key": "OPENAI_API_KEY",
                }
            }
        }
    )
    assert routing["openai"]["provider_path"] == "openai"
