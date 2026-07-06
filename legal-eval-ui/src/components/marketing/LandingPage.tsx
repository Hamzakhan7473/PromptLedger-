import Link from "next/link";
import { Building2, Check, Earth, Users } from "./icons";

import { GenieMascot } from "./GenieMascot";
import { demoRunPath } from "@/lib/demoRun";

const WHO_ITEMS = [
  {
    icon: Building2,
    title: "Legal AI startups shipping to enterprise",
    body: "You build clause extraction, contract review, or agent workflows — and buyers want task-level evidence, not slide decks. Prove accuracy on your own dataset before procurement calls.",
  },
  {
    icon: Earth,
    title: "Platform teams evaluating pipeline changes",
    body: "Compare GPT, Claude, Gemini, and Bedrock on the same JSONL eval set. Pin model IDs, hash your dataset, and show a reproducible manifest when you swap models or prompts.",
  },
  {
    icon: Users,
    title: "ML engineers closing the build-vs-buy gap",
    body: "Stop maintaining one-off eval scripts. Run direct or agent-mode harnesses, pass judge validation gates, and export a shareable trust report for external stakeholders.",
  },
];

const HOW_STEPS = [
  {
    step: "01",
    title: "Create an organization (BYOK)",
    body: "Free platform access — bring your own OpenAI, Google, or Bedrock keys. We never run inference or touch your model spend. Keys are encrypted per org.",
  },
  {
    step: "02",
    title: "Upload your eval set",
    body: "Any JSONL dataset your team defines — not limited to a single public benchmark. Upload on New eval, pick models, run direct eval or the Deep Agents harness.",
  },
  {
    step: "03",
    title: "Share evidence, not vibes",
    body: "Every run records a reproducible manifest (pinned model IDs, dataset SHA-256, seeds). Export a trust report or share a read-only link with buyers.",
  },
];

const WHY_ITEMS = [
  {
    q: "Why can't I just demo the product?",
    body: "Enterprise buyers now ask for methodology transparency and task-level metrics — presence F1, span grounding, judge-validated calibration — not capability claims. Legal Eval closes that gap with auditable runs you can hand to procurement.",
  },
  {
    q: "Why not roll your own eval scripts?",
    body: "You can — but then you maintain bootstrap CIs, judge adjudication, calibration plots, manifest pinning, org workspaces, and exportable reports. We package the full trust layer so your team ships product, not spreadsheets.",
  },
  {
    q: "Why compare multiple providers here?",
    body: "Build-vs-buy and model-selection decisions need apples-to-apples numbers on your data. Route Claude, GPT, Gemini, and Bedrock through one harness and one manifest format.",
  },
];

const TRUST = [
  "BYOK — free platform, your provider billing",
  "Custom JSONL datasets (any categories)",
  "Reproducible manifest on every run",
  "Shareable trust report export",
];

const FREE_FEATURES = [
  "Unlimited eval & agent runs (BYOK)",
  "OpenAI, Gemini, Claude via Bedrock",
  "Deep Agents extract → validate harness",
  "Pinned models + hashed datasets + seeds",
  "LLM judge with statistical agreement gate",
  "Multi-provider comparison on your data",
  "Share links + PDF trust report",
  "Org workspace, audit log, webhooks",
];

export function LandingPage() {
  const demoSummary = demoRunPath("summary");

  return (
    <div className="public-light-shell min-h-screen">
      <section className="taxora-hero-grid border-b border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 py-16 sm:px-6 sm:py-20 md:flex-row md:items-center md:gap-12 lg:py-24">
          <div className="order-2 flex flex-1 flex-col gap-6 md:order-1">
            <p className="text-sm font-medium text-primary">
              Hosted · Evaluation &amp; trust layer for legal AI teams
            </p>
            <h1 className="editorial-headline font-semibold text-3xl leading-tight sm:text-4xl md:text-5xl lg:text-[3.25rem]">
              Prove your legal AI actually works.
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-taxora-text-secondary md:text-lg">
              Reproducible, auditable evaluation for legal document extraction — built for teams
              shipping contract review, clause extraction, and legal agents to enterprise buyers
              who no longer accept &ldquo;trust us.&rdquo;
            </p>
            <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
              Bring your own dataset and your own model keys. Get presence F1, span accuracy,
              judge-validated calibration, and a reproducible manifest you can hand to a
              buyer&apos;s procurement team.
            </p>
            <div className="flex flex-wrap items-center gap-3 sm:gap-4">
              <Link href="/settings" className="btn-primary">
                Get started
              </Link>
              <Link href={demoSummary} className="btn-outline">
                Browse demo results
              </Link>
            </div>
            <p className="text-xs text-muted-foreground">
              Free to use · BYOK · you pay OpenAI / Google / AWS only when you run evals — we
              never host inference.
            </p>
          </div>
          <div className="order-1 flex flex-1 justify-center md:order-2 md:justify-end">
            <GenieMascot />
          </div>
        </div>
      </section>

      <section id="setup" className="section-pad border-b border-border bg-muted/40">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8 text-center">
            <h2 className="editorial-headline font-semibold text-2xl tracking-tight sm:text-3xl">
              How it works
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Three steps from your eval set to evidence you can show externally.
            </p>
          </div>
          <ol className="space-y-4 text-sm">
            {HOW_STEPS.map((step) => (
              <li key={step.step} className="card-surface p-4">
                <span className="text-xs font-semibold tracking-widest text-primary">
                  {step.step}
                </span>
                <h3 className="mt-1 font-semibold">{step.title}</h3>
                <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{step.body}</p>
              </li>
            ))}
          </ol>
          <p className="mt-6 text-center text-xs text-muted-foreground">
            <Link href="/settings" className="text-primary underline-offset-2 hover:underline">
              Settings
            </Link>{" "}
            → create org →{" "}
            <Link href="/new" className="text-primary underline-offset-2 hover:underline">
              New eval
            </Link>
          </p>
        </div>
      </section>

      <section id="who" className="section-pad bg-background text-foreground">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10 max-w-2xl mx-auto text-center md:max-w-3xl">
            <h2 className="editorial-headline font-semibold text-2xl tracking-tight sm:text-3xl">
              Built for legal AI builders
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Not casual contract review — the evaluation layer teams use to validate extraction
              pipelines internally and prove them to enterprise buyers.
            </p>
          </div>
          <ul className="grid gap-6 md:grid-cols-3">
            {WHO_ITEMS.map((item) => (
              <li key={item.title} className="card-surface p-6">
                <span className="mb-4 inline-flex rounded-xl bg-primary/10 p-3 text-primary">
                  <item.icon className="size-6" />
                </span>
                <h3 className="text-lg font-semibold leading-snug">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="how" className="section-pad border-y border-border bg-muted/40">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10 max-w-2xl mx-auto text-center">
            <h2 className="editorial-headline font-semibold text-2xl tracking-tight sm:text-3xl">
              Why teams choose Legal Eval
            </h2>
          </div>
          <ul className="grid gap-6 md:grid-cols-3">
            {WHY_ITEMS.map((item) => (
              <li key={item.q} className="card-surface p-6">
                <h3 className="text-base font-semibold leading-snug">{item.q}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
              </li>
            ))}
          </ul>
          <ul className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {TRUST.map((line) => (
              <li key={line} className="flex items-center gap-2 text-sm text-muted-foreground">
                <Check className="size-4 shrink-0 text-primary" />
                {line}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section-pad border-y border-border bg-accent/30">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="editorial-headline font-semibold text-2xl sm:text-3xl">
            Ready to prove your pipeline?
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Create an organization, add your model keys, upload your eval set, and export evidence
            buyers can audit.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Link href="/settings" className="btn-primary">
              Create organization
            </Link>
            <Link href="/new" className="btn-outline">
              New eval
            </Link>
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            Browse sample output:{" "}
            <Link href={demoSummary} className="text-primary underline-offset-2 hover:underline">
              demo run
            </Link>
            .
          </p>
        </div>
      </section>

      <section id="pricing" className="section-pad bg-background">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10 text-center">
            <h2 className="editorial-headline font-semibold text-2xl sm:text-3xl">Pricing</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Platform access is free — BYOK. You pay providers only when you run evals.
            </p>
          </div>
          <div className="mx-auto max-w-md">
            <div className="card-surface flex flex-col p-8 ring-2 ring-primary/30">
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-lg font-semibold">Workspace</h3>
                <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-primary/15 text-primary">
                  BYOK
                </span>
              </div>
              <p className="mt-3">
                <span className="text-4xl font-semibold">Free</span>
                <span className="text-sm text-muted-foreground"> · your model keys</span>
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                Full trust layer in the browser — custom datasets, multi-provider routing,
                reproducible manifests, shareable reports.
              </p>
              <ul className="mt-6 space-y-2.5 text-sm text-muted-foreground">
                {FREE_FEATURES.map((f) => (
                  <li key={f} className="flex gap-2">
                    <Check className="size-4 shrink-0 text-primary mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link href="/settings" className="btn-primary mt-8 w-full text-center">
                Get started
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="section-pad border-t border-border bg-muted/30">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="editorial-headline font-semibold text-2xl leading-snug sm:text-3xl md:text-4xl">
            Stop asking buyers to trust your legal AI. Show them the eval.
          </h2>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/new" className="btn-primary">
              Start an eval
            </Link>
            <Link href={demoSummary} className="btn-outline">
              Browse demo results
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
