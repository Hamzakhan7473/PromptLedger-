"""Judge prompt template and defensive JSON parsing."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, ValidationError

SYSTEM_PROMPT = """You are an expert legal annotator adjudicating span-level correctness.

You will receive a contract excerpt, a clause category, a gold reference span from CUAD,
and a model's predicted span. Both presence labels are already agreed (clause is present).

Your ONLY task: decide whether the predicted span correctly identifies the relevant clause
for the category — i.e. it captures the same substantive language as the gold span,
even if wording differs slightly.

Respond with JSON only. No markdown, no code fences, no prose outside the JSON object.

Required schema:
{
  "span_correct": <bool>,
  "rationale": <string>
}
"""

USER_PROMPT_TEMPLATE = """Clause category: {category}
Category definition: Language in the contract related to "{category}" that a lawyer should review.

Contract excerpt:
---
{contract_excerpt}
---

Gold reference span (CUAD annotation):
---
{gold_span}
---

Model predicted span:
---
{predicted_span}
---

Is the predicted span correct for this category? Return a single JSON object. JSON only."""


class JudgeDecision(BaseModel):
    span_correct: bool
    rationale: str


def build_judge_prompt(
    *,
    category: str,
    contract_excerpt: str,
    gold_span: str,
    predicted_span: str,
) -> str:
    return USER_PROMPT_TEMPLATE.format(
        category=category,
        contract_excerpt=contract_excerpt,
        gold_span=gold_span,
        predicted_span=predicted_span,
    )


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = _FENCE_RE.sub("", stripped).strip()
    if stripped.startswith("{"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_judge_response(raw_text: str) -> tuple[JudgeDecision | None, str | None]:
    """Parse judge output defensively. Returns (decision, parse_error)."""
    try:
        payload: Any = json.loads(_extract_json_object(raw_text))
        return JudgeDecision.model_validate(payload), None
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        return None, str(exc)
