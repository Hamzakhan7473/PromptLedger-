export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-background px-4 py-10 sm:px-6">
      <div className="mx-auto max-w-6xl space-y-4 text-center sm:text-left">
        <p className="text-xs text-muted-foreground max-w-2xl">
          Evaluation metrics support product and procurement decisions — not professional legal advice.
        </p>
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} Legal Eval. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
