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


def context_from_index(
    index_path: Path,
    *,
    question: str | None = None,
    max_communities: int = 6,
) -> str:
    """Build retrieved_context text from a GraphRAG index JSON artifact."""

    data = json.loads(index_path.read_text(encoding="utf-8"))
    communities: list[dict[str, Any]] = data.get("communities") or []
    if not communities:
        chunks = data.get("chunks") or []
        if chunks:
            lines = []
            for ch in chunks[:20]:
                lines.append(str(ch.get("text", "")).strip())
            return "\n".join(lines).strip()
        return ""

    q_terms = _tokenize(question or "")

    def score(c: dict[str, Any]) -> int:
        text = str(c.get("summary", "")).lower()
        if not q_terms:
            return 1
        return sum(1 for t in q_terms if t in text)

    ranked = sorted(communities, key=score, reverse=True)
    if q_terms and ranked and score(ranked[0]) > 0:
        picked = [c for c in ranked if score(c) > 0][:max_communities]
    else:
        picked = ranked[:max_communities]

    parts: list[str] = []
    for i, c in enumerate(picked, 1):
        parts.append(f"[community-{i}] {str(c.get('summary', '')).strip()}")
    return "\n".join(parts).strip()
