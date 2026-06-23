#!/usr/bin/env bash
# Start PromptLedger demo UI + API (Legal / Fintech / Healthcare / General AI).
# Default: http://127.0.0.1:8765
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROMPT_LEDGER_ROOT="$ROOT"
PORT="${PORT:-8765}"
# Do not use $HOST — conda/macOS often set HOST to a machine id string.
BIND_ADDR="${PROMPT_LEDGER_BIND:-127.0.0.1}"
RELOAD="${RELOAD:-1}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -e ".[web]"
UVICORN_ARGS=(--host "$BIND_ADDR" --port "$PORT")
if [[ "$RELOAD" == "1" ]]; then
  UVICORN_ARGS+=(--reload)
fi
echo "PromptLedger demo → http://${BIND_ADDR}:${PORT}  (API docs: /docs)"
exec .venv/bin/uvicorn web.backend.main:app "${UVICORN_ARGS[@]}"
