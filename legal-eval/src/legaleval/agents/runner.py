"""Agent-mode eval runner — same CallLogRow output as direct eval."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

from legaleval.agents.config import agent_invoke_config, agent_invoke_timeout_s
from legaleval.agents.harness import (
    build_agent_user_message,
    build_clause_agent,
    extract_agent_response_text,
)
from legaleval.agents.model_strings import supports_agent_mode, to_deepagents_model
from legaleval.agents.tokens import (
    TokenUsageTracker,
    TrackingModelClient,
    combine_agent_token_counts,
    sum_orchestrator_message_tokens,
)
from legaleval.data.schema import EvalExample, read_eval_set_jsonl
from legaleval.models.prompt import parse_model_response
from legaleval.models.runner import (
    CallLogRow,
    ModelConfig,
    append_log_row,
    create_client,
    load_models_config,
    resolve_model_names,
)
from legaleval.paths import run_raw_dir


def _require_deepagents() -> None:
    try:
        import deepagents  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Agent mode requires deepagents. Install with: "
            "pip install 'legal-eval[agents]'",
        ) from exc


def invoke_agent_with_limits(
    agent: object,
    input_state: dict[str, object],
    *,
    recursion_limit: int | None = None,
    timeout_s: float | None = None,
) -> dict[str, object]:
    """Invoke the agent with LangGraph recursion_limit and a wall-clock timeout."""
    config = agent_invoke_config(recursion_limit=recursion_limit)
    limit_s = agent_invoke_timeout_s(timeout_s)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            agent.invoke,  # type: ignore[attr-defined]
            input_state,
            config=config,
        )
        try:
            return future.result(timeout=limit_s)
        except FuturesTimeoutError as exc:
            raise TimeoutError(
                f"Agent invoke exceeded {limit_s}s wall-clock timeout",
            ) from exc


def execute_agent_example(
    agent: object,
    example: EvalExample,
    *,
    run_id: str,
    config: ModelConfig,
    client: TrackingModelClient,
    token_tracker: TokenUsageTracker,
    example_ref: list[EvalExample],
    recursion_limit: int | None = None,
    timeout_s: float | None = None,
) -> CallLogRow:
    row = CallLogRow(
        run_id=run_id,
        example_id=example.id,
        category=example.category,
        contract_title=example.contract_title,
        provider=client.provider,
        model=config.name,
        model_id=config.model_id,
    )
    started = time.perf_counter()
    example_ref.clear()
    example_ref.append(example)
    token_tracker.reset()

    try:
        result = invoke_agent_with_limits(
            agent,
            {"messages": [{"role": "user", "content": build_agent_user_message(example)}]},
            recursion_limit=recursion_limit,
            timeout_s=timeout_s,
        )
        row.raw_text = extract_agent_response_text(result)
    except Exception as exc:  # noqa: BLE001
        row.error = f"{type(exc).__name__}: {exc}"
        row.latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return row

    orchestrator_in, orchestrator_out = sum_orchestrator_message_tokens(result)
    row.input_tokens, row.output_tokens, row.total_tokens = combine_agent_token_counts(
        token_tracker,
        orchestrator_in,
        orchestrator_out,
    )
    row.latency_ms = round((time.perf_counter() - started) * 1000, 2)
    prediction, parse_error = parse_model_response(row.raw_text or "")
    if prediction is not None:
        row.parsed = prediction.model_dump()
    if parse_error is not None:
        row.parse_error = parse_error
    return row


def run_model_agent_on_eval_set(
    config: ModelConfig,
    examples: list[EvalExample],
    *,
    run_id: str,
    output_path: Path,
    recursion_limit: int | None = None,
    timeout_s: float | None = None,
) -> None:
    _require_deepagents()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not supports_agent_mode(config):
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                append_log_row(
                    handle,
                    CallLogRow(
                        run_id=run_id,
                        example_id=example.id,
                        category=example.category,
                        contract_title=example.contract_title,
                        provider=config.provider,
                        model=config.name,
                        model_id=config.model_id,
                        error=f"Agent mode unsupported for provider {config.provider!r}",
                    ),
                )
        return

    client: TrackingModelClient | None = None
    try:
        token_tracker = TokenUsageTracker()
        client = TrackingModelClient(create_client(config), token_tracker)
        example_ref: list[EvalExample] = []
        agent = build_clause_agent(to_deepagents_model(config), client, example_ref)
    except Exception as exc:  # noqa: BLE001
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                append_log_row(
                    handle,
                    CallLogRow(
                        run_id=run_id,
                        example_id=example.id,
                        category=example.category,
                        contract_title=example.contract_title,
                        provider=config.provider,
                        model=config.name,
                        model_id=config.model_id,
                        error=f"{type(exc).__name__}: {exc}",
                    ),
                )
        return

    try:
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                row = execute_agent_example(
                    agent,
                    example,
                    run_id=run_id,
                    config=config,
                    client=client,
                    token_tracker=token_tracker,
                    example_ref=example_ref,
                    recursion_limit=recursion_limit,
                    timeout_s=timeout_s,
                )
                append_log_row(handle, row)
    finally:
        client.close()


def run_agent_eval(
    *,
    models: str,
    eval_set_path: Path,
    run_id: str,
    models_config_path: Path | None = None,
    recursion_limit: int | None = None,
    timeout_s: float | None = None,
) -> Path:
    """Run eval set through the Deep Agents harness (same raw log layout as run_eval)."""
    configs = load_models_config(models_config_path)
    selected = resolve_model_names(models, configs)
    examples = read_eval_set_jsonl(eval_set_path)
    output_dir = run_raw_dir(run_id)

    for model_name in selected:
        run_model_agent_on_eval_set(
            configs[model_name],
            examples,
            run_id=run_id,
            output_path=output_dir / f"{model_name}.jsonl",
            recursion_limit=recursion_limit,
            timeout_s=timeout_s,
        )

    return output_dir
