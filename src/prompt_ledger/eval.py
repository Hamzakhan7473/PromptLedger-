from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.manifest import get_pin, load_manifest
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.render import format_retrieved_context, render_prompt
from prompt_ledger.paths import repo_root


@dataclass(frozen=True)
class EvalResult:
    prompt_id: str
    version: str
    scenario_id: str
    ok: bool
    score: float | None
    detail: str
    raw_response: str | None = None


def _openai_complete(system: str, user: str) -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for semantic eval")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
    ).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"].strip()


def run_semantic_eval(
    scenario_path: Path,
    *,
    environment: str = "staging",
    judge: bool = True,
) -> EvalResult:
    from prompt_ledger.load import read_yaml
    from prompt_ledger.scenarios import _load_fixture

    raw = read_yaml(scenario_path)
    sid = raw["id"]
    prompt_id = raw["prompt_id"]
    version = raw.get("version")
    if raw.get("environment"):
        environment = str(raw["environment"])
    root = repo_root()
    manifest = load_manifest()
    if version is None:
        version = get_pin(manifest, environment, prompt_id)
        if not version:
            raise ValueError(f"no pin for {prompt_id!r} in {environment!r}")

    reg = discover_registry(root / "prompts" / "registry")
    pack = reg[prompt_id]
    pv = get_version(pack, str(version))

    retrieved: str | None = None
    if raw.get("graphrag_index"):
        from prompt_ledger.graphrag_bridge import context_from_index

        retrieved = context_from_index(
            (root / raw["graphrag_index"]).resolve(),
            question=raw.get("eval_question"),
        )
    elif raw.get("fixture"):
        chunks = _load_fixture((root / raw["fixture"]).resolve())
        retrieved = format_retrieved_context(chunks)
    elif raw.get("fixture") == "" or raw.get("empty_context"):
        retrieved = ""

    variables = dict(raw.get("variables", {}))
    system_s, user_s = render_prompt(pv, retrieved_context=retrieved, variables=variables)

    if not judge:
        return EvalResult(prompt_id, str(version), sid, True, None, "render-only", None)

    rubric = raw.get("eval_rubric") or (
        "Score 0-1 whether the assistant would correctly follow the prompt and context. "
        "Return JSON: {\"score\": number, \"passed\": boolean, \"reason\": string}"
    )
    judge_user = f"Rubric:\n{rubric}\n\nSystem:\n{system_s}\n\nUser:\n{user_s}"
    raw_out = _openai_complete(
        "You are an evaluation judge. Return only JSON.",
        judge_user,
    )
    try:
        payload = json.loads(raw_out)
        score = float(payload.get("score", 0))
        passed = bool(payload.get("passed", score >= 0.7))
        reason = str(payload.get("reason", ""))
    except (json.JSONDecodeError, TypeError, ValueError):
        passed = False
        score = 0.0
        reason = f"invalid judge JSON: {raw_out[:200]}"

    return EvalResult(
        prompt_id,
        str(version),
        sid,
        passed,
        score,
        reason,
        raw_out,
    )


def compare_versions(
    prompt_id: str,
    version_a: str,
    version_b: str,
    scenario_path: Path,
    *,
    environment: str = "staging",
) -> dict[str, Any]:
    """Run semantic eval twice with pinned versions (via temporary scenario overrides)."""

    from prompt_ledger.load import read_yaml

    base = read_yaml(scenario_path)
    root = repo_root()
    p = root / "tests" / "_eval_tmp_a.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    b = dict(base)
    b["version"] = version_a
    b["id"] = base["id"] + "_a"
    from prompt_ledger.load import write_yaml

    write_yaml(p, b)
    b2 = dict(base)
    b2["version"] = version_b
    b2["id"] = base["id"] + "_b"
    p2 = root / "tests" / "_eval_tmp_b.yaml"
    write_yaml(p2, b2)
    try:
        ra = run_semantic_eval(p, environment=environment)
        rb = run_semantic_eval(p2, environment=environment)
    finally:
        p.unlink(missing_ok=True)
        p2.unlink(missing_ok=True)

    return {
        "prompt_id": prompt_id,
        "version_a": version_a,
        "version_b": version_b,
        "result_a": ra,
        "result_b": rb,
        "winner": version_a
        if (ra.score or 0) > (rb.score or 0)
        else version_b
        if (rb.score or 0) > (ra.score or 0)
        else "tie",
    }
