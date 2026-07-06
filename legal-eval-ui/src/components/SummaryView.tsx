import { CalibrationPanel } from "@/components/CalibrationPanel";
import { FailureTaxonomyChart } from "@/components/FailureTaxonomyChart";
import { ModelMetricsTable } from "@/components/ModelMetricsTable";
import { ProvenancePanel } from "@/components/ProvenancePanel";
import { TrustBanner } from "@/components/TrustBanner";
import type { EvalRun } from "@/lib/types";

export function SummaryView({
  run,
  shareToken,
}: {
  run: EvalRun;
  shareToken?: string;
}) {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-5xl mx-auto p-4 space-y-6">
        <ProvenancePanel run={run} />
        <TrustBanner validation={run.judgeValidation} />

        <section>
          <h2 className="text-xs font-semibold uppercase text-neutral-600 mb-2">
            Per-model metrics
          </h2>
          <ModelMetricsTable run={run} />
        </section>

        <section>
          <h2 className="text-xs font-semibold uppercase text-neutral-600 mb-2">
            Calibration (reliability)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {run.models.map((model) => {
              const cal = run.calibration.models[model];
              if (!cal) {
                return (
                  <div
                    key={model}
                    className="border border-neutral-300 p-3 text-xs text-neutral-500"
                  >
                    {model}: no calibration data
                  </div>
                );
              }
              return (
                <CalibrationPanel
                  key={model}
                  runId={run.runId}
                  model={model}
                  ece={cal.ece}
                  bins={cal.bins}
                  shareToken={shareToken}
                />
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="text-xs font-semibold uppercase text-neutral-600 mb-2">
            Failure taxonomy
          </h2>
          <div className="border border-neutral-300 p-3 bg-white">
            <FailureTaxonomyChart run={run} />
          </div>
        </section>
      </div>
    </div>
  );
}
