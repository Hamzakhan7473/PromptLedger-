"""Run the judge on borderline span cases from a model eval run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from legaleval.data.cuad import read_eval_set_jsonl
from legaleval.judge.borderline import (
    DEFAULT_GRAY_HIGH,
    DEFAULT_GRAY_LOW,
    BorderlineCase,
    borderline_cases_from_rows,
    primary_gold_span,
)
from legaleval.judge.config import load_judge_config
from legaleval.judge.prompt import SYSTEM_PROMPT, build_judge_prompt, parse_judge_response
from legaleval.metrics.compute import join_run_with_gold, load_raw_run
from legaleval.models.runner import ModelClient, create_client
from legaleval.paths import run_judge_dir


class JudgeDecisionRow(BaseModel):
    run_id: str
    example_id: str
    evaluated_model: str
    category: str
    contract_title: str
    token_jaccard: float
    gold_span: str
    predicted_span: str
    judge_model_id: str
    judge_provider: str
    latency_ms: float | None = None
    span_correct: bool | None = None
    rationale: str | None = None
    raw_text: str | None = None
    parse_error: str | None = None
    error: str | None = None


def judge_results_dir(run_id: str) -> Path:
    return run_judge_dir(run_id)


def adjudicate_case(
    client: ModelClient,
    case: BorderlineCase,
    *,
    run_id: str,
    contract_title: str = "",
) -> JudgeDecisionRow:
    row = JudgeDecisionRow(
        run_id=run_id,
        example_id=case.example_id,
        evaluated_model=case.model,
        category=case.category,
        contract_title=contract_title,
        token_jaccard=case.token_jaccard,
        gold_span=primary_gold_span(case.gold_spans),
        predicted_span=case.predicted_span,
        judge_model_id=client.model_id,
        judge_provider=client.provider,
    )
    prompt = build_judge_prompt(
        category=case.category,
        contract_excerpt=case.contract_excerpt,
        gold_span=row.gold_span,
        predicted_span=case.predicted_span,
    )
    try:
        response = client.complete(prompt, SYSTEM_PROMPT)
    except Exception as exc:  # noqa: BLE001
        row.error = f"{type(exc).__name__}: {exc}"
        return row

    row.latency_ms = round(response.latency_ms, 2)
    row.raw_text = response.text
    decision, parse_error = parse_judge_response(response.text)
    if decision is not None:
        row.span_correct = decision.span_correct
        row.rationale = decision.rationale
    if parse_error is not None:
        row.parse_error = parse_error
    return row


def write_decisions(path: Path, rows: list[JudgeDecisionRow]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(row.model_dump_json() + "\n")
    return path


def run_adjudication(
    *,
    run_id: str,
    eval_set_path: Path,
    evaluated_model: str,
    gray_low: float = DEFAULT_GRAY_LOW,
    gray_high: float = DEFAULT_GRAY_HIGH,
    models_config_path: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[list[JudgeDecisionRow], Path]:
    gold_examples = read_eval_set_jsonl(eval_set_path)
    gold_by_id = {example.id: example for example in gold_examples}
    raw_by_model = load_raw_run(run_id)
    if evaluated_model not in raw_by_model:
        raise ValueError(
            f"Model {evaluated_model!r} not found in raw run {run_id}. "
            f"Available: {sorted(raw_by_model)}"
        )

    joined = join_run_with_gold({evaluated_model: raw_by_model[evaluated_model]}, gold_by_id)
    borderline = borderline_cases_from_rows(
        joined[evaluated_model], gray_low=gray_low, gray_high=gray_high
    )

    judge_config = load_judge_config(models_config_path)
    client = create_client(judge_config)
    decisions: list[JudgeDecisionRow] = []
    try:
        for case in borderline:
            title = gold_by_id[case.example_id].contract_title
            decisions.append(
                adjudicate_case(client, case, run_id=run_id, contract_title=title)
            )
    finally:
        client.close()

    out_dir = output_dir or judge_results_dir(run_id)
    output_path = out_dir / f"{evaluated_model}_decisions.jsonl"
    write_decisions(output_path, decisions)
    return decisions, output_path


def load_decisions(path: Path) -> list[JudgeDecisionRow]:
    rows: list[JudgeDecisionRow] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(JudgeDecisionRow.model_validate_json(line))
    return rows


def decisions_summary(decisions: list[JudgeDecisionRow]) -> dict[str, Any]:
    total = len(decisions)
    errors = sum(1 for row in decisions if row.error or row.parse_error)
    adjudicated = sum(1 for row in decisions if row.span_correct is not None)
    return {
        "total_borderline": total,
        "adjudicated": adjudicated,
        "errors": errors,
    }
