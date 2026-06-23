import fs from "fs";
import path from "path";

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

const RESULTS_DIR = path.join(process.cwd(), "public", "results");

function readJson<T>(filePath: string): T {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as T;
}

function readJsonIfExists<T>(filePath: string): T | null {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  return readJson<T>(filePath);
}

function readJsonl<T>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const raw = fs.readFileSync(filePath, "utf-8");
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line) as T);
}

function runDir(runId: string): string {
  return path.join(RESULTS_DIR, runId);
}

/** List run IDs available under public/results/. */
export function listRunIds(): string[] {
  if (!fs.existsSync(RESULTS_DIR)) {
    return [];
  }
  return fs
    .readdirSync(RESULTS_DIR)
    .filter((name) => {
      if (name.startsWith(".")) {
        return false;
      }
      const stat = fs.statSync(path.join(RESULTS_DIR, name));
      return stat.isDirectory();
    })
    .sort()
    .reverse();
}

function loadJudgeDecisions(
  judgeDir: string,
): Record<string, JudgeDecisionRow[]> {
  const byModel: Record<string, JudgeDecisionRow[]> = {};
  if (!fs.existsSync(judgeDir)) {
    return byModel;
  }
  for (const file of fs.readdirSync(judgeDir)) {
    if (!file.endsWith("_decisions.jsonl")) {
      continue;
    }
    const model = file.replace(/_decisions\.jsonl$/, "");
    byModel[model] = readJsonl<JudgeDecisionRow>(path.join(judgeDir, file));
  }
  return byModel;
}

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

/**
 * Load a complete eval run from public/results/<run_id>/.
 *
 * Expected layout (copy from legal-eval harness output):
 *   manifest.json, metrics.json, errors_summary.json, eval_set.jsonl
 *   raw/<model>.jsonl
 *   judge/validation.json, judge/<model>_decisions.jsonl (optional)
 *   calibration/ece.json
 */
export function loadRun(runId: string): EvalRun {
  const base = runDir(runId);
  if (!fs.existsSync(base)) {
    throw new Error(`Run not found: ${runId} (looked in ${base})`);
  }

  const manifest = readJson<Manifest>(path.join(base, "manifest.json"));
  const metrics = readJson<MetricsFile>(path.join(base, "metrics.json"));
  const errorsSummary = readJson<ErrorsSummaryFile>(
    path.join(base, "errors_summary.json"),
  );
  const judgeValidation =
    readJsonIfExists<JudgeValidationFile>(
      path.join(base, "judge", "validation.json"),
    ) ??
    ({
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
    } satisfies JudgeValidationFile);
  const calibration =
    readJsonIfExists<CalibrationFile>(
      path.join(base, "calibration", "ece.json"),
    ) ??
    ({
      run_id: runId,
      eval_set: "",
      models: {},
    } satisfies CalibrationFile);

  const evalSetPath = path.join(base, "eval_set.jsonl");
  if (!fs.existsSync(evalSetPath)) {
    throw new Error(
      `eval_set.jsonl required for Sample Viewer (missing in ${base})`,
    );
  }
  const examples = readJsonl<EvalExample>(evalSetPath);

  const rawDir = path.join(base, "raw");
  const rawByModel: Record<string, RawLogRow[]> = {};
  if (fs.existsSync(rawDir)) {
    for (const file of fs.readdirSync(rawDir)) {
      if (file.endsWith(".jsonl")) {
        const model = file.replace(/\.jsonl$/, "");
        rawByModel[model] = readJsonl<RawLogRow>(path.join(rawDir, file));
      }
    }
  }

  const judgeByModel = loadJudgeDecisions(path.join(base, "judge"));
  const models = Object.keys(rawByModel).sort();

  return {
    runId,
    manifest,
    metrics,
    errorsSummary,
    judgeValidation,
    calibration,
    examples,
    models,
    rawByModel,
    rawByExample: indexRawByExample(rawByModel),
    judgeByExample: indexJudgeByExample(judgeByModel),
  };
}
