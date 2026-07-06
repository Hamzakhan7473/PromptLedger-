import Link from "next/link";

function withShareToken(path: string, shareToken?: string) {
  if (!shareToken) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}token=${encodeURIComponent(shareToken)}`;
}

export function RunNav({
  runId,
  view,
  kappa,
  shareToken,
}: {
  runId: string;
  view: "samples" | "grid" | "summary";
  kappa?: number | null;
  shareToken?: string;
}) {
  const tabClass = (active: boolean) =>
    `px-3 py-1.5 rounded-lg text-sm transition-colors ${
      active
        ? "bg-primary/10 text-primary font-medium"
        : "text-muted-foreground hover:text-foreground hover:bg-muted"
    }`;

  return (
    <nav className="h-14 border-b border-border px-4 sm:px-6 flex items-center gap-3 text-sm bg-background/90 backdrop-blur-md shrink-0">
      <Link href="/dashboard" className="text-muted-foreground hover:text-foreground text-xs">
        ← Workspace
      </Link>
      <span className="text-border">|</span>
      <Link href={withShareToken(`/runs/${runId}/summary`, shareToken)} className={tabClass(view === "summary")}>
        Summary
      </Link>
      <Link href={withShareToken(`/runs/${runId}/samples`, shareToken)} className={tabClass(view === "samples")}>
        Samples
      </Link>
      <Link href={withShareToken(`/runs/${runId}/grid`, shareToken)} className={tabClass(view === "grid")}>
        Grid
      </Link>
      <span className="hidden sm:inline font-mono text-xs text-muted-foreground truncate max-w-[12rem]">
        {runId}
      </span>
      {kappa != null && (
        <span className="ml-auto font-mono text-xs text-muted-foreground">
          judge κ={kappa.toFixed(3)}
        </span>
      )}
    </nav>
  );
}
