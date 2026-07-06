import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 no-underline">
          <span className="inline-flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary text-sm font-bold">
            LE
          </span>
          <span className="text-lg font-semibold text-foreground">Legal Eval</span>
        </Link>

        <nav className="flex items-center gap-3 sm:gap-4">
          <Link
            href="/dashboard"
            className="hidden text-sm text-muted-foreground hover:text-foreground sm:inline"
          >
            Workspace
          </Link>
          <Link
            href="/#pricing"
            className="hidden text-sm text-muted-foreground hover:text-foreground md:inline"
          >
            Free
          </Link>
          <span className="hidden text-sm text-muted-foreground sm:inline">EN</span>
          <Link href="/settings" className="btn-outline min-h-9 px-4 text-sm">
            Log in
          </Link>
        </nav>
      </div>
    </header>
  );
}
