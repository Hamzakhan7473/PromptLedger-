"""Enriched eval rows joining raw logs with gold labels and model metadata."""

from __future__ import annotations

from dataclasses import dataclass

from legaleval.data.cuad import EvalExample
from legaleval.metrics.compute import JoinedRow, join_row
from legaleval.models.runner import CallLogRow


@dataclass(frozen=True)
class EnrichedRow:
    example_id: str
    category: str
    contract_title: str
    model: str
    contract_excerpt: str
    gold_present: bool
    gold_spans: list[str]
    pred_present: bool | None
    pred_span: str | None
    confidence: float | None
    reasoning: str | None
    has_api_error: bool
    has_parse_error: bool
    parse_error: str | None
    api_error: str | None
    raw_text: str | None

    @classmethod
    def from_log(cls, log: CallLogRow, gold: EvalExample) -> EnrichedRow:
        joined = join_row(log, gold)
        confidence: float | None = None
        reasoning: str | None = None
        if log.parsed is not None:
            raw_conf = log.parsed.get("confidence")
            if raw_conf is not None:
                confidence = float(raw_conf)
            reasoning = log.parsed.get("reasoning")
        return cls(
            example_id=joined.example_id,
            category=joined.category,
            contract_title=gold.contract_title,
            model=joined.model,
            contract_excerpt=joined.contract_excerpt,
            gold_present=joined.gold_present,
            gold_spans=joined.gold_spans,
            pred_present=joined.pred_present,
            pred_span=joined.pred_span,
            confidence=confidence,
            reasoning=reasoning,
            has_api_error=joined.has_api_error,
            has_parse_error=joined.has_parse_error,
            parse_error=log.parse_error,
            api_error=log.error,
            raw_text=log.raw_text,
        )


def enrich_run(
    raw_by_model: dict[str, list[CallLogRow]],
    gold_by_id: dict[str, EvalExample],
) -> dict[str, list[EnrichedRow]]:
    enriched: dict[str, list[EnrichedRow]] = {}
    for model_name, logs in raw_by_model.items():
        enriched[model_name] = []
        for log in logs:
            gold = gold_by_id[log.example_id]
            enriched[model_name].append(EnrichedRow.from_log(log, gold))
    return enriched
