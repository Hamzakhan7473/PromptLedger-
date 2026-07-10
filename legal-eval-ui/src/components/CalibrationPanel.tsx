"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  ComposedChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  XAxis,
  YAxis,
} from "recharts";

import { runArtifactFileUrl } from "@/lib/api";
import { getSessionToken } from "@/lib/orgAuth";
import type { CalibrationBin } from "@/lib/types";

const CHART_COLORS = {
  grid: "#d4d4d4",
  axis: "#525252",
  perfect: "#a3a3a3",
  points: "#404040",
};

function binsToChartData(bins: CalibrationBin[]) {
  return bins
    .filter((bin) => bin.count > 0)
    .map((bin) => ({
      confidence: bin.mean_confidence,
      accuracy: bin.empirical_accuracy,
      count: bin.count,
    }));
}

function ReliabilityFromBins({
  model,
  ece,
  bins,
}: {
  model: string;
  ece: number;
  bins: CalibrationBin[];
}) {
  const data = binsToChartData(bins);

  if (data.length === 0) {
    return (
      <p className="text-xs text-neutral-500 p-3 border border-neutral-300">
        No calibration bins for {model}.
      </p>
    );
  }

  return (
    <div>
      <p className="text-xs font-mono text-neutral-600 mb-1 px-1">
        {model} · ECE={ece.toFixed(4)} (from bins)
      </p>
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={data} margin={{ top: 8, right: 8, bottom: 24, left: 8 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="confidence"
            domain={[0, 1]}
            tick={{ fontSize: 10, fill: CHART_COLORS.axis }}
            label={{
              value: "confidence",
              position: "insideBottom",
              offset: -16,
              fontSize: 10,
              fill: CHART_COLORS.axis,
            }}
          />
          <YAxis
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 10, fill: CHART_COLORS.axis }}
            label={{
              value: "accuracy",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              fontSize: 10,
              fill: CHART_COLORS.axis,
            }}
          />
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: 1, y: 1 },
            ]}
            stroke={CHART_COLORS.perfect}
            strokeDasharray="4 4"
          />
          <Scatter dataKey="accuracy" fill={CHART_COLORS.points} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CalibrationPanel({
  runId,
  model,
  ece,
  bins,
  shareToken,
}: {
  runId: string;
  model: string;
  ece: number;
  bins?: CalibrationBin[];
  shareToken?: string;
}) {
  const [pngUrl, setPngUrl] = useState<string | null>(null);
  const [pngFailed, setPngFailed] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;
    const url = runArtifactFileUrl(runId, `calibration/${model}.png`, shareToken);

    async function loadPng() {
      const headers: HeadersInit = {};
      if (!shareToken) {
        const key = await getSessionToken();
        if (key) {
          headers.Authorization = `Bearer ${key}`;
        }
      }

      fetch(url, { headers })
        .then((response) => {
          if (!response.ok) {
            throw new Error("PNG unavailable");
          }
          return response.blob();
        })
        .then((blob) => {
          objectUrl = URL.createObjectURL(blob);
          setPngUrl(objectUrl);
          setPngFailed(false);
        })
        .catch(() => {
          setPngFailed(true);
          setPngUrl(null);
        });
    }

    void loadPng();

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [runId, model, shareToken]);

  if (pngUrl && !pngFailed) {
    return (
      <div className="border border-neutral-300 bg-white p-2">
        <p className="text-xs font-mono text-neutral-600 mb-1 px-1">
          {model} · ECE={ece.toFixed(4)}
        </p>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={pngUrl}
          alt={`Reliability curve for ${model}`}
          className="max-w-full h-auto"
        />
      </div>
    );
  }

  if (bins && bins.length > 0) {
    return (
      <div className="border border-neutral-300 bg-white p-2">
        <ReliabilityFromBins model={model} ece={ece} bins={bins} />
      </div>
    );
  }

  return (
    <div className="border border-neutral-300 bg-white p-2">
      <p className="text-xs text-neutral-500 p-2">
        {model}: calibration PNG unavailable and no bin data.
      </p>
    </div>
  );
}
