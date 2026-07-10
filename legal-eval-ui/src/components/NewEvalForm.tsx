"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { GettingStartedGuide } from "@/components/LocalSetupGuide";
import {
  createRun,
  downloadDocumentTemplate,
  fetchDatasetAdapters,
  fetchModels,
  fetchOrgProfile,
  fetchOrgSecretsStatus,
  importDocuments,
  importHuggingFaceDataset,
  uploadDataset,
  type AdapterCatalogEntry,
  type DatasetImportResponse,
  type DocumentImportResponse,
  type ModelInfo,
  type RunMode,
} from "@/lib/api";

type DatasetSource = "jsonl" | "huggingface" | "documents";

export function NewEvalForm({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [datasetSource, setDatasetSource] = useState<DatasetSource>("jsonl");
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [enabledModels, setEnabledModels] = useState<string[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [file, setFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState("");
  const [runName, setRunName] = useState("");
  const [mode, setMode] = useState<RunMode>("eval");
  const [skipJudge, setSkipJudge] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [storedKeys, setStoredKeys] = useState<string[]>([]);

  const [adapters, setAdapters] = useState<AdapterCatalogEntry[]>([]);
  const [hfRepoId, setHfRepoId] = useState("nguha/legalbench");
  const [hfConfig, setHfConfig] = useState("abercrombie");
  const [hfSplit, setHfSplit] = useState("test");
  const [hfMaxExamples, setHfMaxExamples] = useState(50);
  const [hfAdapter, setHfAdapter] = useState("legalbench_abercrombie");
  const [hfImported, setHfImported] = useState<DatasetImportResponse | null>(null);
  const [importWarning, setImportWarning] = useState<string | null>(null);

  const [documentFiles, setDocumentFiles] = useState<File[]>([]);
  const [documentImport, setDocumentImport] = useState<DocumentImportResponse | null>(null);

  useEffect(() => {
    Promise.all([
      fetchModels(),
      fetchOrgProfile(),
      fetchOrgSecretsStatus(),
      fetchDatasetAdapters(),
    ])
      .then(([catalog, profile, secrets, adapterList]) => {
        setModels(catalog);
        setEnabledModels(profile.enabled_models);
        setStoredKeys(secrets.stored_keys);
        setAdapters(adapterList);
        if (adapterList.length > 0) {
          setHfAdapter((current) =>
            adapterList.some((a) => a.name === current) ? current : adapterList[0].name,
          );
        }
        const initial: Record<string, boolean> = {};
        for (const id of profile.enabled_models) initial[id] = true;
        setSelected(initial);
      })
      .catch((err: Error) => setLoadError(err.message));
  }, []);

  const available = models.filter((m) => enabledModels.includes(m.id));
  const chosen = available.filter((m) => selected[m.id]);
  const selectedAdapter = adapters.find((a) => a.name === hfAdapter);

  function resetHfImport() {
    setHfImported(null);
    setImportWarning(null);
  }

  function resetDocumentImport() {
    setDocumentImport(null);
  }

  function switchSource(source: DatasetSource) {
    setDatasetSource(source);
    setError(null);
    if (source === "jsonl") {
      resetHfImport();
      resetDocumentImport();
    }
    if (source === "huggingface") {
      resetDocumentImport();
    }
    if (source === "documents") {
      resetHfImport();
    }
  }

  async function handleHfImport() {
    setError(null);
    setLoading(true);
    try {
      const imported = await importHuggingFaceDataset({
        repo_id: hfRepoId.trim(),
        config: hfConfig.trim() || null,
        split: hfSplit,
        max_examples: hfMaxExamples,
        adapter: hfAdapter,
        name: datasetName.trim() || undefined,
      });
      setHfImported(imported);
      setImportWarning(imported.warning ?? selectedAdapter?.warning ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Hugging Face import failed.");
      resetHfImport();
    } finally {
      setLoading(false);
    }
  }

  async function handleDocumentUpload() {
    if (documentFiles.length === 0) {
      setError("Choose at least one PDF, DOCX, or TXT file.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const imported = await importDocuments(documentFiles);
      setDocumentImport(imported);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document import failed.");
      resetDocumentImport();
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadTemplate() {
    if (!documentImport) return;
    setError(null);
    try {
      await downloadDocumentTemplate(
        documentImport.download_path,
        documentImport.template_filename,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Template download failed.");
    }
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);

    if (datasetSource === "documents") {
      setError("Download and complete the labeling template, then upload JSONL to run an eval.");
      return;
    }
    if (datasetSource === "jsonl" && !file) {
      setError("Choose a .jsonl dataset file.");
      return;
    }
    if (datasetSource === "huggingface" && !hfImported) {
      setError("Import the Hugging Face dataset first, then start the eval.");
      return;
    }
    if (chosen.length === 0) {
      setError("Select at least one model.");
      return;
    }

    for (const model of chosen) {
      if (mode === "agent" && model.agent_supported === false) {
        setError(`Agent mode is not supported for ${model.label}.`);
        return;
      }
      if (!model.requires_env_key) continue;
      const hasStored = storedKeys.includes(model.requires_env_key);
      if (!hasStored) {
        setError(
          `Missing ${model.requires_env_key}. Add it under Settings → Model API keys before running.`,
        );
        return;
      }
    }

    setLoading(true);
    try {
      const dataset =
        datasetSource === "huggingface" && hfImported
          ? hfImported
          : await uploadDataset(file!, datasetName || undefined);

      const run = await createRun({
        dataset_id: dataset.dataset_id,
        models: chosen.map((m) => m.id),
        mode,
        skip_judge_validate: skipJudge,
        name: runName || undefined,
      });

      router.push(`/runs/${run.run_id}/status`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start eval.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6 max-w-xl">
      <GettingStartedGuide compact />

      {loadError && (
        <p className="text-sm text-red-700 border border-red-300 bg-red-50 p-3">
          {loadError}{" "}
          <Link href="/settings" className="underline">
            Settings
          </Link>
        </p>
      )}

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">1. Dataset source</h2>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => switchSource("jsonl")}
            className={`px-3 py-1.5 text-sm rounded-lg border ${
              datasetSource === "jsonl"
                ? "border-primary bg-primary/10 text-primary font-medium"
                : "border-border text-muted-foreground"
            }`}
          >
            JSONL upload
          </button>
          <button
            type="button"
            onClick={() => switchSource("documents")}
            className={`px-3 py-1.5 text-sm rounded-lg border ${
              datasetSource === "documents"
                ? "border-primary bg-primary/10 text-primary font-medium"
                : "border-border text-muted-foreground"
            }`}
          >
            Documents
          </button>
          <button
            type="button"
            onClick={() => switchSource("huggingface")}
            className={`px-3 py-1.5 text-sm rounded-lg border ${
              datasetSource === "huggingface"
                ? "border-primary bg-primary/10 text-primary font-medium"
                : "border-border text-muted-foreground"
            }`}
          >
            Hugging Face
          </button>
        </div>

        {datasetSource === "jsonl" ? (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">
              JSONL with one <code className="bg-neutral-100 px-1">EvalExample</code> per line:
            </p>
            <pre className="text-xs bg-neutral-50 border border-neutral-200 p-2 overflow-x-auto">
{`{"id":"ex-001","contract_excerpt":"…","category":"Payment Terms","present":true,"gold_spans":["verbatim quote"],"contract_title":"Contract A"}
{"id":"ex-002","contract_excerpt":"…","category":"Payment Terms","present":false,"gold_spans":[],"contract_title":"Contract B"}`}
            </pre>
            <input
              type="text"
              placeholder="Dataset name (optional)"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              className="input-field"
            />
            <input
              key="jsonl-file-input"
              type="file"
              accept=".jsonl"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm"
            />
          </div>
        ) : datasetSource === "documents" ? (
          <div className="space-y-3 card-surface p-5">
            <div className="text-xs text-muted-foreground leading-relaxed">
              Step 1 of a two-step workflow: upload raw contracts (PDF, DOCX, or TXT). The API
              extracts text and builds a labeling template — it does not infer categories or gold
              spans. Fill the template offline, then return here and use the{" "}
              <button
                type="button"
                onClick={() => switchSource("jsonl")}
                className="underline text-primary"
              >
                JSONL upload
              </button>{" "}
              tab to run your eval.
            </div>
            <input
              key="documents-file-input"
              type="file"
              accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
              multiple
              onChange={(e) => {
                setDocumentFiles(Array.from(e.target.files ?? []));
                resetDocumentImport();
              }}
              className="block w-full text-sm"
            />
            <p className="text-xs text-muted-foreground">
              Up to 10 files, 20&nbsp;MiB each. PDFs are capped at 200 pages; at most 500 excerpts
              per request.
            </p>
            <button
              type="button"
              disabled={loading || documentFiles.length === 0}
              onClick={handleDocumentUpload}
              className="btn-outline min-h-9 px-4 text-sm disabled:opacity-50"
            >
              {loading ? "Extracting…" : "Extract excerpts"}
            </button>
            {documentImport && (
              <div className="space-y-3 border border-green-200 bg-green-50 p-3 text-xs text-green-900">
                <p>
                  Extracted <span className="font-semibold">{documentImport.excerpt_count}</span>{" "}
                  candidate excerpt{documentImport.excerpt_count === 1 ? "" : "s"} from{" "}
                  {documentImport.source_files.join(", ")}.
                </p>
                <ul className="space-y-2">
                  {documentImport.preview.map((item) => (
                    <li key={item.id} className="border border-green-200 bg-white p-2 rounded">
                      <p className="font-mono text-[11px] text-muted-foreground">
                        {item.id} · {item.source_reference} · {item.char_count} chars
                      </p>
                      <p className="mt-1 text-neutral-800">{item.excerpt_preview}</p>
                    </li>
                  ))}
                </ul>
                {documentImport.excerpt_count > documentImport.preview.length && (
                  <p className="text-muted-foreground">
                    Showing first {documentImport.preview.length} of{" "}
                    {documentImport.excerpt_count} excerpts.
                  </p>
                )}
                <p className="leading-relaxed">{documentImport.instructions}</p>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={handleDownloadTemplate}
                    className="btn-primary min-h-9 px-4 text-sm"
                  >
                    Download labeling template
                  </button>
                  <button
                    type="button"
                    onClick={() => switchSource("jsonl")}
                    className="btn-outline min-h-9 px-4 text-sm"
                  >
                    Go to JSONL upload
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3 card-surface p-5">
            <p className="text-xs text-muted-foreground">
              Import a public Hugging Face dataset and convert it to EvalExample rows in your
              workspace. Requires outbound network from the hosted API.
            </p>
            <input
              type="text"
              placeholder="Dataset name (optional)"
              value={datasetName}
              onChange={(e) => {
                setDatasetName(e.target.value);
                resetHfImport();
              }}
              className="input-field"
            />
            <div>
              <label className="text-xs text-muted-foreground">Repo ID</label>
              <input
                type="text"
                value={hfRepoId}
                onChange={(e) => {
                  setHfRepoId(e.target.value);
                  resetHfImport();
                }}
                className="input-field font-mono mt-1"
                placeholder="nguha/legalbench"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Config</label>
              <input
                type="text"
                value={hfConfig}
                onChange={(e) => {
                  setHfConfig(e.target.value);
                  resetHfImport();
                }}
                className="input-field font-mono mt-1"
                placeholder="abercrombie"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground">Split</label>
                <select
                  value={hfSplit}
                  onChange={(e) => {
                    setHfSplit(e.target.value);
                    resetHfImport();
                  }}
                  className="input-field mt-1"
                >
                  <option value="train">train</option>
                  <option value="test">test</option>
                  <option value="validation">validation</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Max examples</label>
                <input
                  type="number"
                  min={1}
                  max={10000}
                  value={Number.isFinite(hfMaxExamples) ? hfMaxExamples : ""}
                  onChange={(e) => {
                    setHfMaxExamples(Number(e.target.value) || 100);
                    resetHfImport();
                  }}
                  className="input-field mt-1"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Adapter</label>
              <select
                value={hfAdapter}
                disabled={adapters.length === 0}
                onChange={(e) => {
                  setHfAdapter(e.target.value);
                  resetHfImport();
                }}
                className="input-field mt-1"
              >
                {adapters.length === 0 ? (
                  <option value={hfAdapter}>{hfAdapter}</option>
                ) : (
                  adapters.map((adapter) => (
                    <option key={adapter.name} value={adapter.name}>
                      {adapter.name}
                    </option>
                  ))
                )}
              </select>
              {selectedAdapter && (
                <p className="text-xs text-muted-foreground mt-1">{selectedAdapter.description}</p>
              )}
            </div>
            <button
              type="button"
              disabled={loading}
              onClick={handleHfImport}
              className="btn-outline min-h-9 px-4 text-sm disabled:opacity-50"
            >
              {loading ? "Importing…" : "Import from Hugging Face"}
            </button>
            {hfImported && (
              <p className="text-xs text-green-800 bg-green-50 border border-green-200 p-2">
                Imported <span className="font-mono">{hfImported.dataset_id}</span> —{" "}
                {hfImported.example_count} examples, {hfImported.categories.length} categories.
              </p>
            )}
          </div>
        )}
      </section>

      {importWarning && datasetSource === "huggingface" && hfImported && (
        <div className="text-sm text-amber-900 bg-amber-50 border border-amber-300 p-4 rounded-lg">
          <p className="font-semibold">Heads up: metric fit</p>
          <p className="mt-1 text-xs leading-relaxed">{importWarning}</p>
        </div>
      )}

      <section className="space-y-2">
        <h2 className="text-sm font-semibold">2. Run mode</h2>
        <div className="space-y-2 card-surface p-5 text-sm">
          <label className="flex items-start gap-2">
            <input
              type="radio"
              name="mode"
              checked={mode === "eval"}
              onChange={() => setMode("eval")}
              className="mt-1"
            />
            <span>
              <span className="font-medium">Direct eval</span>
              <span className="block text-xs text-muted-foreground">
                Single-shot model calls — fastest benchmark.
              </span>
            </span>
          </label>
          <label className="flex items-start gap-2">
            <input
              type="radio"
              name="mode"
              checked={mode === "agent"}
              onChange={() => setMode("agent")}
              className="mt-1"
            />
            <span>
              <span className="font-medium">Agent harness</span>
              <span className="block text-xs text-muted-foreground">
                Deep Agents orchestrator with extract → validate subagents. Same metrics
                and UI.
              </span>
            </span>
          </label>
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-semibold">3. Models (org-enabled)</h2>
        <p className="text-xs text-muted-foreground">
          Keys are stored encrypted per organization under{" "}
          <Link href="/settings" className="underline">
            Settings → Model API keys
          </Link>
          . You pay providers directly when a run executes.
        </p>
        {available.length === 0 ? (
          <p className="text-xs text-muted-foreground">
            No models enabled.{" "}
            <Link href="/settings" className="underline">
              Enable in Settings
            </Link>
            .
          </p>
        ) : (
          <div className="space-y-3 card-surface p-5">
            {available.map((model) => (
              <label key={model.id} className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={!!selected[model.id]}
                  onChange={(e) =>
                    setSelected((prev) => ({ ...prev, [model.id]: e.target.checked }))
                  }
                  className="mt-1"
                />
                <span>
                  <span className="font-medium">{model.label}</span>
                  {mode === "agent" && model.agent_supported === false && (
                    <span className="text-amber-700 text-xs ml-1">(no agent)</span>
                  )}
                  <span className="block text-xs text-muted-foreground font-mono">
                    {model.model_id}
                  </span>
                  {model.note && (
                    <span className="block text-xs text-muted-foreground">{model.note}</span>
                  )}
                </span>
              </label>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-semibold">4. Options</h2>
        <input
          type="text"
          placeholder="Run name (optional)"
          value={runName}
          onChange={(e) => setRunName(e.target.value)}
          className="input-field"
        />
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={skipJudge}
            onChange={(e) => setSkipJudge(e.target.checked)}
          />
          Skip judge validation gate (κ &lt; 0.6 abort)
        </label>
      </section>

      {error && (
        <p className="text-sm text-red-700 border border-red-300 bg-red-50 p-3">{error}</p>
      )}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={
            loading ||
            !!loadError ||
            datasetSource === "documents" ||
            (datasetSource === "huggingface" && !hfImported)
          }
          className="btn-primary disabled:opacity-50"
        >
          {loading
            ? "Starting…"
            : datasetSource === "documents"
              ? "Complete labeling template first"
            : datasetSource === "huggingface" && !hfImported
              ? "Import dataset first"
              : mode === "agent"
                ? "Run agent eval"
                : "Run eval"}
        </button>
        <Link href="/" className="text-sm text-muted-foreground hover:text-neutral-900">
          Cancel
        </Link>
      </div>
    </form>
  );
}
