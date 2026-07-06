import Link from "next/link";

import { SiteFooter } from "@/components/marketing/SiteFooter";
import { SiteHeader } from "@/components/marketing/SiteHeader";

export function AppShell({
  children,
  title,
  description,
  backHref = "/dashboard",
  backLabel = "← Workspace",
}: {
  children: React.ReactNode;
  title: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
}) {
  return (
    <div className="public-light-shell min-h-screen flex flex-col">
      <SiteHeader />
      <main className="flex-1 px-4 py-8 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <Link
            href={backHref}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            {backLabel}
          </Link>
          <h1 className="editorial-headline mt-3 text-2xl font-semibold sm:text-3xl">
            {title}
          </h1>
          {description && (
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {description}
            </p>
          )}
          <div className="mt-8">{children}</div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}

export function AppShellWide({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`public-light-shell min-h-screen flex flex-col ${className}`}>
      <SiteHeader />
      <main className="flex-1">{children}</main>
    </div>
  );
}
