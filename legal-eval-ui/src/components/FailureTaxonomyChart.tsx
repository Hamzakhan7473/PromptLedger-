"use client";

import { useRouter } from "next/navigation";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  HARNESS_BUCKET_LABELS,
  HARNESS_ERROR_BUCKETS,
  type HarnessErrorBucket,
} from "@/lib/errorBuckets";
import type { EvalRun } from "@/lib/types";

const MODEL_BAR_COLORS = ["#525252", "#737373", "#404040", "#a3a3a3", "#171717"];

function buildChartData(run: EvalRun) {
  return HARNESS_ERROR_BUCKETS.map((bucket) => {
    const row: Record<string, string | number> = {
      bucket,
      label: HARNESS_BUCKET_LABELS[bucket],
    };
    for (const model of run.models) {
      const counts =
        run.errorsSummary.models[model]?.counts_by_bucket ?? {};
      row[model] = counts[bucket] ?? 0;
    }
    return row;
  });
}

export function FailureTaxonomyChart({ run }: { run: EvalRun }) {
  const router = useRouter();
  const data = buildChartData(run);

  const handleBarClick = (
    bucket: HarnessErrorBucket,
    model: string,
    value: number,
  ) => {
    if (value <= 0) {
      return;
    }
    const params = new URLSearchParams({ bucket, model });
    router.push(`/runs/${run.runId}/grid?${params.toString()}`);
  };

  return (
    <div>
      <p className="text-xs text-neutral-600 mb-2">
        Click a bar to filter Comparison Grid by model and failure bucket.
      </p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
          <CartesianGrid stroke="#e5e5e5" strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: "#525252" }}
            interval={0}
            angle={-20}
            textAnchor="end"
            height={56}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fontSize: 10, fill: "#525252" }}
            width={28}
          />
          <Tooltip
            contentStyle={{ fontSize: 11, borderColor: "#d4d4d4" }}
            formatter={(value, name) => [value, name]}
          />
          {run.models.map((model, idx) => (
            <Bar
              key={model}
              dataKey={model}
              fill={MODEL_BAR_COLORS[idx % MODEL_BAR_COLORS.length]}
              cursor="pointer"
              onClick={(barData) => {
                const payload = barData.payload as Record<string, string | number>;
                const bucket = payload.bucket as HarnessErrorBucket;
                const count = Number(payload[model] ?? 0);
                handleBarClick(bucket, model, count);
              }}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
