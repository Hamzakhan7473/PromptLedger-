# legal-eval API

HTTP layer for **upload → model routing → eval pipeline** — deployed as the hosted web product backend.

Wraps the `legaleval` harness (`legal-eval[agents]` path dependency in `pyproject.toml`).

## End users

Use the **hosted web app**. Create an org in Settings, add model keys, upload JSONL, start runs from New eval. No local install required.

Public demo (no login): `GET /api/v1/demo` returns a share-token URL for the bundled demo run.

## Maintainers — run locally

```bash
cd legal-eval-api
pip install -e ".[dev]"   # requires sibling ../legal-eval
./scripts/start-api.sh    # dev only — sources legal-eval/.env
# → http://127.0.0.1:8787
```

## Docker (Cloud Run image)

Build from **repository root** (sibling `legal-eval/` must be in context):

```bash
docker build -f legal-eval-api/Dockerfile -t legal-eval-api .
docker run --rm -p 8080:8080 \
  -e LEGAL_EVAL_API_DATA=/data \
  -e LEGAL_EVAL_CORS_ORIGINS=http://localhost:3000 \
  legal-eval-api
curl -s http://127.0.0.1:8080/health
```

Environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `8080` | Cloud Run injects this; uvicorn binds `0.0.0.0:$PORT` |
| `LEGAL_EVAL_API_DATA` | `/data` in container | SQLite, datasets, run job metadata |
| `LEGAL_EVAL_MASTER_KEY` | *(file under data dir)* | Fernet key for org secrets — set via Secret Manager in prod |
| `LEGAL_EVAL_CORS_ORIGINS` | localhost UI origins | Comma-separated allowed origins |
| `LEGAL_EVAL_DEMO_SHARE_TOKEN` | `le_demo_public_v1` | Public demo share token |

Deploy: [`../deploy/cloudrun/deploy.sh`](../deploy/cloudrun/deploy.sh) (uses `--no-cpu-throttling` + `--min-instances=1` stopgap for in-process background jobs).

## Endpoints (selected)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness |
| GET | `/api/v1/demo` | — | Public demo run link |
| POST | `/api/v1/orgs` | — | Create organization |
| POST | `/api/v1/datasets` | Bearer | Upload `.jsonl` |
| POST | `/api/v1/runs` | Bearer | Start eval (background thread) |
| GET | `/api/v1/runs/{id}/artifacts` | Bearer or `?token=` | UI artifact bundle |

Auth: `Authorization: Bearer le_org_...`

## Data layout

```
$LEGAL_EVAL_API_DATA/
  legal_eval.db
  .master_key
  datasets/<id>/eval_set.jsonl
  document_staging/<staging_id>/
  runs/<run_id>.json
```

Harness artifacts: `legal-eval/results/<run_id>/` (bundled demo run seeded at startup).

## Tests

```bash
cd legal-eval-api
PYTHONPATH=src:../legal-eval/src python -m pytest -q
```
