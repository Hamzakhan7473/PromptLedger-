"use client";

import { useState } from "react";

import { downloadRunPdf } from "@/lib/api";

export function PdfExportButton({ runId }: { runId: string }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleExport() {
    setLoading(true);
    setError(null);
    try {
      await downloadRunPdf(runId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDF export failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={handleExport}
        disabled={loading}
        title="Download a shareable trust report with provenance, headline metrics, and full eval details."
        className="btn-outline min-h-9 px-4 text-sm disabled:opacity-50 w-fit"
      >
        {loading ? "Exporting…" : "Export shareable report"}
      </button>
      {error && <p className="text-xs text-red-700">{error}</p>}
    </div>
  );
}
