from __future__ import annotations

import json
import re
from typing import Any

from prompt_ledger.registry import PromptVersion


def format_retrieved_context(chunks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for chunk in chunks:
        cid = str(chunk.get("id", "?"))
        text = str(chunk.get("text", "")).strip()
        lines.append(f"[{cid}] {text}")
    return "\n".join(lines).strip()


def render_prompt(
    pv: PromptVersion,
    *,
    retrieved_context: str | None,
    variables: dict[str, Any],
) -> tuple[str, str]:
    """Return (system, user) after substitution."""

    values: dict[str, Any] = dict(variables)
    if "retrieved_context" in pv.variables:
        if retrieved_context is None:
            raise ValueError("retrieved_context is required for this prompt version")
        values.setdefault("retrieved_context", retrieved_context)

    def subst(template: str) -> str:
        out = template
        for key, val in values.items():
            token = "{" + key + "}"
            if token not in out:
                continue
            if isinstance(val, (dict, list)):
                out = out.replace(token, json.dumps(val, ensure_ascii=False))
            else:
                out = out.replace(token, str(val))
        return out

    for key in pv.variables:
        if key not in values:
            raise ValueError(f"Missing variable {key!r}")

    system_s = subst(pv.system)
    user_s = subst(pv.user)
    return system_s, user_s


_UNRESOLVED = re.compile(r"\{[a-zA-Z0-9_.]+\}")


def assert_no_unresolved_placeholders(system: str, user: str) -> None:
    text = system + "\n" + user
    found = _UNRESOLVED.findall(text)
    if found:
        raise ValueError(f"Unresolved placeholders remain: {sorted(set(found))}")
