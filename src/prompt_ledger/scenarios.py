from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml
from prompt_ledger.manifest import get_pin, load_manifest
from prompt_ledger.paths import repo_root
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.render import (
    assert_no_unresolved_placeholders,
    format_retrieved_context,
    render_prompt,
)


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    ok: bool
    errors: list[str]


def _load_fixture(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError(f"Fixture {path} must contain a chunks array")
    return chunks


def resolve_version(raw: dict[str, Any], prompt_id: str) -> str:
    if raw.get("version"):
        return str(raw["version"])
    env = str(raw.get("environment", "staging"))
    manifest = load_manifest()
    ver = get_pin(manifest, env, prompt_id)
    if not ver:
        raise ValueError(f"no manifest pin for {prompt_id!r} in {env!r}")
    return ver


def run_scenario_file(scenario_path: Path) -> ScenarioResult:
    raw = read_yaml(scenario_path)
    sid = raw["id"]
    prompt_id = raw["prompt_id"]
    try:
        version = resolve_version(raw, prompt_id)
    except ValueError as e:
        return ScenarioResult(sid, False, [str(e)])

    variables: dict[str, Any] = dict(raw.get("variables", {}))
    fixture_rel = raw.get("fixture")
    expect = raw.get("expect") or {}
    require_golden = bool(raw.get("require_golden", expect.get("require_golden")))

    root = repo_root()
    registry = discover_registry(root / "prompts" / "registry")
    if prompt_id not in registry:
        return ScenarioResult(sid, False, [f"Unknown prompt_id {prompt_id!r}"])
    pack = registry[prompt_id]
    try:
        pv = get_version(pack, version)
    except KeyError as e:
        return ScenarioResult(sid, False, [str(e)])

    retrieved: str | None = None
    if raw.get("empty_context"):
        retrieved = ""
    elif raw.get("graphrag_index"):
        from prompt_ledger.graphrag_bridge import context_from_index

        gpath = (root / raw["graphrag_index"]).resolve()
        try:
            gpath.relative_to(root.resolve())
        except ValueError:
            return ScenarioResult(sid, False, [f"Illegal graphrag_index path: {raw['graphrag_index']}"])
        retrieved = context_from_index(gpath, question=raw.get("question"))
    elif fixture_rel is not None:
        if fixture_rel == "":
            retrieved = ""
        else:
            fx = (root / fixture_rel).resolve()
            try:
                fx.relative_to(root.resolve())
            except ValueError:
                return ScenarioResult(sid, False, [f"Illegal fixture path: {fixture_rel}"])
            chunks = _load_fixture(fx)
            retrieved = format_retrieved_context(chunks)

    errors: list[str] = []
    try:
        system_s, user_s = render_prompt(pv, retrieved_context=retrieved, variables=variables)
        assert_no_unresolved_placeholders(system_s, user_s)
    except Exception as e:
        return ScenarioResult(sid, False, [f"Render failed: {e}"])

    combined = f"{system_s}\n{user_s}"

    for needle in expect.get("rendered_contains", []):
        if needle not in combined:
            errors.append(f"Expected rendered text to contain {needle!r}")

    for needle in expect.get("rendered_contains_after_substitution", []):
        if needle not in combined:
            errors.append(f"Expected rendered text to contain {needle!r}")

    for needle in expect.get("rendered_must_not_contain", []):
        if needle in combined:
            errors.append(f"Expected rendered text NOT to contain {needle!r}")

    if raw.get("empty_context") or expect.get("must_refuse_without_context"):
        refuse_any = expect.get("refuse_markers") or [
            "insufficient",
            "not provided",
            "cannot answer",
            "do not have",
            "refuse",
        ]
        if not any(m.lower() in combined.lower() for m in refuse_any):
            errors.append("Expected refusal language when context is empty")

    golden = expect.get("golden_response") or raw.get("golden_response")
    if require_golden and not golden:
        errors.append("require_golden is set but no golden_response path provided")
    if golden:
        gpath = (root / golden).resolve()
        try:
            gpath.relative_to(root.resolve())
        except ValueError:
            return ScenarioResult(sid, False, [f"Illegal golden path: {golden}"])
        if not gpath.exists():
            errors.append(f"Golden response file not found: {golden}")
        else:
            payload = json.loads(gpath.read_text(encoding="utf-8"))
            schema_rel = pv.output_schema
            if schema_rel:
                import jsonschema

                schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))
                try:
                    jsonschema.validate(payload, schema)
                except jsonschema.ValidationError as ve:
                    errors.append(f"Golden response invalid vs schema: {ve.message}")

    return ScenarioResult(sid, len(errors) == 0, errors)


def run_all_scenarios(scenario_dir: Path) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    for path in sorted(scenario_dir.glob("*.yaml")):
        results.append(run_scenario_file(path))
    return results
