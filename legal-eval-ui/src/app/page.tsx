import Link from "next/link";

import { listRunIds } from "@/lib/loadRun";

export default function HomePage() {
  const runs = listRunIds();

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-lg font-semibold mb-1">legal-eval-ui</h1>
      <p className="text-sm text-neutral-600 mb-6">
        Static reader for legal-eval harness output. Copy a run into{" "}
        <code className="text-xs bg-neutral-100 px-1">public/results/&lt;run_id&gt;/</code>.
      </p>

      {runs.length === 0 ? (
        <p className="text-sm text-neutral-500 border border-neutral-300 p-4">
          No runs found. Copy harness output to{" "}
          <code className="text-xs">public/results/</code> (see README).
        </p>
      ) : (
        <ul className="border border-neutral-300 divide-y divide-neutral-200">
          {runs.map((runId) => (
            <li key={runId} className="px-4 py-3 hover:bg-neutral-50">
              <div className="text-sm font-mono">{runId}</div>
              <div className="flex gap-3 mt-1 text-xs">
                <Link
                  href={`/runs/${runId}/summary`}
                  className="text-neutral-700 hover:text-neutral-900 underline"
                >
                  Summary
                </Link>
                <Link
                  href={`/runs/${runId}/samples`}
                  className="text-neutral-700 hover:text-neutral-900 underline"
                >
                  Sample Viewer
                </Link>
                <Link
                  href={`/runs/${runId}/grid`}
                  className="text-neutral-700 hover:text-neutral-900 underline"
                >
                  Comparison Grid
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
