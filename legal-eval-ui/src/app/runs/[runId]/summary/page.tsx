import { notFound } from "next/navigation";

import { RunNav } from "@/components/RunNav";
import { SummaryView } from "@/components/SummaryView";
import { loadRun } from "@/lib/loadRun";

export default async function SummaryPage({
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
        view="summary"
        kappa={run.judgeValidation.agreement.cohens_kappa}
      />
      <SummaryView run={run} />
    </div>
  );
}
