import { Suspense } from "react";
import { notFound } from "next/navigation";

import { ComparisonGrid } from "@/components/ComparisonGrid";
import { RunNav } from "@/components/RunNav";
import { loadRun } from "@/lib/loadRun";

export default async function GridPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  let run;
  try {
    run = loadRun(runId);
  } catch {
    notFound();
  }

  return (
    <div className="h-screen flex flex-col">
      <RunNav
        runId={runId}
        view="grid"
        kappa={run.judgeValidation.agreement.cohens_kappa}
      />
      <Suspense
        fallback={
          <div className="flex-1 flex items-center justify-center text-xs text-neutral-500">
            Loading…
          </div>
        }
      >
        <ComparisonGrid run={run} />
      </Suspense>
    </div>
  );
}
