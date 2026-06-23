import type { OutcomeBucket } from "./classifyOutcome";

/** Harness error taxonomy buckets from errors_summary.json. */
export const HARNESS_ERROR_BUCKETS = [
  "missed_present",
  "false_present",
  "correct_present_wrong_span",
  "hallucinated_span",
  "parse_fail",
] as const;

export type HarnessErrorBucket = (typeof HARNESS_ERROR_BUCKETS)[number];

export const HARNESS_BUCKET_LABELS: Record<HarnessErrorBucket, string> = {
  missed_present: "missed",
  false_present: "false present",
  correct_present_wrong_span: "wrong span",
  hallucinated_span: "hallucinated",
  parse_fail: "parse fail",
};

export function harnessBucketToOutcome(
  bucket: string,
): OutcomeBucket | null {
  switch (bucket) {
    case "missed_present":
      return "missed";
    case "false_present":
      return "false_present";
    case "correct_present_wrong_span":
    case "hallucinated_span":
      return "wrong_span";
    case "parse_fail":
      return "parse_fail";
    default:
      return null;
  }
}

export function isHarnessErrorBucket(
  bucket: string,
): bucket is HarnessErrorBucket {
  return (HARNESS_ERROR_BUCKETS as readonly string[]).includes(bucket);
}
