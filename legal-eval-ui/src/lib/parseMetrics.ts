import type { CalibrationFile, EvalRun, MetricsFile } from "./types";

export interface ModelSummaryMetrics {
  model: string;
  presenceF1: number | null;
  f1CiLow: number | null;
  f1CiHigh: number | null;
  meanJaccard: number | null;
  hallucinationRate: number | null;
  parseRate: number | null;
  ece: number | null;
}

interface PresenceOverall {
  f1?: number;
  f1_ci_95?: { low: number; high: number };
}

interface SpanOverall {
  mean_jaccard?: number;
  hallucination_rate?: number;
}

interface ReliabilityOverall {
  combined_error_rate?: number;
}

interface ModelMetricsEntry {
  presence?: { overall?: PresenceOverall };
  span_grounding?: { overall?: SpanOverall };
  reliability?: ReliabilityOverall;
}

function asModelEntry(value: unknown): ModelMetricsEntry {
  return (value ?? {}) as ModelMetricsEntry;
}

export function extractModelMetrics(run: EvalRun): ModelSummaryMetrics[] {
  const metrics = run.metrics as MetricsFile & {
    models: Record<string, unknown>;
  };

  return run.models.map((model) => {
    const entry = asModelEntry(metrics.models[model]);
    const cal = run.calibration.models[model] as
      | CalibrationFile["models"][string]
      | undefined;

    return {
      model,
      presenceF1: entry.presence?.overall?.f1 ?? null,
      f1CiLow: entry.presence?.overall?.f1_ci_95?.low ?? null,
      f1CiHigh: entry.presence?.overall?.f1_ci_95?.high ?? null,
      meanJaccard: entry.span_grounding?.overall?.mean_jaccard ?? null,
      hallucinationRate:
        entry.span_grounding?.overall?.hallucination_rate ?? null,
      parseRate: entry.reliability?.combined_error_rate ?? null,
      ece: cal?.ece ?? null,
    };
  });
}

export function formatRate(value: number | null, digits = 3): string {
  if (value === null) {
    return "—";
  }
  return value.toFixed(digits);
}

export function formatF1WithCi(
  f1: number | null,
  low: number | null,
  high: number | null,
): string {
  if (f1 === null) {
    return "—";
  }
  if (low !== null && high !== null) {
    return `${f1.toFixed(3)} [${low.toFixed(3)}–${high.toFixed(3)}]`;
  }
  return f1.toFixed(3);
}
