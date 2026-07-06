#!/usr/bin/env bash
# End-to-end legal-eval pipeline: data -> models -> metrics -> judge -> validate -> calibration -> errors -> report
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if [[ -x "$ROOT/.venv/bin/python" ]]; then
    PYTHON="$ROOT/.venv/bin/python"
  else
    PYTHON="python3"
  fi
fi

export MPLCONFIGDIR="${MPLCONFIGDIR:-$ROOT/.matplotlib}"
mkdir -p "$MPLCONFIGDIR"

echo "==> legal-eval pipeline"
echo "    python: $PYTHON"
echo "    root:   $ROOT"

"$PYTHON" -m pip install -q -e ".[dev]" 2>/dev/null || "$PYTHON" -m pip install -q -e .

exec "$PYTHON" -m legaleval.pipeline --build-cuad-if-missing "$@"
