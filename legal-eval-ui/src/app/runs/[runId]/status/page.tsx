"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { PdfExportButton } from "@/components/PdfExportButton";
import { ShareButton } from "@/components/ShareButton";
import { fetchRun, type RunSummary } from "@/lib/api";

export default function RunStatusPage() {
  const params = useParams();
  const runId = String(params.runId ?? "");
  const [run, setRun] = useState<RunSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    let cancelled = false;

    async function poll() {
      try {
        const next = await fetchRun(runId);
        if (cancelled) return;
        setRun(next);
        setError(null);
        if (next.status === "queued" || next.status === "running") {
          window.setTimeout(poll, 3000);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load run.");
        }
      }
    }

    poll();
    return () => {
      cancelled = true;
    };
  }, [runId]);

  const status = run?.status ?? "…";

  return (
    <AppShell title="Eval run" description={runId} backHref="/dashboard">
      <div className="card-surface p-6 space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-wide text-muted-foreground">Status</span>
          <StatusBadge status={status} />
        </div>

        {run?.mode && (
          <p className="text-sm text-foreground">
            Mode:{" "}
            <span className="font-mono text-muted-foreground">
              {run.mode === "agent" ? "agent harness" : "direct eval"}
            </span>
          </p>
        )}

        {run?.models && (
          <p className="text-sm text-foreground">
            Models:{" "}
            <span className="font-mono text-muted-foreground">{run.models.join(", ")}</span>
          </p>
        )}

        {(status === "queued" || status === "running") && (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {run?.mode === "agent"
              ? "Agent harness running — extract/validate subagents per example, then metrics, judge, and report."
              : "Pipeline running — metrics, judge, calibration, and report."}{" "}
            This can take several minutes for large datasets.
          </p>
        )}

        {run?.error && (
          <p className="text-sm text-red-700 border border-red-200 bg-red-50 rounded-lg p-3">
            {run.error}
          </p>
        )}

        {error && (
          <p className="text-sm text-red-700 border border-red-200 bg-red-50 rounded-lg p-3">
            {error}
          </p>
        )}

        {status === "completed" && (
          <div className="flex flex-col gap-3 pt-2">
            <Link href={`/runs/${runId}/summary`} className="btn-primary w-fit">
              View results
            </Link>
            <ShareButton runId={runId} />
            <PdfExportButton runId={runId} />
          </div>
        )}
      </div>
    </AppShell>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    queued: "bg-amber-100 text-amber-900",
    running: "bg-blue-100 text-blue-900",
    completed: "bg-primary/15 text-primary",
    failed: "bg-red-100 text-red-900",
  };
  return (
    <span
      className={`text-xs font-medium px-2.5 py-1 rounded-full ${styles[status] ?? "bg-muted"}`}
    >
      {status}
    </span>
  );
}
