"""Synthetic CUAD fixture for unit tests (no network download)."""

from __future__ import annotations

QUESTION_TEMPLATE = (
    'Highlight the parts (if any) of this contract related to "{category}" '
    "that should be reviewed by a lawyer."
)

CATEGORIES = ("Cap On Liability", "Anti-Assignment", "Audit Rights")
SPANS = {
    "Cap On Liability": "liability cap is one million dollars",
    "Anti-Assignment": "Assignment requires consent",
    "Audit Rights": "Audits may occur annually",
}


def _qa(category: str, *, present: bool, context: str) -> dict:
    if present:
        span = SPANS[category]
        start = context.index(span)
        return {
            "question": QUESTION_TEMPLATE.format(category=category),
            "is_impossible": False,
            "answers": [{"text": span, "answer_start": start}],
        }
    return {
        "question": QUESTION_TEMPLATE.format(category=category),
        "is_impossible": True,
        "answers": [],
    }


def _contract(title: str, context: str, qas: list[dict]) -> dict:
    return {
        "title": title,
        "paragraphs": [{"context": context, "qas": qas}],
    }


def make_synthetic_cuad(*, n_contracts: int = 9) -> dict:
    """Build a small CUAD JSON with balanced present/absent pools per category."""
    contracts: list[dict] = []
    for contract_idx in range(n_contracts):
        padding = "x" * 500
        context = (
            f"{padding} The liability cap is one million dollars. "
            f"{padding} Assignment requires consent. "
            f"{padding} Audits may occur annually. "
            f"{padding}"
        )
        qas = [
            _qa(
                category,
                present=contract_idx % len(CATEGORIES) != cat_idx,
                context=context,
            )
            for cat_idx, category in enumerate(CATEGORIES)
        ]
        contracts.append(_contract(f"Contract-{contract_idx}", context, qas))
    return {"data": contracts}
