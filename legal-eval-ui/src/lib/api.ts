import { getSessionToken } from "./orgAuth";

const API_BASE =
  process.env.NEXT_PUBLIC_LEGAL_EVAL_API_URL ?? "http://127.0.0.1:8787";

export type RunMode = "eval" | "agent";

export type ModelInfo = {
  id: string;
  label: string;
  provider: string;
  model_id: string;
  requires_env_key: string | null;
  agent_supported?: boolean;
  note?: string | null;
};

export type DatasetSummary = {
  dataset_id: string;
  org_id: string;
  name: string;
  example_count: number;
  categories: string[];
  created_at: string;
  filename: string;
};

export type DatasetImportResponse = DatasetSummary & {
  warning?: string | null;
};

export type AdapterCatalogEntry = {
  name: string;
  description: string;
  task_fit: "span_extraction" | "classification_as_extraction";
  warning?: string | null;
};

export type HuggingFaceImportRequest = {
  repo_id: string;
  config?: string | null;
  split: string;
  max_examples: number;
  adapter: string;
  name?: string | null;
};

export type ExcerptPreview = {
  id: string;
  contract_title: string;
  source_filename: string;
  source_reference: string;
  excerpt_preview: string;
  char_count: number;
};

export type DocumentImportResponse = {
  staging_id: string;
  excerpt_count: number;
  source_files: string[];
  preview: ExcerptPreview[];
  template_filename: string;
  download_path: string;
  instructions: string;
};

export type RunSummary = {
  run_id: string;
  org_id: string;
  dataset_id: string;
  name: string | null;
  mode: RunMode;
  status: "queued" | "running" | "completed" | "failed";
  models: string[];
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  report_url: string | null;
  ui_summary_url: string | null;
  share_url: string | null;
};

export type OrgProfile = {
  org_id: string;
  name: string;
  enabled_models: string[];
  stored_secret_keys: string[];
  created_at: string;
  onboarding_completed_at?: string | null;
};

export type CreateOrgResponse = {
  org_id: string;
  name: string;
  api_key: string;
  enabled_models: string[];
};

export type OnboardingStatus = {
  completed: boolean;
  completed_at: string | null;
};

export type OrgSecretsStatus = {
  stored_keys: string[];
  openai: boolean;
  google: boolean;
  anthropic: boolean;
};

export type ShareLinkResponse = {
  run_id: string;
  token: string;
  share_url: string;
  api_url: string;
};

export type EnterpriseSettings = {
  org_id: string;
  webhook_url: string | null;
  webhook_configured: boolean;
  webhook_secret_stored: boolean;
  bedrock_region: string | null;
  bedrock_endpoint_url: string | null;
  sso_domain: string | null;
  updated_at: string | null;
};

export type OrgStats = {
  org_id: string;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  running_runs: number;
  queued_runs: number;
  eval_runs: number;
  agent_runs: number;
  runs_last_7_days: number;
  success_rate: number | null;
  avg_duration_seconds: number | null;
};

export type AuditEvent = {
  event_id: string;
  org_id: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

type FetchOptions = RequestInit & {
  shareToken?: string;
  auth?: boolean;
  apiKey?: string;
};

async function apiFetch<T>(path: string, init: FetchOptions = {}): Promise<T> {
  const { shareToken, auth = true, apiKey, ...rest } = init;
  const headers = new Headers(rest.headers);

  if (auth) {
    const key = apiKey ?? (await getSessionToken());
    if (!key && !shareToken) {
      throw new Error("Sign in required. Use the Log in button to access your workspace.");
    }
    if (key) {
      headers.set("Authorization", `Bearer ${key}`);
    }
  }

  let url = `${API_BASE}${path}`;
  if (shareToken) {
    const sep = url.includes("?") ? "&" : "?";
    url = `${url}${sep}token=${encodeURIComponent(shareToken)}`;
  }

  const response = await fetch(url, { ...rest, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type LocalSetupStatus = {
  mode: "self_hosted";
  env_file: string;
  keys: Record<string, boolean>;
  ready: boolean;
};

export async function fetchModels(): Promise<ModelInfo[]> {
  const data = await apiFetch<{ models: ModelInfo[] }>("/api/v1/models", { auth: false });
  return data.models;
}

export async function fetchLocalSetup(): Promise<LocalSetupStatus> {
  return apiFetch<LocalSetupStatus>("/api/v1/setup", { auth: false });
}

export async function createOrganization(name: string): Promise<CreateOrgResponse> {
  return apiFetch<CreateOrgResponse>("/api/v1/orgs", {
    method: "POST",
    auth: false,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export async function fetchOrgProfile(): Promise<OrgProfile> {
  return apiFetch<OrgProfile>("/api/v1/orgs/me");
}

export async function fetchOnboardingStatus(): Promise<OnboardingStatus> {
  return apiFetch<OnboardingStatus>("/api/v1/orgs/me/onboarding");
}

export async function completeOnboarding(): Promise<OnboardingStatus> {
  return apiFetch<OnboardingStatus>("/api/v1/orgs/me/onboarding/complete", {
    method: "POST",
  });
}

export async function updateOrgSecrets(secrets: Record<string, string>): Promise<OrgSecretsStatus> {
  return apiFetch<OrgSecretsStatus>("/api/v1/orgs/me/secrets", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ secrets }),
  });
}

export async function fetchOrgSecretsStatus(): Promise<OrgSecretsStatus> {
  return apiFetch<OrgSecretsStatus>("/api/v1/orgs/me/secrets");
}

export async function updateOrgModels(enabled_models: string[]): Promise<OrgProfile> {
  return apiFetch<OrgProfile>("/api/v1/orgs/me/models", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled_models }),
  });
}

export async function uploadDataset(file: File, name?: string): Promise<DatasetSummary> {
  const form = new FormData();
  form.append("file", file);
  if (name) {
    form.append("name", name);
  }
  return apiFetch<DatasetSummary>("/api/v1/datasets", {
    method: "POST",
    body: form,
  });
}

export async function fetchDatasetAdapters(): Promise<AdapterCatalogEntry[]> {
  return apiFetch<AdapterCatalogEntry[]>("/api/v1/datasets/adapters");
}

export async function importHuggingFaceDataset(
  payload: HuggingFaceImportRequest,
): Promise<DatasetImportResponse> {
  return apiFetch<DatasetImportResponse>("/api/v1/datasets/import/huggingface", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function importDocuments(files: File[]): Promise<DocumentImportResponse> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  return apiFetch<DocumentImportResponse>("/api/v1/datasets/import/documents", {
    method: "POST",
    body: form,
  });
}

export async function downloadDocumentTemplate(
  downloadPath: string,
  filename: string,
): Promise<void> {
  const key = await getSessionToken();
  if (!key) {
    throw new Error("Sign in required to download the template.");
  }
  const response = await fetch(`${API_BASE}${downloadPath}`, {
    headers: { Authorization: `Bearer ${key}` },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Download failed (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function createRun(payload: {
  dataset_id: string;
  models: string[];
  mode?: RunMode;
  api_keys?: Record<string, string>;
  skip_judge_validate?: boolean;
  name?: string;
}): Promise<RunSummary> {
  return apiFetch<RunSummary>("/api/v1/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchRun(runId: string, shareToken?: string): Promise<RunSummary> {
  return apiFetch<RunSummary>(`/api/v1/runs/${runId}`, {
    shareToken,
    auth: !shareToken,
  });
}

export type RunArtifactsBundle = {
  run_id: string;
  manifest: Record<string, unknown>;
  metrics: Record<string, unknown>;
  errors_summary: Record<string, unknown>;
  judge_validation: Record<string, unknown> | null;
  calibration: Record<string, unknown> | null;
  examples: Record<string, unknown>[];
  raw_by_model: Record<string, Record<string, unknown>[]>;
  judge_by_model: Record<string, Record<string, unknown>[]>;
  models: string[];
};

export async function fetchRunArtifacts(
  runId: string,
  options: { shareToken?: string; apiKey?: string } = {},
): Promise<RunArtifactsBundle> {
  return apiFetch<RunArtifactsBundle>(`/api/v1/runs/${runId}/artifacts`, {
    shareToken: options.shareToken,
    apiKey: options.apiKey,
    auth: true,
  });
}

export function runArtifactFileUrl(
  runId: string,
  filePath: string,
  shareToken?: string,
): string {
  let url = `${API_BASE}/api/v1/runs/${runId}/artifacts/files/${filePath}`;
  if (shareToken) {
    url += `?token=${encodeURIComponent(shareToken)}`;
  }
  return url;
}

export async function fetchRuns(): Promise<RunSummary[]> {
  return apiFetch<RunSummary[]>("/api/v1/runs");
}

export async function createShareLink(runId: string): Promise<ShareLinkResponse> {
  return apiFetch<ShareLinkResponse>(`/api/v1/runs/${runId}/share`, {
    method: "POST",
  });
}

export async function fetchEnterpriseSettings(): Promise<EnterpriseSettings> {
  return apiFetch<EnterpriseSettings>("/api/v1/orgs/me/settings");
}

export async function updateEnterpriseSettings(
  payload: Partial<{
    webhook_url: string | null;
    webhook_secret: string;
    bedrock_region: string | null;
    bedrock_endpoint_url: string | null;
    sso_domain: string | null;
  }>,
): Promise<EnterpriseSettings> {
  return apiFetch<EnterpriseSettings>("/api/v1/orgs/me/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchOrgStats(): Promise<OrgStats> {
  return apiFetch<OrgStats>("/api/v1/orgs/me/stats");
}

export async function fetchAuditLog(limit = 100): Promise<AuditEvent[]> {
  return apiFetch<AuditEvent[]>(`/api/v1/orgs/me/audit?limit=${limit}`);
}

export function runPdfExportUrl(runId: string): string {
  return `${API_BASE}/api/v1/runs/${runId}/export.pdf`;
}

export async function downloadRunPdf(runId: string): Promise<void> {
  const key = await getSessionToken();
  if (!key) throw new Error("Sign in required.");
  const response = await fetch(runPdfExportUrl(runId), {
    headers: { Authorization: `Bearer ${key}` },
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `legal-eval-${runId}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export { API_BASE };
