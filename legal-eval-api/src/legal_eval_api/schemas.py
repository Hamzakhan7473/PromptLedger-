"""Request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RunStatus = Literal["queued", "running", "completed", "failed"]
RunMode = Literal["eval", "agent"]


class DatasetSummary(BaseModel):
    dataset_id: str
    org_id: str
    name: str
    example_count: int
    categories: list[str]
    created_at: datetime
    filename: str


class DatasetImportResponse(DatasetSummary):
    warning: str | None = None


class HuggingFaceImportRequest(BaseModel):
    repo_id: str = Field(min_length=1)
    config: str | None = None
    split: str = "test"
    max_examples: int = Field(default=100, ge=1, le=10_000)
    adapter: str = Field(min_length=1)
    name: str | None = None


class AdapterCatalogEntry(BaseModel):
    name: str
    description: str
    task_fit: Literal["span_extraction", "classification_as_extraction"]
    warning: str | None = None


class ExcerptPreview(BaseModel):
    id: str
    contract_title: str
    source_filename: str
    source_reference: str
    excerpt_preview: str
    char_count: int


class DocumentImportResponse(BaseModel):
    staging_id: str
    excerpt_count: int
    source_files: list[str]
    preview: list[ExcerptPreview]
    template_filename: str
    download_path: str
    instructions: str


class CreateRunRequest(BaseModel):
    dataset_id: str
    models: list[str] = Field(min_length=1)
    mode: RunMode = "eval"
    api_keys: dict[str, str] = Field(
        default_factory=dict,
        description="Optional per-run overrides; org-stored keys used when omitted.",
    )
    skip_judge_validate: bool = False
    name: str | None = None


class RunSummary(BaseModel):
    run_id: str
    org_id: str
    dataset_id: str
    name: str | None
    mode: RunMode = "eval"
    status: RunStatus
    models: list[str]
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    report_url: str | None = None
    ui_summary_url: str | None = None
    share_url: str | None = None


class RunDetail(RunSummary):
    steps_completed: list[str] = Field(default_factory=list)
    judge_kappa: float | None = None
    result: dict[str, Any] | None = None


class ModelInfo(BaseModel):
    id: str
    label: str
    provider: str
    model_id: str
    requires_env_key: str | None = None
    agent_supported: bool = True
    note: str | None = None


class CreateOrgRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CreateOrgResponse(BaseModel):
    org_id: str
    name: str
    api_key: str
    enabled_models: list[str]


class OrgProfile(BaseModel):
    org_id: str
    name: str
    enabled_models: list[str]
    stored_secret_keys: list[str]
    created_at: str


class UpdateOrgSecretsRequest(BaseModel):
    secrets: dict[str, str] = Field(default_factory=dict)


class UpdateOrgModelsRequest(BaseModel):
    enabled_models: list[str] = Field(min_length=1)


class OrgSecretsStatus(BaseModel):
    stored_keys: list[str]
    openai: bool
    google: bool
    anthropic: bool


class ShareLinkResponse(BaseModel):
    run_id: str
    token: str
    share_url: str
    api_url: str


class AuditEvent(BaseModel):
    event_id: str
    org_id: str
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class EnterpriseSettings(BaseModel):
    org_id: str
    webhook_url: str | None = None
    webhook_configured: bool = False
    webhook_secret_stored: bool = False
    bedrock_region: str | None = None
    bedrock_endpoint_url: str | None = None
    sso_domain: str | None = None
    updated_at: str | None = None


class UpdateEnterpriseSettingsRequest(BaseModel):
    webhook_url: str | None = None
    webhook_secret: str | None = Field(
        default=None,
        description="HMAC signing secret. Empty string clears stored secret.",
    )
    bedrock_region: str | None = None
    bedrock_endpoint_url: str | None = None
    sso_domain: str | None = Field(
        default=None,
        description="Email domain for SSO routing (e.g. firm.com). Enforced at API gateway in production.",
    )


class OrgStats(BaseModel):
    org_id: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    running_runs: int
    queued_runs: int
    eval_runs: int
    agent_runs: int
    runs_last_7_days: int
    success_rate: float | None = None
    avg_duration_seconds: float | None = None
