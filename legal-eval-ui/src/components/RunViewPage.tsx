"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SiteHeader } from "@/components/marketing/SiteHeader";
import { ComparisonGrid } from "@/components/ComparisonGrid";
import { RunNav } from "@/components/RunNav";
import { SampleViewer } from "@/components/SampleViewer";
import { SummaryView } from "@/components/SummaryView";
import { loadRun } from "@/lib/loadRun";
import type { EvalRun } from "@/lib/types";

type RunView = "summary" | "grid" | "samples";

export function RunViewPage({ runId, view }: { runId: string; view: RunView }) {
  const searchParams = useSearchParams();
  const shareToken = searchParams.get("token") ?? undefined;
  const [run, setRun] = useState<EvalRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    loadRun(runId, { shareToken })
      .then((data) => {
        if (!cancelled) {
          setRun(data);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setRun(null);
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [runId, shareToken]);

  if (loading) {
    return (
      <div className="h-screen flex flex-col bg-background">
        <SiteHeader />
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
          Loading run…
        </div>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="h-screen flex flex-col bg-background">
        <SiteHeader />
        <div className="flex-1 flex flex-col items-center justify-center gap-2 px-4 text-center">
          <p className="text-sm text-red-700">Could not load run: {error ?? "Not found"}</p>
          <p className="text-xs text-muted-foreground">
            Sign in via Settings if this is your run. Demo runs use a share link — no account required.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <SiteHeader />
      <RunNav
        runId={runId}
        view={view}
        kappa={run.judgeValidation.agreement.cohens_kappa}
        shareToken={shareToken}
      />
      {view === "summary" && <SummaryView run={run} shareToken={shareToken} />}
      {view === "grid" && <ComparisonGrid run={run} />}
      {view === "samples" && <SampleViewer run={run} />}
    </div>
  );
}
