import type { EvalRun } from "./types";

export interface PinnedModel {
  name: string;
  modelId: string;
}

export interface ProvenanceInfo {
  runId: string;
  runDateUtc: string;
  datasetPath: string;
  datasetSha256: string;
  seeds: Record<string, number>;
  pinnedModels: PinnedModel[];
  judgeModelId: string | null;
}

function pinnedModelsFromManifest(manifest: EvalRun["manifest"]): PinnedModel[] {
  const pinned = manifest.models_yaml?.pinned;
  if (!pinned || typeof pinned !== "object") {
    return [];
  }
  const modelsBlock = (pinned as { models?: Record<string, { model_id?: string }> }).models;
  if (!modelsBlock || typeof modelsBlock !== "object") {
    return [];
  }
  return Object.entries(modelsBlock)
    .map(([name, spec]) => ({
      name,
      modelId: spec?.model_id ?? "—",
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function extractProvenance(run: EvalRun): ProvenanceInfo {
  const judgeBlock = run.manifest.models_yaml?.pinned as
    | { judge?: { model_id?: string } }
    | undefined;

  return {
    runId: run.manifest.run_id,
    runDateUtc: run.manifest.run_date_utc,
    datasetPath: run.manifest.eval_set?.path ?? run.metrics.eval_set ?? "—",
    datasetSha256: run.manifest.eval_set?.sha256 ?? "—",
    seeds: run.manifest.seeds ?? {},
    pinnedModels: pinnedModelsFromManifest(run.manifest),
    judgeModelId: judgeBlock?.judge?.model_id ?? null,
  };
}

export function formatProvenanceTimestamp(iso: string): string {
  const parsed = Date.parse(iso);
  if (Number.isNaN(parsed)) {
    return iso;
  }
  return new Date(parsed).toUTCString();
}
