# PromptLedger — Legal Eval (source repository)

> **End users:** this repository is for development and deployment of the product. Use the **hosted web app** at your deployed URL — you do not need to clone or run anything locally.

Maintainers: see package READMEs below for development, Docker, and Cloud Run deploy.

| Directory | Role |
|-----------|------|
| [`legal-eval/`](legal-eval/) | Python eval harness (metrics, judge, calibration) |
| [`legal-eval-api/`](legal-eval-api/) | FastAPI backend — orgs, datasets, runs, artifacts |
| [`legal-eval-ui/`](legal-eval-ui/) | Next.js web app — upload, run status, results viewer |

## Development (maintainers only)

```bash
# API + harness (local dev — not the end-user path)
cp legal-eval/.env.example legal-eval/.env   # dev model keys
make -C legal-eval-api install              # or pip install -e legal-eval-api
./scripts/start-api.sh                      # dev server :8787

# UI (points at local API or NEXT_PUBLIC_LEGAL_EVAL_API_URL)
cd legal-eval-ui && npm install && npm run dev
```

**Deploy API to Cloud Run:** [`deploy/cloudrun/deploy.sh`](deploy/cloudrun/deploy.sh)

**Local Docker smoke test (maintainers):** `docker compose up --build` (see comment in `docker-compose.yml`).

## Task

Models receive a contract excerpt and clause category; they return JSON `{present, span, confidence, reasoning}`. Gold labels come from your uploaded JSONL eval set. Metrics include presence F1 with bootstrap CIs, span Jaccard, hallucination rate, judge κ on borderline spans, and calibration (ECE).

## Background

Sample benchmark numbers and harness details: **[legal-eval/README.md](legal-eval/README.md)**
