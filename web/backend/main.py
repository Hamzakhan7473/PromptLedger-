"""PromptLedger control-plane API (wraps Python governance + optional GraphRAG index)."""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure repo root resolves when launched from web/backend
_REPO = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMPT_LEDGER_ROOT", str(_REPO))

from prompt_ledger.approval import load_approval  # noqa: E402
from prompt_ledger.audit import run_audit  # noqa: E402
from prompt_ledger.evidence import build_evidence  # noqa: E402
from prompt_ledger.manifest import load_manifest, validate_manifest  # noqa: E402
from prompt_ledger.paths import repo_root  # noqa: E402
from prompt_ledger.scenarios import run_all_scenarios  # noqa: E402

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
GRAPHRAG_INDEX = _REPO / ".data" / "graphrag-index.json"

app = FastAPI(title="PromptLedger API", version="0.1.0")
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


def _graphrag_binary() -> Path:
    return _REPO / "graphrag" / "cmd" / "graphrag"


def _run_graphrag(args: list[str], *, timeout: int = 300) -> tuple[int, str, str]:
    if not (_REPO / "graphrag" / "go.mod").is_file():
        return 1, "", "graphrag module not found"
    cmd = ["go", "run", "./cmd/graphrag", *args]
    proc = subprocess.run(
        cmd,
        cwd=_REPO / "graphrag",
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PROMPT_LEDGER_ROOT": str(_REPO)},
    )
    return proc.returncode, proc.stdout, proc.stderr


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "repo": str(repo_root())}


@app.get("/api/manifest")
def get_manifest() -> dict[str, Any]:
    return load_manifest()


@app.get("/api/audit")
def audit() -> dict[str, Any]:
    findings = run_audit()
    errors = [asdict(f) for f in findings if f.severity == "error"]
    warnings = [asdict(f) for f in findings if f.severity == "warning"]
    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "findings": [asdict(f) for f in findings],
    }


@app.get("/api/validate-manifest")
def api_validate_manifest() -> dict[str, Any]:
    issues = validate_manifest()
    errors = [asdict(i) for i in issues if i.severity == "error"]
    return {"passed": len(errors) == 0, "issues": [asdict(i) for i in issues]}


@app.get("/api/test")
def test_scenarios() -> dict[str, Any]:
    root = repo_root()
    results = run_all_scenarios(root / "tests" / "scenarios")
    return {
        "passed": all(r.ok for r in results),
        "results": [asdict(r) for r in results],
    }


@app.get("/api/evidence")
def evidence(environment: str = Query("staging")) -> dict[str, Any]:
    return build_evidence(environment=environment, promoter="web-ui")


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
        require_approval=False,
    )
    return {"dry_run": body.dry_run, "manifest": after, "diff": diff}


@app.post("/api/graphrag/index")
def graphrag_index() -> dict[str, Any]:
    """Build stub GraphRAG index from repo README (offline-friendly)."""
    GRAPHRAG_INDEX.parent.mkdir(parents=True, exist_ok=True)
    readme = _REPO / "README.md"
    if not readme.is_file():
        raise HTTPException(404, "README.md not found for demo index")
    code, out, err = _run_graphrag(
        ["index", "-text", str(readme), "-o", str(GRAPHRAG_INDEX), "-stub", "-algo", "labelprop"],
    )
    if code != 0:
        raise HTTPException(500, detail=err or out)
    return {"path": str(GRAPHRAG_INDEX), "stdout": out.strip()}


@app.get("/api/graphrag/context")
def graphrag_context(question: str = Query("")) -> dict[str, str]:
    if not GRAPHRAG_INDEX.is_file():
        raise HTTPException(404, "index missing; POST /api/graphrag/index first")
    from prompt_ledger.graphrag_bridge import context_from_index

    return {"retrieved_context": context_from_index(GRAPHRAG_INDEX, question=question)}


@app.post("/api/graphrag/query")
def graphrag_query(body: GraphRAGQueryBody) -> dict[str, Any]:
    if not GRAPHRAG_INDEX.is_file():
        raise HTTPException(404, "index missing; POST /api/graphrag/index first")
    code, out, err = _run_graphrag(
        ["query", "-index", str(GRAPHRAG_INDEX), "-question", body.question, "-stub", "-json"],
        timeout=120,
    )
    if code != 0:
        raise HTTPException(500, detail=err or out)
    import json

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"final": out.strip(), "raw": out}


@app.get("/")
def index_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
