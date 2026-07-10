"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchRuns, type RunMode, type RunSummary } from "@/lib/api";

export function HomeRunList() {
  const [apiRuns, setApiRuns] = useState<RunSummary[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns()
      .then(setApiRuns)
      .catch((err: Error) => setApiError(err.message));
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          Evaluation workspace — upload your JSONL eval set, compare providers, and export
          reproducible evidence for stakeholders.
        </p>
        <div className="flex flex-wrap gap-2">
          <Link href="/audit" className="btn-outline min-h-9 px-4 text-sm">
            Audit log
          </Link>
          <Link href="/settings" className="btn-outline min-h-9 px-4 text-sm">
            Settings
          </Link>
          <Link href="/new" className="btn-primary min-h-9 px-4 text-sm">
            + New eval
          </Link>
        </div>
      </div>

      {apiError && (
        <p className="text-xs text-muted-foreground card-surface p-4">
          Could not reach the API ({apiError}). Check your connection or try again later.
        </p>
      )}

      <section>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Your runs
        </h2>
        {apiRuns.length === 0 && !apiError ? (
          <p className="text-sm text-muted-foreground card-surface p-6">
            No runs yet.{" "}
            <Link href="/new" className="text-primary hover:underline">
              Start a new eval
            </Link>
            .
          </p>
        ) : (
          <RunList
            runs={apiRuns.map((r) => ({
              id: r.run_id,
              status: r.status,
              mode: r.mode,
            }))}
          />
        )}
      </section>
    </div>
  );
}

function RunList({
  runs,
}: {
  runs: {
    id: string;
    status: RunSummary["status"] | "completed";
    mode?: RunMode;
  }[];
}) {
  return (
    <ul className="card-surface divide-y divide-border overflow-hidden">
      {runs.map((run) => (
        <li key={run.id} className="px-4 py-4 hover:bg-muted/40 transition-colors">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-mono text-foreground">{run.id}</span>
            {run.mode === "agent" && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                agent
              </span>
            )}
            {run.status !== "completed" && (
              <Link
                href={`/runs/${run.id}/status`}
                className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-medium"
              >
                {run.status}
              </Link>
            )}
          </div>
          <div className="flex flex-wrap gap-4 mt-2 text-sm">
            {run.status === "completed" ? (
              <>
                <Link href={`/runs/${run.id}/summary`} className="text-primary hover:underline">
                  Summary
                </Link>
                <Link href={`/runs/${run.id}/samples`} className="text-muted-foreground hover:text-foreground">
                  Sample Viewer
                </Link>
                <Link href={`/runs/${run.id}/grid`} className="text-muted-foreground hover:text-foreground">
                  Comparison Grid
                </Link>
              </>
            ) : (
              <Link href={`/runs/${run.id}/status`} className="text-primary hover:underline">
                View status
              </Link>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
