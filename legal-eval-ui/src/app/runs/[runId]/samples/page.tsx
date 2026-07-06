import { Suspense } from "react";

import { RunViewPage } from "@/components/RunViewPage";

function RunViewFallback() {
  return (
    <div className="h-screen flex items-center justify-center text-sm text-muted-foreground">
      Loading…
    </div>
  );
}

export default async function SamplesPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;
  return (
    <Suspense fallback={<RunViewFallback />}>
      <RunViewPage runId={runId} view="samples" />
    </Suspense>
  );
}
