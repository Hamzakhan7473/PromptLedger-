"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EnterpriseSettingsForm } from "@/components/EnterpriseSettingsForm";
import {
  fetchModels,
  fetchOrgProfile,
  fetchOrgSecretsStatus,
  updateOrgModels,
  updateOrgSecrets,
  type ModelInfo,
  type OrgProfile,
  type OrgSecretsStatus,
} from "@/lib/api";

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return iso;
  }
}

export function SettingsForm() {
  const [profile, setProfile] = useState<OrgProfile | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [secretStatus, setSecretStatus] = useState<OrgSecretsStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchModels(),
      fetchOrgProfile(),
      fetchOrgSecretsStatus(),
    ])
      .then(([catalog, prof, secretsStatus]) => {
        setModels(catalog);
        setProfile(prof);
        setSecretStatus(secretsStatus);
        const map: Record<string, boolean> = {};
        for (const m of prof.enabled_models) map[m] = true;
        setEnabled(map);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  async function saveSecrets() {
    setLoading(true);
    setError(null);
    try {
      const status = await updateOrgSecrets(secrets);
      setSecretStatus(status);
      setSecrets({});
      setMessage("Model API keys saved (encrypted at rest on your API server).");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save keys.");
    } finally {
      setLoading(false);
    }
  }

  async function saveModels() {
    const selected = Object.entries(enabled)
      .filter(([, on]) => on)
      .map(([id]) => id);
    if (selected.length === 0) {
      setError("Enable at least one model.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const prof = await updateOrgModels(selected);
      setProfile(prof);
      setMessage("Enabled models updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update models.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8 max-w-xl">
      {profile && (
        <section className="space-y-3 card-surface p-5">
          <h2 className="text-sm font-semibold">Your organization</h2>
          <p className="text-sm text-foreground">{profile.name}</p>
          <p className="text-xs text-muted-foreground">
            Created {formatDate(profile.created_at)}
          </p>
          <p className="text-xs text-muted-foreground">
            Your workspace is tied to your account. Provider keys below are stored encrypted
            per organization (BYOK).
          </p>
        </section>
      )}

      <section className="space-y-3 card-surface p-5">
        <h2 className="text-sm font-semibold">Enabled models</h2>
        <p className="text-xs text-muted-foreground">
          Choose which models to evaluate. Add provider keys under Model API keys before
          starting a run.
        </p>
        <div className="space-y-2">
          {models.map((m) => (
            <label key={m.id} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!enabled[m.id]}
                onChange={(e) =>
                  setEnabled((prev) => ({ ...prev, [m.id]: e.target.checked }))
                }
              />
              {m.label}
            </label>
          ))}
        </div>
        <button
          type="button"
          disabled={loading}
          onClick={saveModels}
          className="px-3 py-1.5 text-sm border border-neutral-400"
        >
          Save models
        </button>
      </section>

      <section className="space-y-3 card-surface p-5">
        <h2 className="text-sm font-semibold">Model API keys (BYOK)</h2>
        <p className="text-xs text-muted-foreground">
          Your OpenAI / Google / Anthropic keys are encrypted per organization. We never bill
          your model usage — keys go directly to providers.
        </p>
        {secretStatus && (
          <p className="text-xs text-muted-foreground">
            Saved: OpenAI {secretStatus.openai ? "✓" : "—"} · Google{" "}
            {secretStatus.google ? "✓" : "—"} · Anthropic{" "}
            {secretStatus.anthropic ? "✓" : "—"}
          </p>
        )}
        {["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"].map((key) => (
          <div key={key}>
            <label className="text-xs text-muted-foreground">{key}</label>
            <input
              type="password"
              autoComplete="off"
              placeholder={secretStatus?.stored_keys.includes(key) ? "••••••••" : ""}
              value={secrets[key] ?? ""}
              onChange={(e) =>
                setSecrets((prev) => ({ ...prev, [key]: e.target.value }))
              }
              className="input-field font-mono mt-1"
            />
          </div>
        ))}
        <button
          type="button"
          disabled={loading}
          onClick={saveSecrets}
          className="px-3 py-1.5 text-sm border border-neutral-400"
        >
          Save model keys
        </button>
      </section>

      <EnterpriseSettingsForm />

      {message && (
        <p className="text-sm text-green-800 bg-green-50 border border-green-200 p-3">
          {message}
        </p>
      )}
      {error && (
        <p className="text-sm text-red-700 bg-red-50 border border-red-200 p-3">{error}</p>
      )}

      <Link href="/new" className="text-sm text-muted-foreground hover:text-neutral-900 underline">
        → New eval
      </Link>
    </div>
  );
}
