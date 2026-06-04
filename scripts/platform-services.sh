#!/usr/bin/env bash
# Run all platform microservices locally (background processes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROMPT_LEDGER_ROOT="$ROOT"
export PYTHONPATH="$ROOT:$ROOT/src:${PYTHONPATH:-}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -e ".[web]"

PIDS=()
start() {
  local name=$1 port=$2 module=$3
  .venv/bin/uvicorn "$module" --host 127.0.0.1 --port "$port" &
  PIDS+=($!)
  echo "Started $name → http://127.0.0.1:$port/health"
}

trap 'kill ${PIDS[@]} 2>/dev/null || true' EXIT

start agent-service 8081 services.agent_service.main:app
start environment-service 8082 services.environment_service.main:app
start reward-service 8083 services.reward_service.main:app
start trace-service 8084 services.trace_service.main:app
start eval-service 8085 services.eval_service.main:app
start dataset-service 8086 services.dataset_service.main:app

echo ""
echo "Platform APIs ready. Example:"
echo "  curl -X POST http://127.0.0.1:8082/api/v1/env/reset -H 'Content-Type: application/json' -d '{\"environment\":\"legal\"}'"
echo "Press Ctrl+C to stop."
wait
