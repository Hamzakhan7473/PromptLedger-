"use client";

import { useEffect, useState } from "react";

import { fetchOrgStats, type OrgStats } from "@/lib/api";
import { hasOrgApiKey } from "@/lib/orgAuth";

export function OrgDashboard() {
  const [stats, setStats] = useState<OrgStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!hasOrgApiKey()) return;
    fetchOrgStats()
      .then(setStats)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (!hasOrgApiKey()) return null;
  if (error) {
    return (
      <p className="text-xs text-muted-foreground card-surface p-4">
        Dashboard unavailable ({error}).
      </p>
    );
  }
  if (!stats) return null;

  const successPct =
    stats.success_rate != null ? `${(stats.success_rate * 100).toFixed(1)}%` : "—";
  const avgMin =
    stats.avg_duration_seconds != null
      ? `${Math.round(stats.avg_duration_seconds / 60)}m`
      : "—";

  return (
    <section className="card-surface p-6">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-4">
        Org dashboard
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Stat label="Total runs" value={String(stats.total_runs)} />
        <Stat label="Success rate" value={successPct} />
        <Stat label="Last 7 days" value={String(stats.runs_last_7_days)} />
        <Stat label="Avg duration" value={avgMin} />
        <Stat label="Eval runs" value={String(stats.eval_runs)} />
        <Stat label="Agent runs" value={String(stats.agent_runs)} />
        <Stat label="Running" value={String(stats.running_runs)} />
        <Stat label="Failed" value={String(stats.failed_runs)} />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-background/80 px-3 py-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-xl font-semibold tabular-nums mt-1 text-foreground">{value}</p>
    </div>
  );
}
