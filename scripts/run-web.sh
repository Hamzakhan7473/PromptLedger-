#!/usr/bin/env bash
# Start PromptLedger demo UI + API (Legal / Fintech / Healthcare / General AI).
# Default: http://127.0.0.1:8765
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROMPT_LEDGER_ROOT="$ROOT"
PORT="${PORT:-8765}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -e ".[web]"
exec .venv/bin/uvicorn web.backend.main:app --host 127.0.0.1 --port "$PORT" --reload
