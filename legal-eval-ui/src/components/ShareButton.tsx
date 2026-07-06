"use client";

import { useState } from "react";

import { createShareLink, type ShareLinkResponse } from "@/lib/api";

export function ShareButton({ runId }: { runId: string }) {
  const [link, setLink] = useState<ShareLinkResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleShare() {
    setError(null);
    try {
      const response = await createShareLink(runId);
      setLink(response);
      const full =
        typeof window !== "undefined"
          ? `${window.location.origin}${response.share_url}`
          : response.share_url;
      await navigator.clipboard.writeText(full);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create share link.");
    }
  }

  return (
    <div className="space-y-2">
      <button
        type="button"
        onClick={handleShare}
        className="px-3 py-2 text-sm btn-outline"
      >
        {copied ? "Link copied!" : "Copy share link"}
      </button>
      {link && (
        <p className="text-xs text-neutral-600 font-mono break-all">
          {link.share_url}
        </p>
      )}
      {error && <p className="text-xs text-red-700">{error}</p>}
    </div>
  );
}
