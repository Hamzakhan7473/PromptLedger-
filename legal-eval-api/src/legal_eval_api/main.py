"""FastAPI application."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response

from legaleval.paths import run_report_path

from legal_eval_api.artifacts import load_run_artifacts_bundle, resolve_artifact_file
from legal_eval_api.audit import get_audit_log
from legal_eval_api.auth import AuthContext, get_current_org, run_access
from legal_eval_api.config import API_HOST, API_PORT, CORS_ORIGINS
from legal_eval_api.datasets import (
    get_dataset,
    get_document_template_path,
    ingest_dataset,
    ingest_documents,
    ingest_hf_dataset,
    list_adapters,
    list_datasets,
    model_catalog,
)
from legal_eval_api.demo_seed import public_demo_link, seed_public_demo_run
from legal_eval_api.db import init_db
from legal_eval_api.enterprise import get_enterprise_settings, update_enterprise_settings
from legal_eval_api.export_pdf import load_run_report_pdf
from legal_eval_api.jobs import create_run, get_run, list_runs
from legal_eval_api.orgs import (
    ensure_default_org,
    get_profile,
    get_secrets_status,
    register_org,
    update_models,
    update_secrets,
)
from legal_eval_api.schemas import (
    AdapterCatalogEntry,
    AuditEvent,
    CreateOrgRequest,
    CreateOrgResponse,
    CreateRunRequest,
    DatasetImportResponse,
    DatasetSummary,
    DocumentImportResponse,
    EnterpriseSettings,
    HuggingFaceImportRequest,
    OrgProfile,
    OrgSecretsStatus,
    OrgStats,
    RunDetail,
    RunSummary,
    ShareLinkResponse,
    UpdateEnterpriseSettingsRequest,
    UpdateOrgModelsRequest,
    UpdateOrgSecretsRequest,
)
from legal_eval_api.setup import local_setup_status
from legal_eval_api.sharing import create_share_link
from legal_eval_api.stats import compute_org_stats
from legal_eval_api.storage import ensure_dirs

app = FastAPI(
    title="legal-eval API",
    description="Upload legal eval datasets, route to frontier models, run the eval pipeline.",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    ensure_dirs()
    init_db()
    ensure_default_org()
    seed_public_demo_run()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/demo")
def api_public_demo() -> dict[str, object]:
    """Public demo run link (read-only via share token)."""
    link = public_demo_link()
    if link is None:
        return {"available": False}
    return {"available": True, **link}


@app.get("/api/v1/setup")
def api_setup() -> dict[str, object]:
    """Whether local model keys are loaded (from legal-eval/.env)."""
    return local_setup_status()


# --- Organizations (Phase 2) ---


@app.post("/api/v1/orgs", response_model=CreateOrgResponse)
def api_create_org(request: CreateOrgRequest) -> CreateOrgResponse:
    return register_org(request)


@app.get("/api/v1/orgs/me", response_model=OrgProfile)
def api_org_profile(org: Annotated[AuthContext, Depends(get_current_org)]) -> OrgProfile:
    return get_profile(org.org_id)


@app.put("/api/v1/orgs/me/secrets", response_model=OrgSecretsStatus)
def api_update_secrets(
    request: UpdateOrgSecretsRequest,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> OrgSecretsStatus:
    return update_secrets(org.org_id, request)


@app.get("/api/v1/orgs/me/secrets", response_model=OrgSecretsStatus)
def api_secrets_status(
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> OrgSecretsStatus:
    return get_secrets_status(org.org_id)


@app.put("/api/v1/orgs/me/models", response_model=OrgProfile)
def api_update_models(
    request: UpdateOrgModelsRequest,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> OrgProfile:
    return update_models(org.org_id, request)


# --- Enterprise (Phase 4) ---


@app.get("/api/v1/orgs/me/settings", response_model=EnterpriseSettings)
def api_enterprise_settings(
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> EnterpriseSettings:
    return get_enterprise_settings(org.org_id)


@app.put("/api/v1/orgs/me/settings", response_model=EnterpriseSettings)
def api_update_enterprise_settings(
    request: UpdateEnterpriseSettingsRequest,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> EnterpriseSettings:
    return update_enterprise_settings(org.org_id, request)


@app.get("/api/v1/orgs/me/stats", response_model=OrgStats)
def api_org_stats(
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> OrgStats:
    return compute_org_stats(org.org_id)


@app.get("/api/v1/orgs/me/audit", response_model=list[AuditEvent])
def api_audit_log(
    org: Annotated[AuthContext, Depends(get_current_org)],
    limit: int = 100,
) -> list[AuditEvent]:
    events = get_audit_log(org.org_id, limit=min(limit, 500))
    return [AuditEvent(**event) for event in events]


# --- Models catalog (public) ---


@app.get("/api/v1/models")
def api_models():
    return {"models": model_catalog()}


# --- Datasets (org-scoped) ---


@app.get("/api/v1/datasets", response_model=list[DatasetSummary])
def api_list_datasets(
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> list[DatasetSummary]:
    return list_datasets(org.org_id)


@app.post("/api/v1/datasets", response_model=DatasetSummary)
async def api_upload_dataset(
    org: Annotated[AuthContext, Depends(get_current_org)],
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
) -> DatasetSummary:
    return await ingest_dataset(file, org_id=org.org_id, name=name)


@app.get("/api/v1/datasets/adapters", response_model=list[AdapterCatalogEntry])
def api_list_dataset_adapters() -> list[AdapterCatalogEntry]:
    return list_adapters()


@app.post("/api/v1/datasets/import/huggingface", response_model=DatasetImportResponse)
async def api_import_huggingface_dataset(
    request: HuggingFaceImportRequest,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> DatasetImportResponse:
    return await ingest_hf_dataset(request, org_id=org.org_id)


@app.post("/api/v1/datasets/import/documents", response_model=DocumentImportResponse)
async def api_import_documents(
    org: Annotated[AuthContext, Depends(get_current_org)],
    files: list[UploadFile] = File(...),
) -> DocumentImportResponse:
    return await ingest_documents(files, org_id=org.org_id)


@app.get("/api/v1/datasets/import/documents/{staging_id}/template.jsonl")
def api_download_document_template(
    staging_id: str,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> FileResponse:
    template_path, filename = get_document_template_path(staging_id, org.org_id)
    return FileResponse(
        path=template_path,
        media_type="application/x-ndjson",
        filename=filename,
    )


@app.get("/api/v1/datasets/{dataset_id}", response_model=DatasetSummary)
def api_get_dataset(
    dataset_id: str,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> DatasetSummary:
    return get_dataset(dataset_id, org.org_id)


# --- Runs (org-scoped + share token) ---


@app.get("/api/v1/runs", response_model=list[RunSummary])
def api_list_runs(
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> list[RunSummary]:
    return list_runs(org.org_id)


@app.post("/api/v1/runs", response_model=RunSummary)
def api_create_run(
    request: CreateRunRequest,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> RunSummary:
    return create_run(org.org_id, request)


@app.get("/api/v1/runs/{run_id}", response_model=RunDetail)
def api_get_run(
    run_id: str,
    org: Annotated[AuthContext, Depends(run_access)],
) -> RunDetail:
    return get_run(run_id, org.org_id)


@app.post("/api/v1/runs/{run_id}/share", response_model=ShareLinkResponse)
def api_share_run(
    run_id: str,
    org: Annotated[AuthContext, Depends(get_current_org)],
) -> ShareLinkResponse:
    link = create_share_link(org.org_id, run_id)
    from legal_eval_api.storage import read_json, run_meta_path, write_json

    meta = read_json(run_meta_path(run_id))
    meta["share_token"] = link.token
    write_json(run_meta_path(run_id), meta)
    return link


@app.get("/api/v1/runs/{run_id}/artifacts")
def api_run_artifacts(
    run_id: str,
    org: Annotated[AuthContext, Depends(run_access)],
) -> dict[str, object]:
    """JSON bundle for UI run views (summary, grid, samples)."""
    return load_run_artifacts_bundle(run_id)


@app.get("/api/v1/runs/{run_id}/artifacts/files/{file_path:path}")
def api_run_artifact_file(
    run_id: str,
    file_path: str,
    org: Annotated[AuthContext, Depends(run_access)],
) -> FileResponse:
    """Serve a single artifact file (e.g. calibration PNG). Storage backend swappable in artifacts.py."""
    path, media_type = resolve_artifact_file(run_id, file_path)
    return FileResponse(path, media_type=media_type)


@app.get("/api/v1/runs/{run_id}/report")
def api_run_report(
    run_id: str,
    org: Annotated[AuthContext, Depends(run_access)],
) -> PlainTextResponse:
    detail = get_run(run_id, org.org_id)
    if detail.status != "completed":
        return PlainTextResponse("Run not complete.", status_code=409)
    path = run_report_path(run_id)
    if not path.exists():
        return PlainTextResponse("Report not found.", status_code=404)
    return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="text/markdown")


@app.get("/api/v1/runs/{run_id}/export.pdf")
def api_run_export_pdf(
    run_id: str,
    org: Annotated[AuthContext, Depends(run_access)],
) -> Response:
    detail = get_run(run_id, org.org_id)
    if detail.status != "completed":
        return PlainTextResponse("Run not complete.", status_code=409)
    try:
        pdf_bytes = load_run_report_pdf(run_id)
    except FileNotFoundError:
        return PlainTextResponse("Report not found.", status_code=404)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="legal-eval-{run_id}.pdf"',
        },
    )


def main() -> None:
    import uvicorn

    uvicorn.run(
        "legal_eval_api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
