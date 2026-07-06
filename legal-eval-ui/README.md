# legal-eval-ui

Next.js web app for the **hosted Legal Eval product** — org settings, dataset upload, run status, summary / grid / sample viewer.

Runs fetch artifacts from the API at runtime (`NEXT_PUBLIC_LEGAL_EVAL_API_URL`).

## End users

Open the deployed app URL. Create an org in **Settings**, add model keys, upload JSONL on **New eval**, browse results when complete.

**Demo (no login):** landing page links to `/runs/demo/summary?token=le_demo_public_v1` (token configurable via `NEXT_PUBLIC_DEMO_SHARE_TOKEN`).

## Maintainers — local dev

```bash
npm install
export NEXT_PUBLIC_LEGAL_EVAL_API_URL=http://127.0.0.1:8787
npm run dev
```

Static files under `public/results/demo/` are the source for the API's bundled demo run (copied to `legal-eval-api/demo_run/demo` for Docker).

## Views

- **Summary** — per-model metrics, calibration, failure taxonomy
- **Grid** — model × example comparison with filters
- **Samples** — span highlighting and judge decisions

See component README in repo history for field-level artifact requirements.
