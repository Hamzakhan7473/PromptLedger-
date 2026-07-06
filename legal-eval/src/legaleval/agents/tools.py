"""Extract and validate tools used by Deep Agents subagents."""

from __future__ import annotations

from legaleval.data.schema import EvalExample
from legaleval.models.prompt import SYSTEM_PROMPT, build_user_prompt
from legaleval.models.runner import ModelClient

EXTRACTOR_SYSTEM = """You are a legal clause extraction specialist.
Given a contract excerpt and clause category, draft a JSON prediction:
{"present": <bool>, "span": <string or null>, "confidence": <0-1>, "reasoning": <string>}

Rules:
- span must be an exact verbatim quote when present=true
- span must be null when present=false
- JSON only, no markdown"""

VALIDATOR_SYSTEM = """You are a legal extraction validator.
Review a draft clause extraction against the contract excerpt and category.
Return JSON only:
{
  "valid": <bool>,
  "issues": [<string>, ...],
  "revised": {"present": <bool>, "span": <string or null>, "confidence": <0-1>, "reasoning": <string>} | null
}

If valid=true, revised may be null. If valid=false, provide a corrected revised object."""


def _bound_example(example_ref: list[EvalExample]) -> EvalExample:
    if not example_ref:
        raise RuntimeError("No eval example is bound for agent clause tools")
    return example_ref[0]


def make_clause_tools(
    client: ModelClient,
    example_ref: list[EvalExample],
) -> tuple[object, object]:
    """Build extract/validate tools bound to a client and per-invoke example."""

    def extract_clause() -> str:
        """Draft clause presence and verbatim span from the bound contract excerpt."""
        example = _bound_example(example_ref)
        prompt = (
            f"{build_user_prompt(example)}\n\n"
            "Return your draft extraction as a single JSON object."
        )
        response = client.complete(prompt, EXTRACTOR_SYSTEM)
        return response.text

    def validate_extraction(draft_json: str) -> str:
        """Validate a draft extraction; return validation JSON with optional revision."""
        example = _bound_example(example_ref)
        prompt = f"""Contract title: {example.contract_title or "Contract"}
Clause category: {example.category}

Contract excerpt:
---
{example.contract_excerpt}
---

Draft extraction:
{draft_json}

Validate the draft. JSON only."""
        response = client.complete(prompt, VALIDATOR_SYSTEM)
        return response.text

    return extract_clause, validate_extraction
