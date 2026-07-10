"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { NewEvalForm } from "@/components/NewEvalForm";
import {
  completeOnboarding,
  fetchOnboardingStatus,
  fetchOrgSecretsStatus,
  updateOrgSecrets,
} from "@/lib/api";
import { demoRunPath } from "@/lib/demoRun";

type Step = "welcome" | "byok" | "dataset" | "first-run";

const STEPS: Step[] = ["welcome", "byok", "dataset", "first-run"];

export function OnboardingWizard() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("welcome");
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [secretSaved, setSecretSaved] = useState({ openai: false, google: false, anthropic: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOnboardingStatus()
      .then((status) => {
        if (status.completed) router.replace("/dashboard");
      })
      .catch(() => undefined);
    fetchOrgSecretsStatus()
      .then((s) =>
        setSecretSaved({ openai: s.openai, google: s.google, anthropic: s.anthropic }),
      )
      .catch(() => undefined);
  }, [router]);

  const stepIndex = STEPS.indexOf(step);

  async function finishOnboarding(redirectTo: string) {
    setLoading(true);
    try {
      await completeOnboarding();
      router.push(redirectTo);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save progress.");
      setLoading(false);
    }
  }

  async function saveByok() {
    setLoading(true);
    setError(null);
    try {
      const status = await updateOrgSecrets(secrets);
      setSecretSaved({ openai: status.openai, google: status.google, anthropic: status.anthropic });
      setSecrets({});
      setStep("dataset");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save keys.");
    } finally {
      setLoading(false);
    }
  }

  function skipStep() {
    const next = STEPS[stepIndex + 1];
    if (next) setStep(next);
    else void finishOnboarding("/dashboard");
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        {STEPS.map((s, i) => (
          <div
            key={s}
            className={`h-1 flex-1 rounded-full ${i <= stepIndex ? "bg-primary" : "bg-border"}`}
          />
        ))}
      </div>

      {step === "welcome" && (
        <section className="card-surface space-y-4 p-6">
          <h2 className="text-xl font-semibold">Welcome to Legal Eval</h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Prove your legal AI extraction pipeline with reproducible, judge-validated metrics.
            Upload contracts or JSONL eval sets, compare frontier models side-by-side, and share
            trust reports with enterprise buyers — all with your own API keys (BYOK).
          </p>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-primary" onClick={() => setStep("byok")}>
              Get started
            </button>
            <button
              type="button"
              className="btn-outline min-h-9 px-4 text-sm"
              disabled={loading}
              onClick={() => void finishOnboarding("/dashboard")}
            >
              Skip for now
            </button>
          </div>
        </section>
      )}

      {step === "byok" && (
        <section className="card-surface space-y-4 p-6">
          <h2 className="text-lg font-semibold">Bring your model keys</h2>
          <p className="text-sm text-muted-foreground">
            Add at least one provider key so evals run against your accounts. We never charge for
            model usage — keys are encrypted and sent only to the provider you choose.
          </p>
          {["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"].map((key) => (
            <div key={key}>
              <label className="text-xs text-muted-foreground">{key}</label>
              <input
                type="password"
                autoComplete="off"
                placeholder={
                  secretSaved[key === "OPENAI_API_KEY" ? "openai" : key === "GOOGLE_API_KEY" ? "google" : "anthropic"]
                    ? "••••••••"
                    : ""
                }
                value={secrets[key] ?? ""}
                onChange={(e) => setSecrets((prev) => ({ ...prev, [key]: e.target.value }))}
                className="input-field font-mono mt-1"
              />
            </div>
          ))}
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => void saveByok()}
            >
              Save keys & continue
            </button>
            <button type="button" className="btn-outline min-h-9 px-4 text-sm" onClick={skipStep}>
              Skip
            </button>
          </div>
        </section>
      )}

      {step === "dataset" && (
        <section className="card-surface space-y-4 p-6">
          <h2 className="text-lg font-semibold">Add a dataset</h2>
          <p className="text-sm text-muted-foreground">
            Upload JSONL, import from Hugging Face, extract from PDFs/DOCX, or explore the public
            demo run first.
          </p>
          <div className="rounded-xl border border-border p-4">
            <NewEvalForm compact />
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-primary" onClick={() => setStep("first-run")}>
              Continue
            </button>
            <Link href={demoRunPath("summary")} className="btn-outline min-h-9 px-4 text-sm inline-flex items-center">
              Explore demo first
            </Link>
            <button type="button" className="btn-outline min-h-9 px-4 text-sm" onClick={skipStep}>
              Skip
            </button>
          </div>
        </section>
      )}

      {step === "first-run" && (
        <section className="card-surface space-y-4 p-6">
          <h2 className="text-lg font-semibold">Run your first eval</h2>
          <p className="text-sm text-muted-foreground">
            Kick off a comparison run from the workspace, or finish setup and explore the demo if
            you are not ready to spend model tokens yet.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link href="/new" className="btn-primary min-h-9 px-4 text-sm inline-flex items-center">
              Start new eval
            </Link>
            <Link href={demoRunPath("summary")} className="btn-outline min-h-9 px-4 text-sm inline-flex items-center">
              View demo run
            </Link>
            <button
              type="button"
              className="btn-outline min-h-9 px-4 text-sm"
              disabled={loading}
              onClick={() => void finishOnboarding("/dashboard")}
            >
              Go to dashboard
            </button>
          </div>
        </section>
      )}

      {error && (
        <p className="text-sm text-red-700 bg-red-50 border border-red-200 p-3">{error}</p>
      )}
    </div>
  );
}
