import type { EvalExample, ExampleScore, ModelPrediction } from "./types";

export function scoreExample(
  gold: EvalExample,
  prediction: ModelPrediction | null,
  hasError: boolean,
): ExampleScore {
  if (hasError || prediction === null) {
    return {
      presenceCorrect: null,
      presenceLabel: "no prediction",
      spanGrounded: null,
      spanLabel: "—",
    };
  }

  const presenceCorrect = prediction.present === gold.present;
  let spanGrounded: boolean | null = null;
  let spanLabel = "—";

  if (gold.present && prediction.present && prediction.span) {
    const inExcerpt = gold.contract_excerpt.includes(prediction.span);
    spanGrounded = inExcerpt;
    spanLabel = inExcerpt ? "in excerpt" : "hallucinated";
  } else if (!gold.present && !prediction.present) {
    spanLabel = "n/a (absent)";
  } else if (gold.present && !prediction.present) {
    spanLabel = "missed span";
  } else if (!gold.present && prediction.present) {
    spanLabel = prediction.span
      ? gold.contract_excerpt.includes(prediction.span)
        ? "false span in text"
        : "hallucinated FP"
      : "false present";
  }

  return {
    presenceCorrect,
    presenceLabel: presenceCorrect ? "correct" : "wrong",
    spanGrounded,
    spanLabel,
  };
}
