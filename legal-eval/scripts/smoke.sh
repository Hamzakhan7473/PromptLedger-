#!/usr/bin/env bash
# Pre-flight smoke test: first 3 eval examples × every model in models.yaml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
exec "$PYTHON" -m legaleval.smoke "$@"
