"use client";

import Link from "next/link";

const STEPS = [
  {
    step: "01",
    title: "Create your organization",
    body: "Sign up in Settings to get an org API key. Your workspace is isolated from other teams on the platform.",
  },
  {
    step: "02",
    title: "Add model keys & upload data",
    body: "Save OpenAI, Google, or Bedrock credentials under Settings → Model API keys. Upload a JSONL eval set on New eval.",
  },
  {
    step: "03",
    title: "Run & share results",
    body: "Pick models, run your eval, and track presence F1, span grounding, judge κ, and calibration. Share read-only links or export a trust report when complete.",
  },
];

type GettingStartedGuideProps = {
  compact?: boolean;
};

export function GettingStartedGuide({ compact = false }: GettingStartedGuideProps) {
  return (
    <section className={compact ? "space-y-2" : "space-y-3 card-surface p-5"}>
      <div>
        <h2 className={compact ? "text-sm font-semibold" : "text-base font-semibold"}>
          Getting started
        </h2>
        <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
          Everything runs in your browser against the hosted API. You pay model providers
          directly when you start an eval — we do not host inference for you.
        </p>
      </div>
      <ol className="space-y-3 text-sm">
        {STEPS.map((item) => (
          <li key={item.step}>
            <span className="text-xs font-semibold tracking-widest text-primary">
              {item.step}
            </span>
            <p className="mt-1 font-medium">{item.title}</p>
            <p className="text-xs text-muted-foreground leading-relaxed">{item.body}</p>
          </li>
        ))}
      </ol>
      <p className="text-xs text-muted-foreground">
        New here?{" "}
        <Link href="/settings" className="text-primary underline-offset-2 hover:underline">
          Open Settings
        </Link>{" "}
        to create an org, then{" "}
        <Link href="/new" className="text-primary underline-offset-2 hover:underline">
          start an eval
        </Link>
        .
      </p>
    </section>
  );
}

/** @deprecated Use GettingStartedGuide — kept for imports during transition. */
export const LocalSetupGuide = GettingStartedGuide;
