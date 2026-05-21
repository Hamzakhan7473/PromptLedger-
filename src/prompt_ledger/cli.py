from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from prompt_ledger.approval import (
    approve,
    decline,
    load_approval,
    request_approval,
)
from prompt_ledger.audit import run_audit
from prompt_ledger.diff import manifest_env_diff, prompt_text_diff, staging_production_prompt_diffs
from prompt_ledger.eval import compare_versions, run_semantic_eval
from prompt_ledger.evidence import build_evidence, export_evidence
from prompt_ledger.manifest import load_manifest, validate_manifest
from prompt_ledger.optimization import OptimizationEvent, emit_optimization_event
from prompt_ledger.packs import verify_pack
from prompt_ledger.paths import manifest_path, repo_root
from prompt_ledger.promote import promote_environment
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.render import format_retrieved_context, render_prompt
from prompt_ledger.review import emit_review_webhook
from prompt_ledger.scenarios import run_all_scenarios, run_scenario_file

app = typer.Typer(add_completion=False, no_args_is_help=True)
approval_app = typer.Typer(help="Promotion approval workflow")
pack_app = typer.Typer(help="Policy pack verification")
eval_app = typer.Typer(help="Semantic evaluation (requires OPENAI_API_KEY)")
app.add_typer(approval_app, name="approval")
app.add_typer(pack_app, name="pack")
app.add_typer(eval_app, name="eval")
console = Console()


def _emit_json(data: Any) -> None:
    typer.echo(json.dumps(data, indent=2, default=str))


def _has_errors(findings: list) -> bool:
    return any(getattr(f, "severity", "") == "error" for f in findings)


@app.command()
def audit(
    registry: Path | None = typer.Option(None, help="Registry root"),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output"),
) -> None:
    """Run static governance audits on all prompt packs and manifest pins."""

    root = repo_root()
    reg = registry or (root / "prompts" / "registry")
    findings = run_audit(registry_root=reg)
    if json_out:
        _emit_json({"passed": not _has_errors(findings), "findings": [asdict(f) for f in findings]})
        raise typer.Exit(0 if not _has_errors(findings) else 1)

    if not findings:
        console.print("[green]Audit passed: no findings.[/green]")
        raise typer.Exit(0)

    table = Table(title="Audit findings")
    table.add_column("Severity")
    table.add_column("Prompt")
    table.add_column("Version")
    table.add_column("Code")
    table.add_column("Message")
    for f in findings:
        table.add_row(f.severity, f.prompt_id, f.version, f.code, f.message)
    console.print(table)
    raise typer.Exit(1 if _has_errors(findings) else 0)


@app.command("validate-manifest")
def validate_manifest_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
    """Validate manifest environment pins against the prompt registry."""

    issues = validate_manifest()
    if json_out:
        _emit_json(
            {
                "passed": not _has_errors(issues),
                "issues": [asdict(i) for i in issues],
            },
        )
        raise typer.Exit(0 if not _has_errors(issues) else 1)
    if not issues:
        console.print("[green]Manifest valid.[/green]")
        raise typer.Exit(0)
    for i in issues:
        console.print(f"[red]{i.severity}[/red] {i.code}: {i.message}")
    raise typer.Exit(1)


@app.command()
def test(
    scenarios_dir: Path | None = typer.Option(None, help="Scenario YAML directory"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Run render/grounding scenarios (deterministic; no live LLM by default)."""

    root = repo_root()
    sdir = scenarios_dir or (root / "tests" / "scenarios")
    results = run_all_scenarios(sdir)
    if json_out:
        _emit_json(
            {
                "passed": all(r.ok for r in results),
                "results": [asdict(r) for r in results],
            },
        )
        raise typer.Exit(0 if all(r.ok for r in results) else 1)

    failed = [r for r in results if not r.ok]
    for r in results:
        if r.ok:
            console.print(f"[green]OK[/green]  {r.scenario_id}")
        else:
            console.print(f"[red]FAIL[/red] {r.scenario_id}")
            for err in r.errors:
                console.print(f"  - {err}")
    if failed:
        raise typer.Exit(1)
    console.print(f"[green]All {len(results)} scenario(s) passed.[/green]")


@app.command("test-one")
def test_one(
    scenario: Path = typer.Argument(..., exists=True, readable=True),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Run a single scenario file."""

    res = run_scenario_file(scenario)
    if json_out:
        _emit_json(asdict(res))
        raise typer.Exit(0 if res.ok else 1)
    if res.ok:
        console.print(f"[green]OK[/green] {res.scenario_id}")
        raise typer.Exit(0)
    console.print(f"[red]FAIL[/red] {res.scenario_id}")
    for err in res.errors:
        console.print(f"  - {err}")
    raise typer.Exit(1)


@app.command()
def render(
    prompt_id: str = typer.Option(..., "--prompt", "-p"),
    environment: str = typer.Option("staging", "--env", "-e"),
    fixture: Path | None = typer.Option(None, help="RAG fixture JSON path"),
    graphrag_index: Path | None = typer.Option(None, help="GraphRAG index JSON"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Render a prompt for an environment pin with optional context."""

    from prompt_ledger.graphrag_bridge import context_from_index
    from prompt_ledger.manifest import get_pin
    from prompt_ledger.scenarios import _load_fixture

    root = repo_root()
    manifest = load_manifest()
    ver = get_pin(manifest, environment, prompt_id)
    if not ver:
        console.print(f"[red]No pin for {prompt_id} in {environment}[/red]")
        raise typer.Exit(1)
    reg = discover_registry(root / "prompts" / "registry")
    pv = get_version(reg[prompt_id], ver)
    retrieved: str | None = None
    if graphrag_index:
        retrieved = context_from_index(graphrag_index.resolve())
    elif fixture:
        retrieved = format_retrieved_context(_load_fixture(fixture.resolve()))
    system_s, user_s = render_prompt(pv, retrieved_context=retrieved, variables={})
    payload = {
        "prompt_id": prompt_id,
        "version": ver,
        "environment": environment,
        "system": system_s,
        "user": user_s,
    }
    if json_out:
        _emit_json(payload)
        return
    console.print("[bold]system[/bold]")
    console.print(system_s)
    console.print("[bold]user[/bold]")
    console.print(user_s)


@app.command()
def diff(
    env_a: str = typer.Option("staging", "--env-a"),
    env_b: str = typer.Option("production", "--env-b"),
    prompt: str | None = typer.Option(None, "--prompt", help="Diff two versions for one prompt"),
    version_a: str | None = typer.Option(None),
    version_b: str | None = typer.Option(None),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Diff manifest pins or prompt text between versions."""

    if prompt and version_a and version_b:
        data = prompt_text_diff(prompt, version_a, version_b)
    else:
        data = {
            "manifest": manifest_env_diff(load_manifest(), env_a, env_b),
            "prompt_text_diffs": staging_production_prompt_diffs()
            if env_a == "staging" and env_b == "production"
            else [],
        }
    if json_out:
        _emit_json(data)
        return
    console.print_json(data=data)


@app.command()
def evidence(
    output: Path = typer.Option(..., "--output", "-o"),
    environment: str = typer.Option("production", "--env", "-e"),
    promoter: str | None = typer.Option(None, help="Who promoted (for audit trail)"),
    notify_review: bool = typer.Option(False, help="POST bundle to PROMPT_LEDGER_REVIEW_WEBHOOK_URL"),
) -> None:
    """Export audit + scenario + manifest evidence bundle (JSON)."""

    path = export_evidence(output, environment=environment, promoter=promoter)
    if notify_review:
        payload = build_evidence(environment=environment, promoter=promoter)
        emit_review_webhook(payload)
    console.print(f"[green]Wrote evidence[/green] {path}")


@app.command()
def promote(
    environment: str = typer.Option("production", "--environment", "-e"),
    sync_from: str | None = typer.Option("staging", "--sync-from"),
    manifest: Path | None = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
    require_approval: bool = typer.Option(False, "--require-approval"),
    set_prompt: list[str] = typer.Option(
        [],
        "--set",
        help="Set single pin: prompt_id=version (repeatable)",
    ),
    notify_optimization_api: bool = typer.Option(False),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Promote prompt pins (copy env, set pins, optional approval gate)."""

    set_pins: dict[str, str] = {}
    for item in set_prompt:
        if "=" not in item:
            raise typer.BadParameter(f"expected prompt_id=version, got {item!r}")
        pid, ver = item.split("=", 1)
        set_pins[pid.strip()] = ver.strip()

    after, diff = promote_environment(
        target=environment,
        sync_from=sync_from if sync_from and not set_pins else None,
        manifest=manifest,
        dry_run=dry_run,
        require_approval=require_approval,
        set_pins=set_pins or None,
    )
    if json_out:
        _emit_json({"dry_run": dry_run, "manifest": after, "diff": diff})
    else:
        console.print(f"[green]{'Would update' if dry_run else 'Updated'}[/green] {manifest or manifest_path()}")
        if diff and any(diff.get(k) for k in ("added", "removed", "changed")):
            console.print_json(data=diff)

    if not dry_run and notify_optimization_api:
        envs = after.get("environments", {})
        pins = envs.get(environment, {})
        for prompt_id, version in pins.items():
            emit_optimization_event(
                OptimizationEvent(
                    prompt_id=prompt_id,
                    version=str(version),
                    environment=environment,
                    metrics={"event": "promote", "sync_from": sync_from},
                ),
            )


@approval_app.command("request")
def approval_request(
    environment: str = typer.Option("production", "--environment", "-e"),
    sync_from: str = typer.Option("staging", "--sync-from"),
    by: str = typer.Option("unknown", "--by"),
) -> None:
    if by == "unknown":
        by = os.environ.get("USER", "unknown")
    rec = request_approval(
        target_environment=environment,
        sync_from=sync_from,
        requested_by=by,
    )
    console.print(f"[yellow]Pending approval[/yellow] for {rec.target_environment} <- {rec.sync_from}")


@approval_app.command("approve")
def approval_approve(
    by: str = typer.Option("unknown", "--by"),
    note: str | None = typer.Option(None),
) -> None:
    if by == "unknown":
        by = os.environ.get("USER", "unknown")
    rec = approve(approved_by=by, note=note)
    console.print(f"[green]Approved[/green] promotion to {rec.target_environment}")


@approval_app.command("decline")
def approval_decline(
    by: str = typer.Option("unknown", "--by"),
    note: str | None = typer.Option(None),
) -> None:
    if by == "unknown":
        by = os.environ.get("USER", "unknown")
    rec = decline(declined_by=by, note=note)
    console.print(f"[red]Declined[/red] promotion to {rec.target_environment}")


@approval_app.command("status")
def approval_status(json_out: bool = typer.Option(False, "--json")) -> None:
    rec = load_approval()
    if json_out:
        _emit_json(asdict(rec) if rec else {"status": "none"})
        return
    if not rec:
        console.print("No approval record.")
        return
    console.print_json(data=asdict(rec))


@pack_app.command("verify")
def pack_verify(
    pack_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    issues = verify_pack(pack_dir)
    if json_out:
        _emit_json({"passed": not _has_errors(issues), "issues": [asdict(i) for i in issues]})
        raise typer.Exit(0 if not _has_errors(issues) else 1)
    if not issues:
        console.print("[green]Pack verification passed.[/green]")
        raise typer.Exit(0)
    for i in issues:
        console.print(f"{i.severity}: {i.message}")
    raise typer.Exit(1 if _has_errors(issues) else 0)


@eval_app.command("run")
def eval_run(
    scenario: Path = typer.Argument(..., exists=True, readable=True),
    environment: str = typer.Option("staging", "--env", "-e"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Run semantic eval for one scenario (requires OPENAI_API_KEY)."""

    try:
        res = run_semantic_eval(scenario, environment=environment)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e
    if json_out:
        _emit_json(asdict(res))
        raise typer.Exit(0 if res.ok else 1)
    console.print(f"{'OK' if res.ok else 'FAIL'} score={res.score} {res.detail}")
    raise typer.Exit(0 if res.ok else 1)


@eval_app.command("compare")
def eval_compare(
    scenario: Path = typer.Argument(..., exists=True, readable=True),
    prompt_id: str = typer.Option(..., "--prompt", "-p"),
    version_a: str = typer.Option(..., "--version-a"),
    version_b: str = typer.Option(..., "--version-b"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    try:
        data = compare_versions(prompt_id, version_a, version_b, scenario)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e
    if json_out:
        _emit_json(
            {
                "winner": data["winner"],
                "result_a": asdict(data["result_a"]),
                "result_b": asdict(data["result_b"]),
            },
        )
        return
    console.print(f"Winner: {data['winner']}")
    console.print(f"A ({version_a}): {data['result_a'].score}")
    console.print(f"B ({version_b}): {data['result_b'].score}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
