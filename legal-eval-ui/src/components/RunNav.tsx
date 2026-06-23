import Link from "next/link";

export function RunNav({
  runId,
  view,
  kappa,
}: {
  runId: string;
  view: "samples" | "grid" | "summary";
  kappa?: number | null;
}) {
  const tabClass = (active: boolean) =>
    `px-2 py-1 border ${
      active
        ? "border-neutral-500 bg-white font-semibold text-neutral-900"
        : "border-transparent text-neutral-600 hover:text-neutral-900"
    }`;

  return (
    <nav className="h-12 border-b border-neutral-300 px-4 flex items-center gap-3 text-xs bg-neutral-100 shrink-0">
      <Link href="/" className="text-neutral-600 hover:text-neutral-900">
        ← runs
      </Link>
      <span className="text-neutral-300">|</span>
      <Link href={`/runs/${runId}/summary`} className={tabClass(view === "summary")}>
        Summary
      </Link>
      <Link href={`/runs/${runId}/samples`} className={tabClass(view === "samples")}>
        Sample Viewer
      </Link>
      <Link href={`/runs/${runId}/grid`} className={tabClass(view === "grid")}>
        Comparison Grid
      </Link>
      <span className="font-mono text-neutral-500">{runId}</span>
      {kappa != null && (
        <span className="ml-auto font-mono text-neutral-600">
          judge κ={kappa.toFixed(3)}
        </span>
      )}
    </nav>
  );
}
