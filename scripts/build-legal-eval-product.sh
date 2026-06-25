#!/usr/bin/env bash
# End-to-end: smoke configured models → full eval → sync to UI → production build.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVAL="$ROOT/legal-eval"
UI="$ROOT/legal-eval-ui"
PYTHON="${PYTHON:-$EVAL/.venv/bin/python}"

# Models with real IDs (skip TODO placeholders in models.yaml).
MODELS="${MODELS:-openai,google,bedrock_claude}"

cd "$EVAL"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$EVAL/.matplotlib}"
mkdir -p "$MPLCONFIGDIR"

echo "==> 1/4 Smoke test ($MODELS)"
"$PYTHON" -m legaleval.smoke --models "$MODELS" || {
  echo "Smoke failed — fix models.yaml / API keys before full eval." >&2
  exit 1
}

echo ""
echo "==> 2/4 Full eval pipeline ($MODELS)"
"$PYTHON" -m legaleval.pipeline --models "$MODELS"

echo ""
echo "==> 3/4 Sync results to legal-eval-ui"
"$EVAL/scripts/sync-to-ui.sh"

echo ""
echo "==> 4/4 Build static UI"
cd "$UI"
npm run build

RUN_ID="$(basename "$(readlink "$EVAL/results/latest")")"
echo ""
echo "Product ready."
echo "  Run ID:  $RUN_ID"
echo "  Report:  $EVAL/results/$RUN_ID/REPORT.md"
echo "  Dev UI:  cd legal-eval-ui && npm run dev"
echo "  Prod:    cd legal-eval-ui && npm run start"
