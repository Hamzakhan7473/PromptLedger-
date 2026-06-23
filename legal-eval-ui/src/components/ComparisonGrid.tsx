"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  classifyOutcome,
  modelsDisagreeOnPresence,
  OUTCOME_CELL_CLASS,
  OUTCOME_LABELS,
  OUTCOME_LEGEND_CLASS,
  OUTCOME_SHORT,
  type OutcomeBucket,
} from "@/lib/classifyOutcome";
import { harnessBucketToOutcome } from "@/lib/errorBuckets";
import type { EvalRun } from "@/lib/types";

const ALL_BUCKETS: OutcomeBucket[] = [
  "correct",
  "wrong_span",
  "false_present",
  "missed",
  "parse_fail",
];

interface GridRow {
  exampleId: string;
  category: string;
  goldPresent: boolean;
  cells: ReturnType<typeof classifyOutcome>[];
}

function buildGridRows(run: EvalRun): GridRow[] {
  return run.examples.map((example) => ({
    exampleId: example.id,
    category: example.category,
    goldPresent: example.present,
    cells: run.models.map((model) =>
      classifyOutcome(example, run.rawByExample[example.id]?.[model] ?? null),
    ),
  }));
}

export function ComparisonGrid({ run }: { run: EvalRun }) {
  const searchParams = useSearchParams();
  const bucketParam = searchParams.get("bucket");
  const modelParam = searchParams.get("model");

  const initialOutcome =
    bucketParam && harnessBucketToOutcome(bucketParam)
      ? harnessBucketToOutcome(bucketParam)!
      : "all";
  const initialModel =
    modelParam && run.models.includes(modelParam) ? modelParam : "all";

  const [category, setCategory] = useState<string>("all");
  const [outcomeFilter, setOutcomeFilter] = useState<OutcomeBucket | "all">(
    initialOutcome,
  );
  const [modelFilter, setModelFilter] = useState<string>(initialModel);
  const [disagreementsOnly, setDisagreementsOnly] = useState(false);

  useEffect(() => {
    const mapped = bucketParam ? harnessBucketToOutcome(bucketParam) : null;
    if (mapped) {
      setOutcomeFilter(mapped);
    }
    if (modelParam && run.models.includes(modelParam)) {
      setModelFilter(modelParam);
    }
  }, [bucketParam, modelParam, run.models]);

  const categories = useMemo(() => {
    const set = new Set(run.examples.map((ex) => ex.category));
    return Array.from(set).sort();
  }, [run.examples]);

  const allRows = useMemo(() => buildGridRows(run), [run]);

  const filteredRows = useMemo(() => {
    return allRows.filter((row) => {
      if (category !== "all" && row.category !== category) {
        return false;
      }
      if (disagreementsOnly && !modelsDisagreeOnPresence(row.cells)) {
        return false;
      }
      if (
        outcomeFilter !== "all" &&
        modelFilter !== "all"
      ) {
        const modelIdx = run.models.indexOf(modelFilter);
        if (modelIdx === -1 || row.cells[modelIdx]?.bucket !== outcomeFilter) {
          return false;
        }
      } else if (
        outcomeFilter !== "all" &&
        !row.cells.some((cell) => cell.bucket === outcomeFilter)
      ) {
        return false;
      }
      return true;
    });
  }, [allRows, category, disagreementsOnly, modelFilter, outcomeFilter, run.models]);

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <div className="border-b border-neutral-300 px-3 py-2 bg-white flex flex-wrap items-center gap-x-4 gap-y-2 text-xs shrink-0">
        <label className="flex items-center gap-1.5">
          <span className="text-neutral-600">category</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="border border-neutral-300 px-1.5 py-0.5 font-mono bg-white"
          >
            <option value="all">all</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-1.5">
          <span className="text-neutral-600">model</span>
          <select
            value={modelFilter}
            onChange={(e) => setModelFilter(e.target.value)}
            className="border border-neutral-300 px-1.5 py-0.5 font-mono bg-white"
          >
            <option value="all">all</option>
            {run.models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-1.5">
          <span className="text-neutral-600">outcome</span>
          <select
            value={outcomeFilter}
            onChange={(e) =>
              setOutcomeFilter(e.target.value as OutcomeBucket | "all")
            }
            className="border border-neutral-300 px-1.5 py-0.5 font-mono bg-white"
          >
            <option value="all">all</option>
            {ALL_BUCKETS.map((bucket) => (
              <option key={bucket} value={bucket}>
                {OUTCOME_LABELS[bucket]}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={disagreementsOnly}
            onChange={(e) => setDisagreementsOnly(e.target.checked)}
            className="rounded border-neutral-400"
          />
          <span className="text-neutral-700">disagreements only</span>
        </label>

        <span className="font-mono text-neutral-500 ml-auto">
          {filteredRows.length}/{allRows.length} rows
        </span>
      </div>

      <div className="px-3 py-1.5 border-b border-neutral-200 bg-neutral-50 flex flex-wrap gap-3 text-xs shrink-0">
        {ALL_BUCKETS.map((bucket) => (
          <span key={bucket} className="inline-flex items-center gap-1">
            <span
              className={`inline-block w-3 h-3 border ${OUTCOME_LEGEND_CLASS[bucket]}`}
            />
            <span className="font-mono">{OUTCOME_SHORT[bucket]}</span>
            <span className="text-neutral-500">{OUTCOME_LABELS[bucket]}</span>
          </span>
        ))}
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-xs">
          <thead className="sticky top-0 z-20 bg-neutral-100">
            <tr>
              <th className="sticky left-0 z-30 bg-neutral-100 border-b border-r border-neutral-300 px-2 py-1.5 text-left font-mono font-semibold min-w-[5.5rem]">
                id
              </th>
              <th className="sticky left-[5.5rem] z-30 bg-neutral-100 border-b border-r border-neutral-300 px-2 py-1.5 text-center font-semibold w-12">
                gold
              </th>
              {run.models.map((model) => (
                <th
                  key={model}
                  className="border-b border-neutral-300 px-1 py-1.5 text-center font-mono font-semibold min-w-[3rem]"
                >
                  {model}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.length === 0 ? (
              <tr>
                <td
                  colSpan={2 + run.models.length}
                  className="px-3 py-6 text-center text-neutral-500"
                >
                  No examples match filters.
                </td>
              </tr>
            ) : (
              filteredRows.map((row) => (
                <tr key={row.exampleId} className="group">
                  <td className="sticky left-0 z-10 bg-white group-hover:bg-neutral-50 border-b border-r border-neutral-200 px-2 py-1 font-mono align-top">
                    <div>{row.exampleId}</div>
                    <div className="text-neutral-500 truncate max-w-[8rem]">
                      {row.category}
                    </div>
                  </td>
                  <td className="sticky left-[5.5rem] z-10 bg-white group-hover:bg-neutral-50 border-b border-r border-neutral-200 px-2 py-1 text-center font-mono align-top">
                    <span
                      className={
                        row.goldPresent ? "text-green-800" : "text-neutral-500"
                      }
                    >
                      {row.goldPresent ? "Y" : "N"}
                    </span>
                  </td>
                  {row.cells.map((cell, idx) => {
                    const model = run.models[idx];
                    return (
                      <td
                        key={model}
                        className="border-b border-neutral-200 p-0.5 text-center align-top"
                      >
                        <Link
                          href={`/runs/${run.runId}/samples?example=${row.exampleId}`}
                          title={OUTCOME_LABELS[cell.bucket]}
                          className={`block font-mono px-1 py-1 border border-transparent ${OUTCOME_CELL_CLASS[cell.bucket]}`}
                        >
                          {OUTCOME_SHORT[cell.bucket]}
                        </Link>
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
