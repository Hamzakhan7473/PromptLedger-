import {
  extractProvenance,
  formatProvenanceTimestamp,
  type ProvenanceInfo,
} from "@/lib/provenance";
import type { EvalRun } from "@/lib/types";

function SeedList({ seeds }: { seeds: Record<string, number> }) {
  const entries = Object.entries(seeds).sort(([a], [b]) => a.localeCompare(b));
  if (entries.length === 0) {
    return <span className="font-mono text-xs">—</span>;
  }
  return (
    <ul className="space-y-1">
      {entries.map(([key, value]) => (
        <li key={key} className="font-mono text-xs">
          <span className="text-muted-foreground">{key}:</span> {value}
        </li>
      ))}
    </ul>
  );
}

function ModelPinList({ models }: { models: ProvenanceInfo["pinnedModels"] }) {
  if (models.length === 0) {
    return <span className="font-mono text-xs">—</span>;
  }
  return (
    <ul className="space-y-1.5">
      {models.map((model) => (
        <li key={model.name} className="font-mono text-xs">
          <span className="font-semibold text-foreground">{model.name}</span>
          <span className="text-muted-foreground"> → </span>
          {model.modelId}
        </li>
      ))}
    </ul>
  );
}

export function ProvenancePanel({ run }: { run: EvalRun }) {
  const provenance = extractProvenance(run);

  return (
    <section className="rounded-xl border-2 border-primary/25 bg-gradient-to-br from-primary/10 via-background to-background p-5 sm:p-6 shadow-sm">
      <div className="mb-4 space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
          Reproducibility &amp; provenance
        </p>
        <p className="max-w-3xl text-sm leading-relaxed text-muted-foreground">
          Pinned models, hashed dataset, and fixed seeds — the audit trail procurement teams
          expect before trusting your extraction pipeline.
        </p>
      </div>

      <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-sm">
        <div className="space-y-1 rounded-lg border border-border/80 bg-background/80 p-3">
          <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Run
          </dt>
          <dd className="font-mono text-xs break-all">{provenance.runId}</dd>
          <dd className="text-xs text-muted-foreground">
            {formatProvenanceTimestamp(provenance.runDateUtc)}
          </dd>
        </div>

        <div className="space-y-1 rounded-lg border border-border/80 bg-background/80 p-3 sm:col-span-2 lg:col-span-1">
          <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Dataset
          </dt>
          <dd className="font-mono text-xs break-all">{provenance.datasetPath}</dd>
          <dd className="font-mono text-[11px] text-muted-foreground break-all">
            SHA-256: {provenance.datasetSha256}
          </dd>
        </div>

        <div className="space-y-1 rounded-lg border border-border/80 bg-background/80 p-3">
          <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Seeds
          </dt>
          <dd>
            <SeedList seeds={provenance.seeds} />
          </dd>
        </div>

        <div className="space-y-1 rounded-lg border border-border/80 bg-background/80 p-3 sm:col-span-2">
          <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Pinned model IDs
          </dt>
          <dd>
            <ModelPinList models={provenance.pinnedModels} />
          </dd>
          {provenance.judgeModelId && (
            <dd className="mt-2 font-mono text-xs text-muted-foreground">
              Judge: {provenance.judgeModelId}
            </dd>
          )}
        </div>
      </dl>
    </section>
  );
}
