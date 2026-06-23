import type { ReactNode } from "react";

export interface SpanRange {
  start: number;
  end: number;
  gold?: boolean;
  model?: string;
}

const MODEL_COLORS = [
  "bg-sky-200 text-sky-950",
  "bg-violet-200 text-violet-950",
  "bg-rose-200 text-rose-950",
  "bg-lime-200 text-lime-950",
  "bg-orange-200 text-orange-950",
];

const GOLD_CLASS = "bg-amber-200 text-amber-950";
const OVERLAP_CLASS = "bg-teal-300 text-teal-950 ring-1 ring-teal-700";

export function modelColorClass(model: string, modelOrder: string[]): string {
  const idx = modelOrder.indexOf(model);
  return MODEL_COLORS[idx % MODEL_COLORS.length] ?? "bg-gray-200";
}

export function findSpanRange(
  excerpt: string,
  span: string,
): { start: number; end: number } | null {
  if (!span) {
    return null;
  }
  const start = excerpt.indexOf(span);
  if (start === -1) {
    return null;
  }
  return { start, end: start + span.length };
}

export function buildHighlightRanges(
  excerpt: string,
  goldSpans: string[],
  predictedByModel: Record<string, string | null | undefined>,
): SpanRange[] {
  const ranges: SpanRange[] = [];

  for (const span of goldSpans) {
    const pos = findSpanRange(excerpt, span);
    if (pos) {
      ranges.push({ ...pos, gold: true });
    }
  }

  for (const [model, span] of Object.entries(predictedByModel)) {
    if (!span) {
      continue;
    }
    const pos = findSpanRange(excerpt, span);
    if (pos) {
      ranges.push({ ...pos, model });
    }
  }

  return ranges;
}

function segmentFlags(
  mid: number,
  ranges: SpanRange[],
): { gold: boolean; models: string[] } {
  const models: string[] = [];
  let gold = false;
  for (const range of ranges) {
    if (mid >= range.start && mid < range.end) {
      if (range.gold) {
        gold = true;
      }
      if (range.model && !models.includes(range.model)) {
        models.push(range.model);
      }
    }
  }
  return { gold, models };
}

export function HighlightedExcerpt({
  excerpt,
  goldSpans,
  predictedByModel,
  modelOrder,
}: {
  excerpt: string;
  goldSpans: string[];
  predictedByModel: Record<string, string | null | undefined>;
  modelOrder: string[];
}) {
  const ranges = buildHighlightRanges(excerpt, goldSpans, predictedByModel);

  const breakpoints = new Set<number>([0, excerpt.length]);
  for (const range of ranges) {
    breakpoints.add(range.start);
    breakpoints.add(range.end);
  }
  const sorted = Array.from(breakpoints).sort((a, b) => a - b);

  const nodes: ReactNode[] = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];
    if (start === end) {
      continue;
    }
    const text = excerpt.slice(start, end);
    const mid = (start + end) / 2;
    const { gold, models } = segmentFlags(mid, ranges);

    let className = "";
    if (gold && models.length > 0) {
      className = OVERLAP_CLASS;
    } else if (gold) {
      className = GOLD_CLASS;
    } else if (models.length === 1) {
      className = modelColorClass(models[0], modelOrder);
    } else if (models.length > 1) {
      className = OVERLAP_CLASS;
    }

    if (className) {
      nodes.push(
        <mark key={`${start}-${end}`} className={`${className} px-0.5 rounded-sm`}>
          {text}
        </mark>,
      );
    } else {
      nodes.push(<span key={`${start}-${end}`}>{text}</span>);
    }
  }

  return (
    <div className="font-mono text-xs leading-relaxed whitespace-pre-wrap break-words border border-neutral-300 bg-neutral-50 p-3 max-h-[32rem] overflow-y-auto">
      {nodes}
    </div>
  );
}
