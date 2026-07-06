"""Eval prompt template and defensive JSON parsing."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from legaleval.data.schema import EvalExample

SYSTEM_PROMPT = """You are a legal contract analyst. Your task is to determine whether a specific \
clause category is present in a contract excerpt.

Respond with JSON only. No markdown, no code fences, no prose outside the JSON object.

Required schema:
{
  "present": <bool>,
  "span": <string or null>,
  "confidence": <float between 0 and 1>,
  "reasoning": <string>
}

Rules:
- "present" is true only if the category is substantively addressed in the excerpt.
- "span" must be an exact verbatim quote from the excerpt when present=true; null when present=false.
- "confidence" reflects how certain you are (0.0 = guess, 1.0 = certain).
- "reasoning" is a brief justification (1-3 sentences).
"""

USER_PROMPT_TEMPLATE = """Contract title: {contract_title}
Clause category: {category}

Contract excerpt:
---
{contract_excerpt}
---

Does this excerpt contain language related to "{category}"?
Return a single JSON object matching the required schema. JSON only."""


class ModelPrediction(BaseModel):
    present: bool
    span: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


def build_user_prompt(example: EvalExample) -> str:
    return USER_PROMPT_TEMPLATE.format(
        contract_title=example.contract_title,
        category=example.category,
        contract_excerpt=example.contract_excerpt,
    )


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = _FENCE_RE.sub("", stripped).strip()
    return stripped


def _extract_json_object(text: str) -> str:
    stripped = _strip_code_fences(text)
    if stripped.startswith("{"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_model_response(raw_text: str) -> tuple[ModelPrediction | None, str | None]:
    """Parse model output defensively. Returns (prediction, parse_error)."""
    try:
        payload: Any = json.loads(_extract_json_object(raw_text))
        prediction = ModelPrediction.model_validate(payload)
        if prediction.present and not prediction.span:
            return None, "present=true requires a non-null span"
        if not prediction.present and prediction.span:
            return None, "present=false requires span=null"
        return prediction, None
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        return None, str(exc)
