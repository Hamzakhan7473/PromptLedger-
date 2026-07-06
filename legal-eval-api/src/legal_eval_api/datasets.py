"""Dataset upload validation and catalog."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile

from legaleval.data.schema import (
    EvalExample,
    gold_span_warnings,
    semantic_validation_errors,
    write_eval_set_jsonl,
)

from legal_eval_api.audit import record_audit
from legal_eval_api.config import AVAILABLE_MODELS, DOCUMENT_STAGING_DIR
from legal_eval_api.schemas import (
    AdapterCatalogEntry,
    DatasetImportResponse,
    DatasetSummary,
    DocumentImportResponse,
    ExcerptPreview,
    HuggingFaceImportRequest,
    ModelInfo,
)
from legal_eval_api.storage import (
    dataset_eval_path,
    dataset_meta_path,
    ensure_dirs,
    new_id,
    read_json,
    utc_now,
    write_json,
)

logger = logging.getLogger(__name__)


def model_catalog() -> list[ModelInfo]:
    return [
        ModelInfo(
            id="openai",
            label="OpenAI GPT-5.4 mini",
            provider="openai",
            model_id="gpt-5.4-mini",
            requires_env_key="OPENAI_API_KEY",
            note="Save in Settings → Model API keys (encrypted per org).",
        ),
        ModelInfo(
            id="google",
            label="Google Gemini 2.5 Flash",
            provider="google",
            model_id="gemini-2.5-flash",
            requires_env_key="GOOGLE_API_KEY",
            note="Save in Settings → Model API keys (encrypted per org).",
        ),
        ModelInfo(
            id="bedrock_claude",
            label="Bedrock Claude Sonnet 4.6",
            provider="bedrock",
            model_id="us.anthropic.claude-sonnet-4-6",
            requires_env_key=None,
            agent_supported=True,
            note="Configure AWS/Bedrock access for your deployment (Settings → Enterprise).",
        ),
    ]


def parse_eval_jsonl(text: str) -> list[EvalExample]:
    examples: list[EvalExample] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
            examples.append(EvalExample.model_validate(payload))
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Line {line_no}: invalid example — {exc}",
            ) from exc
    if not examples:
        raise HTTPException(status_code=400, detail="Dataset is empty.")
    return examples


def validate_dataset_semantics(examples: list[EvalExample]) -> None:
    """Reject datasets that would fail judge validation or violate gold-span rules."""
    errors = semantic_validation_errors(examples)
    if errors:
        detail = errors[0] if len(errors) == 1 else "; ".join(errors)
        raise HTTPException(status_code=400, detail=detail)

    for warning in gold_span_warnings(examples):
        logger.warning("Dataset upload: %s", warning)


def persist_eval_examples(
    examples: list[EvalExample],
    *,
    org_id: str,
    name: str,
    filename: str,
    audit_action: str = "dataset.uploaded",
    audit_metadata: dict | None = None,
) -> DatasetSummary:
    """Validate and store EvalExample rows (shared by JSONL upload and HF import)."""
    ensure_dirs()
    validate_dataset_semantics(examples)
    dataset_id = new_id()
    dest = dataset_eval_path(dataset_id)
    write_eval_set_jsonl(examples, dest)

    categories = sorted({example.category for example in examples})
    created_at = utc_now()
    meta = {
        "dataset_id": dataset_id,
        "org_id": org_id,
        "name": name,
        "example_count": len(examples),
        "categories": categories,
        "created_at": created_at.isoformat(),
        "filename": filename,
    }
    write_json(dataset_meta_path(dataset_id), meta)
    record_audit(
        org_id,
        audit_action,
        resource_type="dataset",
        resource_id=dataset_id,
        metadata=audit_metadata
        or {"example_count": len(examples), "filename": filename},
    )
    return DatasetSummary(**meta)


def validate_models(selected: list[str]) -> list[str]:
    unknown = [name for name in selected if name not in AVAILABLE_MODELS]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model(s): {', '.join(unknown)}",
        )
    return selected


async def ingest_dataset(
    upload: UploadFile,
    *,
    org_id: str,
    name: str | None = None,
) -> DatasetSummary:
    ensure_dirs()
    if not upload.filename or not upload.filename.endswith(".jsonl"):
        raise HTTPException(
            status_code=400,
            detail="Upload a .jsonl file (one EvalExample per line).",
        )

    body = await upload.read()
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8.") from exc

    examples = parse_eval_jsonl(text)
    return await ingest_eval_examples(
        examples,
        org_id=org_id,
        name=name or upload.filename or "dataset",
        filename=upload.filename or "upload.jsonl",
    )


async def ingest_eval_examples(
    examples: list[EvalExample],
    *,
    org_id: str,
    name: str,
    filename: str,
    audit_action: str = "dataset.uploaded",
    audit_metadata: dict | None = None,
) -> DatasetSummary:
    return persist_eval_examples(
        examples,
        org_id=org_id,
        name=name,
        filename=filename,
        audit_action=audit_action,
        audit_metadata=audit_metadata,
    )


def list_datasets(org_id: str) -> list[DatasetSummary]:
    ensure_dirs()
    summaries: list[DatasetSummary] = []
    if not DATASETS_DIR.exists():
        return summaries
    for path in sorted(DATASETS_DIR.iterdir()):
        if not path.is_dir():
            continue
        meta_file = path / "meta.json"
        if meta_file.exists():
            meta = read_json(meta_file)
            if meta.get("org_id") == org_id:
                summaries.append(DatasetSummary(**meta))
    summaries.sort(key=lambda item: item.created_at, reverse=True)
    return summaries


def get_dataset(dataset_id: str, org_id: str) -> DatasetSummary:
    meta_file = dataset_meta_path(dataset_id)
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    meta = read_json(meta_file)
    if meta.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return DatasetSummary(**meta)


def get_dataset_eval_path(dataset_id: str, org_id: str) -> Path:
    get_dataset(dataset_id, org_id)
    path = dataset_eval_path(dataset_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return path


async def ingest_hf_dataset(
    request: HuggingFaceImportRequest,
    *,
    org_id: str,
) -> DatasetImportResponse:
    from legal_eval_api.dataset_sources.huggingface import import_hf_dataset

    examples, adapter = import_hf_dataset(
        repo_id=request.repo_id.strip(),
        config=request.config.strip() if request.config else None,
        split=request.split.strip(),
        max_examples=request.max_examples,
        adapter_name=request.adapter.strip(),
    )
    display_name = request.name or (
        f"{request.repo_id}"
        + (f"/{request.config}" if request.config else "")
        + f" ({request.split})"
    )
    filename = (
        f"hf:{request.repo_id}"
        + (f":{request.config}" if request.config else "")
        + f":{request.split}.jsonl"
    )
    summary = await ingest_eval_examples(
        examples,
        org_id=org_id,
        name=display_name,
        filename=filename,
        audit_action="dataset.imported.huggingface",
        audit_metadata={
            "example_count": len(examples),
            "filename": filename,
            "repo_id": request.repo_id,
            "config": request.config,
            "split": request.split,
            "adapter": request.adapter,
        },
    )
    return DatasetImportResponse(**summary.model_dump(), warning=adapter.warning)


def list_adapters() -> list[AdapterCatalogEntry]:
    from legal_eval_api.dataset_sources.adapters import list_adapters as _list

    return [
        AdapterCatalogEntry(
            name=spec.name,
            description=spec.description,
            task_fit=spec.task_fit,
            warning=spec.warning,
        )
        for spec in _list()
    ]


PREVIEW_SNIPPET_CHARS = 240
DOCUMENT_TEMPLATE_INSTRUCTIONS = (
    "Fill in category, present, and gold_spans for each row in the downloaded template, "
    "then upload the completed file on the JSONL tab to run your eval. "
    "This is a two-step workflow — labeling happens outside the app."
)


async def ingest_documents(
    files: list[UploadFile],
    *,
    org_id: str,
) -> DocumentImportResponse:
    from legal_eval_api.dataset_sources.documents import (
        build_candidates_from_uploads,
        render_template_jsonl,
    )

    ensure_dirs()
    DOCUMENT_STAGING_DIR.mkdir(parents=True, exist_ok=True)

    candidates = await build_candidates_from_uploads(files)
    staging_id = new_id()
    staging_dir = DOCUMENT_STAGING_DIR / staging_id
    staging_dir.mkdir(parents=True, exist_ok=True)

    template_filename = f"labeling-template-{staging_id}.jsonl"
    template_path = staging_dir / template_filename
    template_path.write_text(render_template_jsonl(candidates), encoding="utf-8")

    source_files = sorted({candidate.source_filename for candidate in candidates})
    write_json(
        staging_dir / "meta.json",
        {
            "staging_id": staging_id,
            "org_id": org_id,
            "template_filename": template_filename,
            "source_files": source_files,
            "excerpt_count": len(candidates),
            "created_at": utc_now().isoformat(),
        },
    )

    record_audit(
        org_id,
        action="dataset.imported.documents",
        resource_type="document_staging",
        resource_id=staging_id,
        metadata={
            "excerpt_count": len(candidates),
            "source_files": source_files,
        },
    )

    preview = [
        ExcerptPreview(
            id=candidate.id,
            contract_title=candidate.contract_title,
            source_filename=candidate.source_filename,
            source_reference=candidate.source_reference,
            excerpt_preview=candidate.contract_excerpt[:PREVIEW_SNIPPET_CHARS]
            + ("…" if len(candidate.contract_excerpt) > PREVIEW_SNIPPET_CHARS else ""),
            char_count=len(candidate.contract_excerpt),
        )
        for candidate in candidates[:5]
    ]

    return DocumentImportResponse(
        staging_id=staging_id,
        excerpt_count=len(candidates),
        source_files=source_files,
        preview=preview,
        template_filename=template_filename,
        download_path=f"/api/v1/datasets/import/documents/{staging_id}/template.jsonl",
        instructions=DOCUMENT_TEMPLATE_INSTRUCTIONS,
    )


def get_document_template_path(staging_id: str, org_id: str) -> tuple[Path, str]:
    staging_dir = DOCUMENT_STAGING_DIR / staging_id
    meta_file = staging_dir / "meta.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail=f"Document staging not found: {staging_id}")
    meta = read_json(meta_file)
    if meta.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail=f"Document staging not found: {staging_id}")
    template_filename = meta.get("template_filename", f"labeling-template-{staging_id}.jsonl")
    template_path = staging_dir / template_filename
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Labeling template not found: {staging_id}")
    return template_path, template_filename


# Re-export for storage module used in list_datasets
from legal_eval_api.storage import DATASETS_DIR  # noqa: E402
