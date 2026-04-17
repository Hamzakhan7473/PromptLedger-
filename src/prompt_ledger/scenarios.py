from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompt_ledger.load import read_yaml
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


def run_scenario_file(scenario_path: Path) -> ScenarioResult:
    raw = read_yaml(scenario_path)
    sid = raw["id"]
    prompt_id = raw["prompt_id"]
    version = str(raw["version"])
    variables: dict[str, Any] = dict(raw.get("variables", {}))
    fixture_rel = raw.get("fixture")
    expect = raw.get("expect") or {}

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
    if fixture_rel:
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

    golden = expect.get("golden_response")
    if golden:
        gpath = (root / golden).resolve()
        try:
            gpath.relative_to(root.resolve())
        except ValueError:
            return ScenarioResult(sid, False, [f"Illegal golden path: {golden}"])
        if gpath.exists():
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
