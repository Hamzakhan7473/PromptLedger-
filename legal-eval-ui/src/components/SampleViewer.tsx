"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { HighlightedExcerpt, modelColorClass } from "@/lib/highlightSpans";
import { scoreExample } from "@/lib/scoreExample";
import type {
  EvalExample,
  EvalRun,
  JudgeDecisionRow,
  ModelExampleView,
  RawLogRow,
} from "@/lib/types";

function buildModelViews(
  example: EvalExample,
  run: EvalRun,
): ModelExampleView[] {
  return run.models.map((model) => {
    const row: RawLogRow | null = run.rawByExample[example.id]?.[model] ?? null;
    const prediction = row?.parsed ?? null;
    const hasError = Boolean(row?.error || row?.parse_error);
    const score = scoreExample(example, prediction, hasError);
    const hallucinated = Boolean(
      prediction?.present &&
        prediction.span &&
        !example.contract_excerpt.includes(prediction.span),
    );
    const judge: JudgeDecisionRow | null =
      run.judgeByExample[example.id]?.[model] ?? null;

    return { model, row, prediction, score, hallucinated, judge };
  });
}

function ScoreBadge({ correct, label }: { correct: boolean | null; label: string }) {
  if (correct === null) {
    return (
      <span className="text-neutral-500 text-xs font-mono">{label}</span>
    );
  }
  return (
    <span
      className={`text-xs font-mono px-1.5 py-0.5 border ${
        correct
          ? "border-green-700 text-green-800 bg-green-50"
          : "border-red-700 text-red-800 bg-red-50"
      }`}
    >
      {label}
    </span>
  );
}

export function SampleViewer({ run }: { run: EvalRun }) {
  const searchParams = useSearchParams();
  const exampleFromUrl = searchParams.get("example");
  const [selectedId, setSelectedId] = useState(
    exampleFromUrl && run.examples.some((ex) => ex.id === exampleFromUrl)
      ? exampleFromUrl
      : (run.examples[0]?.id ?? ""),
  );

  useEffect(() => {
    if (
      exampleFromUrl &&
      run.examples.some((ex) => ex.id === exampleFromUrl)
    ) {
      setSelectedId(exampleFromUrl);
    }
  }, [exampleFromUrl, run.examples]);

  const selected = useMemo(
    () => run.examples.find((ex) => ex.id === selectedId) ?? run.examples[0],
    [run.examples, selectedId],
  );

  const modelViews = useMemo(
    () => (selected ? buildModelViews(selected, run) : []),
    [selected, run],
  );

  const predictedByModel = useMemo(() => {
    const map: Record<string, string | null> = {};
    for (const view of modelViews) {
      map[view.model] = view.prediction?.span ?? null;
    }
    return map;
  }, [modelViews]);

  if (!selected) {
    return (
      <p className="text-sm text-neutral-600">No examples in eval set.</p>
    );
  }

  return (
    <div className="flex flex-1 min-h-0 border-t border-neutral-300">
      <aside className="w-72 shrink-0 border-r border-neutral-300 overflow-y-auto bg-white">
        <div className="px-3 py-2 border-b border-neutral-300 bg-neutral-100">
          <h2 className="text-xs font-semibold uppercase tracking-wide text-neutral-600">
            Examples ({run.examples.length})
          </h2>
          <p className="text-xs text-neutral-500 font-mono mt-0.5">{run.runId}</p>
        </div>
        <ul className="divide-y divide-neutral-200">
          {run.examples.map((example) => (
            <li key={example.id}>
              <button
                type="button"
                onClick={() => setSelectedId(example.id)}
                className={`w-full text-left px-3 py-2 hover:bg-neutral-50 ${
                  example.id === selected.id ? "bg-neutral-100" : ""
                }`}
              >
                <div className="font-mono text-xs text-neutral-800">{example.id}</div>
                <div className="text-xs text-neutral-600 truncate mt-0.5">
                  {example.category}
                </div>
                <div className="text-xs font-mono mt-1">
                  <span
                    className={
                      example.present
                        ? "text-green-800"
                        : "text-neutral-500"
                    }
                  >
                    gold: {example.present ? "present" : "absent"}
                  </span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <main className="flex-1 overflow-y-auto p-4 bg-white">
        <header className="mb-4 border-b border-neutral-200 pb-3">
          <h1 className="text-sm font-semibold font-mono">{selected.id}</h1>
          <p className="text-xs text-neutral-600 mt-1">
            <span className="font-medium">{selected.category}</span>
            {" · "}
            {selected.contract_title}
          </p>
          <p className="text-xs font-mono mt-1">
            gold present={String(selected.present)}
            {selected.gold_spans.length > 0 && (
              <span className="text-neutral-500">
                {" "}
                · {selected.gold_spans.length} gold span
                {selected.gold_spans.length > 1 ? "s" : ""}
              </span>
            )}
          </p>
        </header>

        <section className="mb-4">
          <h2 className="text-xs font-semibold uppercase text-neutral-600 mb-2">
            Contract excerpt
          </h2>
          <div className="flex flex-wrap gap-3 mb-2 text-xs">
            <span className="inline-flex items-center gap-1">
              <span className={`inline-block w-3 h-3 rounded-sm ${"bg-amber-200"}`} />
              gold span
            </span>
            {run.models.map((model) => (
              <span key={model} className="inline-flex items-center gap-1 font-mono">
                <span
                  className={`inline-block w-3 h-3 rounded-sm ${modelColorClass(model, run.models).split(" ")[0]}`}
                />
                {model}
              </span>
            ))}
            <span className="inline-flex items-center gap-1">
              <span className={`inline-block w-3 h-3 rounded-sm ${"bg-teal-300 ring-1 ring-teal-700"}`} />
              overlap
            </span>
          </div>
          <HighlightedExcerpt
            excerpt={selected.contract_excerpt}
            goldSpans={selected.gold_spans}
            predictedByModel={predictedByModel}
            modelOrder={run.models}
          />
        </section>

        <section>
          <h2 className="text-xs font-semibold uppercase text-neutral-600 mb-2">
            Model predictions
          </h2>
          <div className="space-y-3">
            {modelViews.map((view) => (
              <div
                key={view.model}
                className="border border-neutral-300 p-3 bg-neutral-50"
              >
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className="font-mono text-sm font-semibold">{view.model}</span>
                  <ScoreBadge
                    correct={view.score.presenceCorrect}
                    label={`presence: ${view.score.presenceLabel}`}
                  />
                  {view.score.spanLabel !== "—" && (
                    <span
                      className={`text-xs font-mono px-1.5 py-0.5 border ${
                        view.hallucinated
                          ? "border-red-800 bg-red-100 text-red-900"
                          : "border-neutral-400 text-neutral-700"
                      }`}
                    >
                      span: {view.score.spanLabel}
                    </span>
                  )}
                  {view.prediction && (
                    <span className="text-xs font-mono text-neutral-600">
                      conf={view.prediction.confidence.toFixed(2)}
                    </span>
                  )}
                </div>

                {view.row?.error && (
                  <p className="text-xs font-mono text-red-800 mb-2">
                    API error: {view.row.error}
                  </p>
                )}
                {view.row?.parse_error && (
                  <p className="text-xs font-mono text-red-800 mb-2">
                    Parse error: {view.row.parse_error}
                  </p>
                )}

                {view.prediction ? (
                  <dl className="text-xs font-mono grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
                    <dt className="text-neutral-500">present</dt>
                    <dd>{String(view.prediction.present)}</dd>
                    <dt className="text-neutral-500">span</dt>
                    <dd className="break-words whitespace-pre-wrap">
                      {view.prediction.span ?? "null"}
                      {view.hallucinated && (
                        <span className="block mt-1 text-red-900 font-semibold">
                          ⚠ NOT A SUBSTRING OF EXCERPT (hallucinated)
                        </span>
                      )}
                    </dd>
                    <dt className="text-neutral-500">reasoning</dt>
                    <dd className="break-words text-neutral-800 font-sans text-xs leading-snug">
                      {view.prediction.reasoning}
                    </dd>
                  </dl>
                ) : (
                  <p className="text-xs text-neutral-500">No parsed prediction.</p>
                )}

                {view.judge && view.judge.span_correct !== null && (
                  <div className="mt-3 pt-3 border-t border-neutral-300">
                    <p className="text-xs font-semibold uppercase text-neutral-600 mb-1">
                      Judge adjudication
                    </p>
                    <p className="text-xs font-mono">
                      span_correct=
                      <span
                        className={
                          view.judge.span_correct
                            ? "text-green-800"
                            : "text-red-800"
                        }
                      >
                        {String(view.judge.span_correct)}
                      </span>
                      {" · "}
                      jaccard={view.judge.token_jaccard.toFixed(3)}
                    </p>
                    {view.judge.rationale && (
                      <p className="text-xs text-neutral-800 mt-1 leading-snug">
                        {view.judge.rationale}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
