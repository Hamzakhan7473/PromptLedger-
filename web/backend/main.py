"""PromptLedger control-plane API (wraps Python governance + multi-vertical demo)."""

from __future__ import annotations

import os
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

_REPO = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMPT_LEDGER_ROOT", str(_REPO))

from prompt_ledger.approval import load_approval  # noqa: E402
from prompt_ledger.audit import run_audit  # noqa: E402
from prompt_ledger.demo import (  # noqa: E402
    build_graphrag_index,
    list_verticals,
    load_demo_config,
    render_vertical_preview,
    run_vertical_demo,
)
from prompt_ledger.evidence import build_evidence  # noqa: E402
from prompt_ledger.graphrag_cli import resolve_graphrag_invocation  # noqa: E402
from prompt_ledger.manifest import load_manifest, validate_manifest  # noqa: E402
from prompt_ledger.paths import repo_root  # noqa: E402
from prompt_ledger.platform.dataset import build_rl_datasets  # noqa: E402
from prompt_ledger.platform.environments import list_environments  # noqa: E402
from prompt_ledger.platform.evaluation import evaluate_trajectories  # noqa: E402
from prompt_ledger.platform.observability import observability_stack  # noqa: E402
from prompt_ledger.platform.orchestrator import run_agent_task  # noqa: E402
from prompt_ledger.platform.router import list_models  # noqa: E402
from prompt_ledger.platform.tools import list_tools  # noqa: E402
from prompt_ledger.platform.trajectory_store import get_trajectory, list_trajectories  # noqa: E402
from prompt_ledger.scenarios import run_all_scenarios  # noqa: E402

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
GRAPHRAG_INDEX = _REPO / ".data" / "graphrag-index.json"

app = FastAPI(title="PromptLedger API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromoteBody(BaseModel):
    environment: str = "production"
    sync_from: str = "staging"
    dry_run: bool = True


class GraphRAGQueryBody(BaseModel):
    question: str


class AgentRunBody(BaseModel):
    environment: str
    task: str
    cost_sensitive: bool = False


def _run_graphrag(args: list[str], *, timeout: int = 300) -> tuple[int, str, str]:
    try:
        cmd, cwd = resolve_graphrag_invocation(args)
    except FileNotFoundError as e:
        return 1, "", str(e)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PROMPT_LEDGER_ROOT": str(_REPO)},
    )
    return proc.returncode, proc.stdout, proc.stderr


@app.get("/api/health")
def health() -> dict[str, Any]:
    verticals = list_verticals()
    return {
        "status": "ok",
        "repo": str(repo_root()),
        "mode": "demo",
        "verticals": len(verticals),
        "vertical_ids": [v["id"] for v in verticals],
        "docs": "/docs",
    }


@app.get("/api/agent/environments")
def api_agent_environments() -> dict[str, Any]:
    return {"environments": list_environments()}


@app.get("/api/agent/tools")
def api_agent_tools() -> dict[str, Any]:
    return {"tools": list_tools()}


@app.get("/api/agent/models")
def api_agent_models() -> dict[str, Any]:
    return {"models": list_models()}


@app.get("/api/agent/trajectories")
def api_agent_trajectories(
    environment: str | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
) -> dict[str, Any]:
    return {"trajectories": list_trajectories(environment=environment, limit=limit)}


@app.get("/api/agent/trajectories/{trajectory_id}")
def api_agent_trajectory(trajectory_id: str) -> dict[str, Any]:
    data = get_trajectory(trajectory_id)
    if not data:
        raise HTTPException(404, "trajectory not found")
    return data


@app.post("/api/agent/run")
def api_agent_run(body: AgentRunBody) -> dict[str, Any]:
    try:
        return run_agent_task(
            body.environment,
            body.task,
            cost_sensitive=body.cost_sensitive,
        )
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/api/agent/evaluate")
def api_agent_evaluate(environment: str | None = Query(None)) -> dict[str, Any]:
    return evaluate_trajectories(environment=environment)


@app.post("/api/agent/datasets")
def api_agent_datasets(environment: str | None = Query(None)) -> dict[str, Any]:
    return build_rl_datasets(environment=environment)


@app.get("/api/agent/observability")
def api_agent_observability() -> dict[str, Any]:
    return observability_stack()


@app.get("/api/demo/verticals")
def api_demo_verticals() -> dict[str, Any]:
    return {"verticals": list_verticals()}


@app.get("/api/demo/vertical/{vertical_id}")
def api_demo_vertical(vertical_id: str) -> dict[str, Any]:
    cfg = load_demo_config()
    if vertical_id not in cfg:
        raise HTTPException(404, f"unknown vertical {vertical_id}")
    v = cfg[vertical_id]
    return {
        "id": vertical_id,
        "label": v.label,
        "headline": v.headline,
        "description": v.description,
        "accent": v.accent,
        "icon": v.icon,
        "checks": v.checks,
        "prompt_id": v.prompt_id,
        "preview": render_vertical_preview(v),
    }


@app.post("/api/demo/run/{vertical_id}")
def api_demo_run(vertical_id: str) -> dict[str, Any]:
    try:
        return run_vertical_demo(vertical_id)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e
    except Exception as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/demo/graphrag/{vertical_id}")
def api_demo_graphrag_index(vertical_id: str) -> dict[str, Any]:
    try:
        return build_graphrag_index(vertical_id)
    except (KeyError, FileNotFoundError) as e:
        raise HTTPException(404, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.get("/api/manifest")
def get_manifest() -> dict[str, Any]:
    return load_manifest()


@app.get("/api/audit")
def audit() -> dict[str, Any]:
    findings = run_audit()
    errors = [asdict(f) for f in findings if f.severity == "error"]
    return {"passed": len(errors) == 0, "findings": [asdict(f) for f in findings]}


@app.get("/api/validate-manifest")
def api_validate_manifest() -> dict[str, Any]:
    issues = validate_manifest()
    return {"passed": not any(i.severity == "error" for i in issues), "issues": [asdict(i) for i in issues]}


@app.get("/api/test")
def test_scenarios() -> dict[str, Any]:
    results = run_all_scenarios(repo_root() / "tests" / "scenarios")
    return {"passed": all(r.ok for r in results), "results": [asdict(r) for r in results]}


@app.get("/api/evidence")
def evidence(environment: str = Query("staging")) -> dict[str, Any]:
    return build_evidence(environment=environment, promoter="demo-ui")


@app.get("/api/approval")
def approval_status() -> dict[str, Any]:
    rec = load_approval()
    return {"record": asdict(rec) if rec else None}


@app.post("/api/promote")
def promote(body: PromoteBody) -> dict[str, Any]:
    from prompt_ledger.promote import promote_environment

    after, diff = promote_environment(
        target=body.environment,
        sync_from=body.sync_from,
        dry_run=body.dry_run,
    )
    return {"dry_run": body.dry_run, "manifest": after, "diff": diff}


@app.post("/api/graphrag/index")
def graphrag_index() -> dict[str, Any]:
    GRAPHRAG_INDEX.parent.mkdir(parents=True, exist_ok=True)
    readme = _REPO / "README.md"
    code, out, err = _run_graphrag(
        ["index", "-text", str(readme), "-o", str(GRAPHRAG_INDEX), "-stub", "-algo", "labelprop"],
    )
    if code != 0:
        raise HTTPException(500, detail=err or out)
    return {"path": str(GRAPHRAG_INDEX), "stdout": out.strip()}


@app.get("/")
def index_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
