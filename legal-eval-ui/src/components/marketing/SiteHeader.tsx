"use client";

import Link from "next/link";

import { useAuth } from "@/components/AuthProvider";

export function SiteHeader() {
  const { user, loading, signOut } = useAuth();

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
          {!loading && user && (
            <Link
              href="/dashboard"
              className="hidden text-sm text-muted-foreground hover:text-foreground sm:inline"
            >
              Workspace
            </Link>
          )}
          <Link
            href="/#pricing"
            className="hidden text-sm text-muted-foreground hover:text-foreground md:inline"
          >
            Free
          </Link>
          <span className="hidden text-sm text-muted-foreground sm:inline">EN</span>
          {!loading && !user && (
            <>
              <Link href="/sign-in" className="btn-outline min-h-9 px-4 text-sm">
                Log in
              </Link>
              <Link
                href="/sign-up"
                className="btn-primary min-h-9 px-4 text-sm hidden sm:inline-flex"
              >
                Sign up
              </Link>
            </>
          )}
          {!loading && user && (
            <div className="flex items-center gap-2">
              <span className="hidden text-xs text-muted-foreground sm:inline max-w-[140px] truncate">
                {user.email}
              </span>
              <button
                type="button"
                onClick={() => void signOut()}
                className="btn-outline min-h-9 px-3 text-sm"
              >
                Sign out
              </button>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
