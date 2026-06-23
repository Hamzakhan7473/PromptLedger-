#!/usr/bin/env bash
# Start PromptLedger API (:8765) + legal-eval-ui (:3000). Survives terminal close.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p .data/logs

# conda/macOS often set HOST to a machine id and break uvicorn
unset HOST
export PROMPT_LEDGER_ROOT="$ROOT"

stop_port() {
  local port=$1
  local pids
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    kill $pids 2>/dev/null || true
    sleep 1
  fi
}

stop_port 8765
stop_port 3000

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Missing .venv — run: python3 -m venv .venv && .venv/bin/pip install -e '.[web]'"
  exit 1
fi

if [[ ! -d legal-eval-ui/node_modules ]]; then
  echo "Missing legal-eval-ui deps — run: cd legal-eval-ui && npm install"
  exit 1
fi

nohup .venv/bin/uvicorn web.backend.main:app --host 127.0.0.1 --port 8765 \
  >> .data/logs/demo-api.log 2>&1 &
echo $! > .data/logs/demo-api.pid
disown

nohup npm run dev --prefix legal-eval-ui -- --port 3000 \
  >> .data/logs/legal-eval-ui.log 2>&1 &
echo $! > .data/logs/legal-eval-ui.pid
disown

echo "Waiting for servers..."
for i in {1..30}; do
  up=0
  curl -sf http://127.0.0.1:8765/ >/dev/null 2>&1 && up=$((up + 1))
  curl -sf http://127.0.0.1:3000/ >/dev/null 2>&1 && up=$((up + 1))
  if [[ $up -eq 2 ]]; then
    echo ""
    echo "  PromptLedger (API + demo UI):  http://127.0.0.1:8765"
    echo "  legal-eval-ui:                 http://127.0.0.1:3000"
    echo "  Logs:  .data/logs/demo-api.log  .data/logs/legal-eval-ui.log"
    echo "  Stop:  ./scripts/stop-dev.sh"
    exit 0
  fi
  sleep 1
done

echo "Servers did not become ready. Tail logs:"
tail -20 .data/logs/demo-api.log 2>/dev/null || true
tail -20 .data/logs/legal-eval-ui.log 2>/dev/null || true
exit 1
