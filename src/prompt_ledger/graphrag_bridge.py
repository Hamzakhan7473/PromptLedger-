from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _tokenize(s: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{3,}", s.lower())
    stop = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "what",
        "how", "why", "who", "when", "this", "that", "with", "from",
    }
    return {w for w in words if w not in stop}


def _entity_names(data: dict[str, Any]) -> dict[str, str]:
    return {str(e["id"]): str(e.get("name", "")) for e in data.get("entities") or []}


def context_from_index(
    index_path: Path,
    *,
    question: str | None = None,
    max_communities: int = 10,
) -> str:
    """Build {retrieved_context} text from a GraphRAG index JSON (matches Go contextfmt.ForPrompt)."""

    data = json.loads(index_path.read_text(encoding="utf-8"))
    communities: list[dict[str, Any]] = data.get("communities") or []
    if not communities:
        chunks = data.get("chunks") or []
        if chunks:
            lines = [str(ch.get("text", "")).strip() for ch in chunks[:20]]
            return "\n".join(lines).strip()
        return ""

    names = _entity_names(data)
    q_terms = _tokenize(question or "")

    def score(c: dict[str, Any]) -> int:
        text = str(c.get("summary", "")).lower()
        for mid in c.get("member_ids") or []:
            text += " " + str(names.get(mid, "")).lower()
        if not q_terms:
            return 1
        return sum(1 for t in q_terms if t in text) + (1 if c.get("level") == 1 else 0)

    ranked = sorted(communities, key=score, reverse=True)
    max_s = score(ranked[0]) if ranked else 0
    if max_s == 0:
        picked = communities[:max_communities]
    else:
        thresh = max(1, (max_s + 1) // 2)
        picked = [c for c in ranked if score(c) >= thresh][:max_communities]

    parts: list[str] = []
    for c in picked:
        cid = str(c.get("id", "?"))
        parts.append(f"[{cid}] {str(c.get('summary', '')).strip()}")
    return "\n".join(parts).strip()
