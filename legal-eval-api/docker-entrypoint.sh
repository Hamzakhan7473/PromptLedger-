#!/bin/sh
# Create writable data dirs before uvicorn (Cloud Run ephemeral disk).
set -eu

DATA_ROOT="${LEGAL_EVAL_API_DATA:-/data}"

mkdir -p \
  "${DATA_ROOT}" \
  "${DATA_ROOT}/datasets" \
  "${DATA_ROOT}/runs" \
  "${DATA_ROOT}/job_configs" \
  "${DATA_ROOT}/document_staging" \
  /app/legal-eval/results \
  "${MPLCONFIGDIR:-/tmp/matplotlib}"

exec "$@"
