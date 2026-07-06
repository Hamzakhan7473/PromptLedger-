"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EnterpriseSettingsForm } from "@/components/EnterpriseSettingsForm";
import { LocalSetupGuide } from "@/components/LocalSetupGuide";
import {
  createOrganization,
  fetchModels,
  fetchOrgProfile,
  fetchOrgSecretsStatus,
  updateOrgModels,
  updateOrgSecrets,
  type ModelInfo,
  type OrgSecretsStatus,
} from "@/lib/api";
import {
  clearOrgApiKey,
  getOrgApiKey,
  hasOrgApiKey,
  setOrgApiKey,
} from "@/lib/orgAuth";

export function SettingsForm() {
  const [orgName, setOrgName] = useState("My Firm");
  const [apiKey, setApiKey] = useState("");
  const [newOrgKey, setNewOrgKey] = useState<string | null>(null);
  const [profile, setProfile] = useState<{ org_id: string; name: string; enabled_models: string[] } | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [secretStatus, setSecretStatus] = useState<OrgSecretsStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setApiKey(getOrgApiKey() ?? "");
    fetchModels().then(setModels).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!hasOrgApiKey()) return;
    fetchOrgProfile()
      .then((prof) => {
        setProfile(prof);
        const map: Record<string, boolean> = {};
        for (const m of prof.enabled_models) map[m] = true;
        setEnabled(map);
      })
      .catch((err: Error) => setError(err.message));
    fetchOrgSecretsStatus()
      .then(setSecretStatus)
      .catch(() => undefined);
  }, [apiKey]);

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

  async function saveApiKey() {
    setOrgApiKey(apiKey.trim());
    setMessage("Organization API key saved in this browser.");
    setError(null);
  }

  async function handleCreateOrg() {
    setLoading(true);
    setError(null);
    try {
      const org = await createOrganization(orgName.trim() || "My Firm");
      setNewOrgKey(org.api_key);
      setOrgApiKey(org.api_key);
      setApiKey(org.api_key);
      setProfile({ org_id: org.org_id, name: org.name, enabled_models: org.enabled_models });
      const map: Record<string, boolean> = {};
      for (const m of org.enabled_models) map[m] = true;
      setEnabled(map);
      setMessage("Organization created. Copy the API key now — it won't be shown again.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create org.");
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

  function logout() {
    clearOrgApiKey();
    setApiKey("");
    setProfile(null);
    setSecretStatus(null);
    setMessage("Signed out of this browser.");
  }

  return (
    <div className="space-y-8 max-w-xl">
      <LocalSetupGuide />

      <section className="space-y-3 card-surface p-5">
        <h2 className="text-sm font-semibold">Organization API key</h2>
        <p className="text-xs text-muted-foreground">
          Required for all API calls. Stored in browser localStorage only.
        </p>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="le_org_..."
          className="input-field font-mono"
        />
        <div className="flex gap-2 flex-wrap">
          <button
            type="button"
            onClick={saveApiKey}
            className="btn-primary"
          >
            Save key
          </button>
          <button type="button" onClick={logout} className="btn-outline min-h-9 px-3 text-sm">
            Sign out
          </button>
        </div>
        {newOrgKey && (
          <p className="text-xs text-amber-800 bg-amber-50 border border-amber-200 p-2 font-mono break-all">
            New key (copy now): {newOrgKey}
          </p>
        )}
      </section>

      <section className="space-y-3 card-surface p-5">
        <h2 className="text-sm font-semibold">Create organization</h2>
        <input
          type="text"
          value={orgName}
          onChange={(e) => setOrgName(e.target.value)}
          className="input-field"
          placeholder="Firm or startup name"
        />
        <button
          type="button"
          disabled={loading}
          onClick={handleCreateOrg}
          className="btn-primary disabled:opacity-50"
        >
          Create organization
        </button>
        {profile && (
          <p className="text-xs text-muted-foreground">
            Signed in as <span className="font-mono">{profile.org_id}</span> — {profile.name}
          </p>
        )}
      </section>

      {hasOrgApiKey() && (
        <>
          <section className="space-y-3 card-surface p-5">
            <h2 className="text-sm font-semibold">Enabled models</h2>
            <p className="text-xs text-muted-foreground">
              Choose which models to evaluate. Add provider keys under Model API keys below
              before starting a run.
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
            <h2 className="text-sm font-semibold">Model API keys</h2>
            <p className="text-xs text-muted-foreground">
              Save your OpenAI / Google keys here (encrypted per organization). Bedrock uses
              AWS credentials configured for the API deployment.
            </p>
            {secretStatus && (
              <p className="text-xs text-muted-foreground">
                Saved: OpenAI {secretStatus.openai ? "✓" : "—"} · Google{" "}
                {secretStatus.google ? "✓" : "—"}
              </p>
            )}
            {["OPENAI_API_KEY", "GOOGLE_API_KEY"].map((key) => (
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
        </>
      )}

      {message && <p className="text-sm text-green-800 bg-green-50 border border-green-200 p-3">{message}</p>}
      {error && <p className="text-sm text-red-700 bg-red-50 border border-red-200 p-3">{error}</p>}

      <Link href="/new" className="text-sm text-muted-foreground hover:text-neutral-900 underline">
        → New eval
      </Link>
    </div>
  );
}
