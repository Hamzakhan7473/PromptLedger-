#!/usr/bin/env bash
# Copy a legal-eval run into legal-eval-ui/public/results/ for the static reader.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UI_ROOT="$(cd "$ROOT/../legal-eval-ui" && pwd)"
RUN_ID="${1:-}"

if [[ -z "$RUN_ID" ]]; then
  LATEST="$ROOT/results/latest"
  if [[ -L "$LATEST" ]]; then
    RUN_ID="$(basename "$(readlink "$LATEST")")"
  else
    echo "Usage: $0 <run_id>" >&2
    echo "  or ensure results/latest symlink exists" >&2
    exit 1
  fi
fi

SRC="$ROOT/results/$RUN_ID"
DEST="$UI_ROOT/public/results/$RUN_ID"

if [[ ! -d "$SRC" ]]; then
  echo "Run not found: $SRC" >&2
  exit 1
fi

mkdir -p "$UI_ROOT/public/results"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
cp "$ROOT/data/eval_set.jsonl" "$DEST/eval_set.jsonl"

echo "Synced $RUN_ID → legal-eval-ui/public/results/$RUN_ID"
echo "  Summary:  http://localhost:3000/runs/$RUN_ID/summary"
echo "  Grid:     http://localhost:3000/runs/$RUN_ID/grid"
echo "  Samples:  http://localhost:3000/runs/$RUN_ID/samples"
