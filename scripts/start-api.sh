#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVAL="$ROOT/legal-eval"
API="$ROOT/legal-eval-api"
PYTHON="${PYTHON:-$EVAL/.venv/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

if [[ -f "$EVAL/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$EVAL/.env"
  set +a
fi

"$PYTHON" -m pip install -q -e "$EVAL[agents]" -e "$API"
exec "$PYTHON" -m legal_eval_api.main
