"""Identify borderline span cases eligible for judge adjudication."""

from __future__ import annotations

from dataclasses import dataclass

from legaleval.metrics.compute import JoinedRow
from legaleval.metrics.span import best_gold_jaccard

DEFAULT_GRAY_LOW = 0.2
DEFAULT_GRAY_HIGH = 0.7


@dataclass(frozen=True)
class BorderlineCase:
    example_id: str
    category: str
    contract_excerpt: str
    contract_title: str
    gold_spans: list[str]
    predicted_span: str
    token_jaccard: float
    model: str


def primary_gold_span(gold_spans: list[str]) -> str:
    if not gold_spans:
        raise ValueError("Gold spans required for judge adjudication")
    return max(gold_spans, key=len)


def is_borderline_jaccard(
    jaccard: float,
    *,
    gray_low: float = DEFAULT_GRAY_LOW,
    gray_high: float = DEFAULT_GRAY_HIGH,
) -> bool:
    return gray_low <= jaccard <= gray_high


def borderline_cases_from_rows(
    rows: list[JoinedRow],
    *,
    gray_low: float = DEFAULT_GRAY_LOW,
    gray_high: float = DEFAULT_GRAY_HIGH,
) -> list[BorderlineCase]:
    """Return TP-presence rows whose token Jaccard falls in the gray zone."""
    cases: list[BorderlineCase] = []
    for row in rows:
        if row.pred_present is not True or row.gold_present is not True:
            continue
        if not row.pred_span or not row.gold_spans:
            continue
        jaccard = best_gold_jaccard(row.pred_span, row.gold_spans)
        if not is_borderline_jaccard(jaccard, gray_low=gray_low, gray_high=gray_high):
            continue
        cases.append(
            BorderlineCase(
                example_id=row.example_id,
                category=row.category,
                contract_excerpt=row.contract_excerpt,
                contract_title="",  # filled by caller if available
                gold_spans=list(row.gold_spans),
                predicted_span=row.pred_span,
                token_jaccard=round(jaccard, 6),
                model=row.model,
            )
        )
    return cases
