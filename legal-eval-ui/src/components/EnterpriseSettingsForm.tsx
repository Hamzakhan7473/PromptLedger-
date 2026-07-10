"use client";

import { useEffect, useState } from "react";

import {
  fetchEnterpriseSettings,
  updateEnterpriseSettings,
  type EnterpriseSettings,
} from "@/lib/api";

export function EnterpriseSettingsForm() {
  const [settings, setSettings] = useState<EnterpriseSettings | null>(null);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookSecret, setWebhookSecret] = useState("");
  const [bedrockRegion, setBedrockRegion] = useState("");
  const [bedrockEndpoint, setBedrockEndpoint] = useState("");
  const [ssoDomain, setSsoDomain] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEnterpriseSettings()
      .then((data) => {
        setSettings(data);
        setWebhookUrl(data.webhook_url ?? "");
        setBedrockRegion(data.bedrock_region ?? "");
        setBedrockEndpoint(data.bedrock_endpoint_url ?? "");
        setSsoDomain(data.sso_domain ?? "");
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  async function handleSave() {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const payload: Record<string, string | null> = {
        webhook_url: webhookUrl.trim() || null,
        bedrock_region: bedrockRegion.trim() || null,
        bedrock_endpoint_url: bedrockEndpoint.trim() || null,
        sso_domain: ssoDomain.trim() || null,
      };
      if (webhookSecret.trim()) {
        payload.webhook_secret = webhookSecret.trim();
      }
      const updated = await updateEnterpriseSettings(payload);
      setSettings(updated);
      setWebhookSecret("");
      setMessage("Enterprise settings saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-3 card-surface p-5">
      <h2 className="text-sm font-semibold">Enterprise</h2>
      <p className="text-xs text-neutral-600">
        Webhooks, private Bedrock endpoints, and SSO domain routing.
      </p>

      <div>
        <label className="text-xs text-neutral-600">Webhook URL</label>
        <input
          type="url"
          value={webhookUrl}
          onChange={(e) => setWebhookUrl(e.target.value)}
          placeholder="https://your-firm.com/hooks/legal-eval"
          className="input-field font-mono mt-1"
        />
        {settings?.webhook_secret_stored && (
          <p className="text-xs text-neutral-500 mt-1">Signing secret stored</p>
        )}
      </div>

      <div>
        <label className="text-xs text-neutral-600">Webhook signing secret</label>
        <input
          type="password"
          autoComplete="off"
          value={webhookSecret}
          onChange={(e) => setWebhookSecret(e.target.value)}
          placeholder={settings?.webhook_secret_stored ? "••••••••" : "Optional HMAC secret"}
          className="input-field font-mono mt-1"
        />
      </div>

      <div>
        <label className="text-xs text-neutral-600">Bedrock region (VPC/private)</label>
        <input
          type="text"
          value={bedrockRegion}
          onChange={(e) => setBedrockRegion(e.target.value)}
          placeholder="us-east-1"
          className="input-field font-mono mt-1"
        />
      </div>

      <div>
        <label className="text-xs text-neutral-600">Bedrock VPC endpoint URL</label>
        <input
          type="url"
          value={bedrockEndpoint}
          onChange={(e) => setBedrockEndpoint(e.target.value)}
          placeholder="https://bedrock-runtime.us-east-1.amazonaws.com"
          className="input-field font-mono mt-1"
        />
      </div>

      <div>
        <label className="text-xs text-neutral-600">SSO email domain</label>
        <input
          type="text"
          value={ssoDomain}
          onChange={(e) => setSsoDomain(e.target.value)}
          placeholder="lawfirm.com"
          className="input-field mt-1"
        />
        <p className="text-xs text-neutral-500 mt-1">
          Used with Okta/Azure AD at your API gateway in production deployments.
        </p>
      </div>

      <button
        type="button"
        disabled={loading}
        onClick={handleSave}
        className="px-3 py-1.5 text-sm border border-neutral-400 disabled:opacity-50"
      >
        Save enterprise settings
      </button>

      {message && <p className="text-xs text-green-800">{message}</p>}
      {error && <p className="text-xs text-red-700">{error}</p>}
    </section>
  );
}
