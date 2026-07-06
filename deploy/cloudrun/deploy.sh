#!/usr/bin/env bash
# Deploy legal-eval-api to Google Cloud Run.
#
# Prerequisites:
#   - gcloud CLI authenticated
#   - Artifact Registry repo created
#   - Secrets in Google Secret Manager (not wired here yet):
#       LEGAL_EVAL_MASTER_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, etc.
#
# Build context is REPO ROOT (Dockerfile copies sibling legal-eval/).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# --- placeholders (override via env or edit) ---
: "${GCP_PROJECT_ID:=YOUR_GCP_PROJECT_ID}"
: "${GCP_REGION:=us-central1}"
: "${ARTIFACT_REPO:=legal-eval}"
: "${IMAGE_NAME:=legal-eval-api}"
: "${SERVICE_NAME:=legal-eval-api}"
: "${IMAGE_TAG:=$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"

IMAGE_URI="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Building and pushing ${IMAGE_URI}"
# gcloud reads ignore patterns from --ignore-file (Docker Desktop may not support --ignorefile).
gcloud builds submit \
  --project "${GCP_PROJECT_ID}" \
  --tag "${IMAGE_URI}" \
  --ignore-file=legal-eval-api/.dockerignore \
  --file=legal-eval-api/Dockerfile \
  .

echo "==> Deploying to Cloud Run: ${SERVICE_NAME}"
# CPU / instance tradeoffs for in-process background eval threads (jobs.py):
#
# - Default Cloud Run CPU throttling stops CPU after the HTTP response returns.
#   Long eval jobs run in daemon threads and WILL be starved or killed when the
#   container scales down or throttles CPU — a correctness risk.
#
# - --no-cpu-throttling ("CPU always allocated"): keeps CPU for background threads
#   while the instance is running. Higher cost, required stopgap until a queue/worker
#   migration (Cloud Tasks, Pub/Sub worker, etc.).
#
# - --min-instances=1: avoids scale-to-zero cold starts that discard in-flight threads.
#   Adds baseline cost (~always-on instance). Set to 0 for dev/staging to save money.
#
# Do NOT pass secrets on the command line. Wire Secret Manager in a follow-up task:
#   --set-secrets=LEGAL_EVAL_MASTER_KEY=legal-eval-master-key:latest,...
gcloud run deploy "${SERVICE_NAME}" \
  --project "${GCP_PROJECT_ID}" \
  --region "${GCP_REGION}" \
  --image "${IMAGE_URI}" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --no-cpu-throttling \
  --min-instances 1 \
  --max-instances 5 \
  --set-env-vars "LEGAL_EVAL_API_DATA=/data,LEGAL_EVAL_API_HOST=0.0.0.0,MPLCONFIGDIR=/tmp/matplotlib"

echo "==> Done. Service URL:"
gcloud run services describe "${SERVICE_NAME}" \
  --project "${GCP_PROJECT_ID}" \
  --region "${GCP_REGION}" \
  --format 'value(status.url)'

echo ""
echo "Next steps (manual):"
echo "  - Mount Cloud Storage / Filestore for LEGAL_EVAL_API_DATA and results (separate task)"
echo "  - Add Secret Manager bindings for LEGAL_EVAL_MASTER_KEY and provider API keys"
echo "  - Set LEGAL_EVAL_CORS_ORIGINS to your UI origin"
echo "  - Health check: GET {service_url}/health (already implemented in main.py)"
