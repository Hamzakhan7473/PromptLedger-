/** Types matching legal-eval harness JSON outputs. */

export interface EvalExample {
  id: string;
  contract_excerpt: string;
  category: string;
  present: boolean;
  gold_spans: string[];
  contract_title: string;
}

export interface ModelPrediction {
  present: boolean;
  span: string | null;
  confidence: number;
  reasoning: string;
}

export interface RawLogRow {
  run_id: string;
  example_id: string;
  category: string;
  contract_title: string;
  provider: string;
  model: string;
  model_id: string;
  latency_ms: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  raw_text: string | null;
  parsed: ModelPrediction | null;
  parse_error: string | null;
  error: string | null;
}

export interface JudgeDecisionRow {
  run_id: string;
  example_id: string;
  evaluated_model: string;
  category: string;
  contract_title: string;
  token_jaccard: number;
  gold_span: string;
  predicted_span: string;
  judge_model_id: string;
  judge_provider: string;
  latency_ms: number | null;
  span_correct: boolean | null;
  rationale: string | null;
  raw_text: string | null;
  parse_error: string | null;
  error: string | null;
}

export interface Manifest {
  run_id: string;
  run_date_utc: string;
  seeds: Record<string, number>;
  eval_set: { path: string; sha256: string };
  models_yaml: {
    path: string;
    sha256: string;
    pinned: Record<string, unknown>;
  };
  steps_completed: string[];
}

export interface MetricsFile {
  run_id: string;
  eval_set: string;
  n_bootstrap: number;
  models: Record<string, unknown>;
}

export interface ErrorsSummaryFile {
  run_id: string;
  eval_set: string;
  models: Record<
    string,
    {
      report_path: string;
      total_errors: number;
      counts_by_bucket: Record<string, number>;
    }
  >;
}

export interface JudgeValidationFile {
  sample_size: number;
  seed: number;
  reference_rule: string;
  agreement: {
    n_sampled: number;
    n_scored: number;
    n_errors: number;
    accuracy: number | null;
    cohens_kappa: number | null;
    min_kappa_required: number;
    passes_threshold: boolean;
  };
  cases: unknown[];
}

export interface CalibrationBin {
  bin_index: number;
  confidence_low: number;
  confidence_high: number;
  mean_confidence: number;
  empirical_accuracy: number;
  count: number;
}

export interface CalibrationModelData {
  ece: number;
  n_calibrated: number;
  n_excluded: number;
  bins?: CalibrationBin[];
  plot_path?: string;
}

export interface CalibrationFile {
  run_id: string;
  eval_set: string;
  models: Record<string, CalibrationModelData>;
}

export interface ExampleScore {
  presenceCorrect: boolean | null;
  presenceLabel: string;
  spanGrounded: boolean | null;
  spanLabel: string;
}

export interface ModelExampleView {
  model: string;
  row: RawLogRow | null;
  prediction: ModelPrediction | null;
  score: ExampleScore;
  hallucinated: boolean;
  judge: JudgeDecisionRow | null;
}

export interface EvalRun {
  runId: string;
  manifest: Manifest;
  metrics: MetricsFile;
  errorsSummary: ErrorsSummaryFile;
  judgeValidation: JudgeValidationFile;
  calibration: CalibrationFile;
  examples: EvalExample[];
  models: string[];
  rawByModel: Record<string, RawLogRow[]>;
  rawByExample: Record<string, Record<string, RawLogRow>>;
  judgeByExample: Record<string, Record<string, JudgeDecisionRow>>;
}
