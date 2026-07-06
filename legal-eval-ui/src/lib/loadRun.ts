import type {
  CalibrationFile,
  ErrorsSummaryFile,
  EvalExample,
  EvalRun,
  JudgeDecisionRow,
  JudgeValidationFile,
  Manifest,
  MetricsFile,
  RawLogRow,
} from "./types";
import { fetchRunArtifacts, type RunArtifactsBundle } from "./api";

export type LoadRunOptions = {
  shareToken?: string;
  apiKey?: string;
};

const DEFAULT_JUDGE_VALIDATION: JudgeValidationFile = {
  sample_size: 0,
  seed: 0,
  reference_rule: "",
  agreement: {
    n_sampled: 0,
    n_scored: 0,
    n_errors: 0,
    accuracy: null,
    cohens_kappa: null,
    min_kappa_required: 0.6,
    passes_threshold: false,
  },
  cases: [],
};

const DEFAULT_CALIBRATION = (runId: string): CalibrationFile => ({
  run_id: runId,
  eval_set: "",
  models: {},
});

function indexRawByExample(
  rawByModel: Record<string, RawLogRow[]>,
): Record<string, Record<string, RawLogRow>> {
  const index: Record<string, Record<string, RawLogRow>> = {};
  for (const [model, rows] of Object.entries(rawByModel)) {
    for (const row of rows) {
      if (!index[row.example_id]) {
        index[row.example_id] = {};
      }
      index[row.example_id][model] = row;
    }
  }
  return index;
}

function indexJudgeByExample(
  judgeByModel: Record<string, JudgeDecisionRow[]>,
): Record<string, Record<string, JudgeDecisionRow>> {
  const index: Record<string, Record<string, JudgeDecisionRow>> = {};
  for (const [model, rows] of Object.entries(judgeByModel)) {
    for (const row of rows) {
      if (!index[row.example_id]) {
        index[row.example_id] = {};
      }
      index[row.example_id][model] = row;
    }
  }
  return index;
}

function bundleToEvalRun(runId: string, bundle: RunArtifactsBundle): EvalRun {
  const rawByModel = bundle.raw_by_model as unknown as Record<string, RawLogRow[]>;
  const judgeByModel = bundle.judge_by_model as unknown as Record<string, JudgeDecisionRow[]>;

  return {
    runId,
    manifest: bundle.manifest as unknown as Manifest,
    metrics: bundle.metrics as unknown as MetricsFile,
    errorsSummary: bundle.errors_summary as unknown as ErrorsSummaryFile,
    judgeValidation:
      (bundle.judge_validation as unknown as JudgeValidationFile | null) ?? DEFAULT_JUDGE_VALIDATION,
    calibration: (bundle.calibration as unknown as CalibrationFile | null) ?? DEFAULT_CALIBRATION(runId),
    examples: bundle.examples as unknown as EvalExample[],
    models: bundle.models.length > 0 ? bundle.models : Object.keys(rawByModel).sort(),
    rawByModel,
    rawByExample: indexRawByExample(rawByModel),
    judgeByExample: indexJudgeByExample(judgeByModel),
  };
}

/**
 * Load a complete eval run from the API at runtime (replaces build-time public/results reads).
 */
export async function loadRun(runId: string, options: LoadRunOptions = {}): Promise<EvalRun> {
  const bundle = await fetchRunArtifacts(runId, {
    shareToken: options.shareToken,
    apiKey: options.apiKey,
  });
  return bundleToEvalRun(runId, bundle);
}

/** @deprecated Static public/results listing; use fetchRuns() from the API instead. */
export function listRunIds(): string[] {
  return [];
}
