import type { EvalExample, RawLogRow } from "./types";
import { bestGoldJaccard } from "./tokenJaccard";

/** Matches legal-eval report/errors.py span match threshold. */
export const SPAN_MATCH_THRESHOLD = 0.7;

export type OutcomeBucket =
  | "correct"
  | "wrong_span"
  | "false_present"
  | "missed"
  | "parse_fail";

export const OUTCOME_LABELS: Record<OutcomeBucket, string> = {
  correct: "correct",
  wrong_span: "wrong span",
  false_present: "false present",
  missed: "missed",
  parse_fail: "parse fail",
};

export const OUTCOME_SHORT: Record<OutcomeBucket, string> = {
  correct: "ok",
  wrong_span: "span",
  false_present: "fp",
  missed: "miss",
  parse_fail: "err",
};

export const OUTCOME_CELL_CLASS: Record<OutcomeBucket, string> = {
  correct: "bg-green-100 text-green-900 hover:bg-green-200",
  wrong_span: "bg-amber-100 text-amber-950 hover:bg-amber-200",
  false_present: "bg-orange-100 text-orange-950 hover:bg-orange-200",
  missed: "bg-red-100 text-red-900 hover:bg-red-200",
  parse_fail: "bg-neutral-200 text-neutral-700 hover:bg-neutral-300",
};

export const OUTCOME_LEGEND_CLASS: Record<OutcomeBucket, string> = {
  correct: "bg-green-100 border-green-400",
  wrong_span: "bg-amber-100 border-amber-400",
  false_present: "bg-orange-100 border-orange-400",
  missed: "bg-red-100 border-red-400",
  parse_fail: "bg-neutral-200 border-neutral-400",
};

export interface ClassifiedOutcome {
  bucket: OutcomeBucket;
  predPresent: boolean | null;
}

/** Mirrors legal-eval classify_error bucket assignment. */
export function classifyOutcome(
  example: EvalExample,
  row: RawLogRow | null,
): ClassifiedOutcome {
  if (!row || row.error || row.parse_error || row.parsed === null) {
    return { bucket: "parse_fail", predPresent: null };
  }

  const pred = row.parsed;

  if (example.present && !pred.present) {
    return { bucket: "missed", predPresent: false };
  }

  if (!example.present && pred.present) {
    return { bucket: "false_present", predPresent: true };
  }

  if (pred.present && pred.span) {
    if (!example.contract_excerpt.includes(pred.span)) {
      return { bucket: "wrong_span", predPresent: true };
    }
    if (example.present) {
      const jaccard = bestGoldJaccard(pred.span, example.gold_spans);
      if (jaccard < SPAN_MATCH_THRESHOLD) {
        return { bucket: "wrong_span", predPresent: true };
      }
    }
  }

  return { bucket: "correct", predPresent: pred.present };
}

export function modelsDisagreeOnPresence(
  outcomes: ClassifiedOutcome[],
): boolean {
  const keys = outcomes.map((o) =>
    o.predPresent === null ? "?" : String(o.predPresent),
  );
  return new Set(keys).size > 1;
}
