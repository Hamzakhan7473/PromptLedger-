import {
  extractModelMetrics,
  formatF1WithCi,
  formatRate,
} from "@/lib/parseMetrics";
import type { EvalRun } from "@/lib/types";

export function ModelMetricsTable({ run }: { run: EvalRun }) {
  const rows = extractModelMetrics(run);

  return (
    <div className="overflow-x-auto border border-neutral-300">
      <table className="w-full text-xs border-collapse">
        <thead className="bg-neutral-100">
          <tr>
            <th className="text-left px-3 py-2 border-b border-neutral-300 font-semibold">
              model
            </th>
            <th className="text-left px-3 py-2 border-b border-neutral-300 font-semibold">
              presence F1 [95% CI]
            </th>
            <th className="text-right px-3 py-2 border-b border-neutral-300 font-semibold">
              span Jaccard
            </th>
            <th className="text-right px-3 py-2 border-b border-neutral-300 font-semibold">
              halluc. rate
            </th>
            <th className="text-right px-3 py-2 border-b border-neutral-300 font-semibold">
              parse rate
            </th>
            <th className="text-right px-3 py-2 border-b border-neutral-300 font-semibold">
              ECE
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.model} className="border-b border-neutral-200">
              <td className="px-3 py-2 font-mono">{row.model}</td>
              <td className="px-3 py-2 font-mono">
                {formatF1WithCi(row.presenceF1, row.f1CiLow, row.f1CiHigh)}
              </td>
              <td className="px-3 py-2 font-mono text-right">
                {formatRate(row.meanJaccard)}
              </td>
              <td className="px-3 py-2 font-mono text-right">
                {formatRate(row.hallucinationRate)}
              </td>
              <td className="px-3 py-2 font-mono text-right">
                {formatRate(row.parseRate)}
              </td>
              <td className="px-3 py-2 font-mono text-right">
                {formatRate(row.ece)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
