"use client";

import Link from "next/link";

const STEPS = [
  {
    step: "01",
    title: "Sign up",
    body: "Create an account — your workspace is provisioned automatically on first login.",
  },
  {
    step: "02",
    title: "Add model keys & upload data",
    body: "Save OpenAI, Google, or Anthropic credentials under Settings. Upload JSONL, import from Hugging Face, or extract from PDFs.",
  },
  {
    step: "03",
    title: "Run & share results",
    body: "Compare models, track presence F1, span grounding, judge κ, and calibration. Share read-only links or export a trust report.",
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
        <Link href="/sign-up" className="text-primary underline-offset-2 hover:underline">
          Sign up
        </Link>{" "}
        or{" "}
        <Link href="/onboarding" className="text-primary underline-offset-2 hover:underline">
          follow the setup guide
        </Link>
        .
      </p>
    </section>
  );
}

/** @deprecated Use GettingStartedGuide — kept for imports during transition. */
export const LocalSetupGuide = GettingStartedGuide;
