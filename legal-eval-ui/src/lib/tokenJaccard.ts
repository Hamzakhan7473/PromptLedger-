export function tokenize(text: string): Set<string> {
  const matches = text.toLowerCase().match(/[a-z0-9]+/g);
  return new Set(matches ?? []);
}

export function tokenJaccard(predicted: string, gold: string): number {
  const predTokens = tokenize(predicted);
  const goldTokens = tokenize(gold);
  if (predTokens.size === 0 && goldTokens.size === 0) {
    return 1;
  }
  if (predTokens.size === 0 || goldTokens.size === 0) {
    return 0;
  }
  let intersection = 0;
  for (const t of predTokens) {
    if (goldTokens.has(t)) {
      intersection++;
    }
  }
  const union = predTokens.size + goldTokens.size - intersection;
  return intersection / union;
}

export function bestGoldJaccard(
  predictedSpan: string,
  goldSpans: string[],
): number {
  if (goldSpans.length === 0) {
    return 0;
  }
  return Math.max(
    ...goldSpans.map((gold) => tokenJaccard(predictedSpan, gold)),
  );
}
