#!/usr/bin/env bash
# Start demo API + all platform microservices locally.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROMPT_LEDGER_ROOT="$ROOT"
export PYTHONPATH="$ROOT:$ROOT/src"
export PATH="/usr/bin:/bin:/opt/homebrew/bin:$PATH"

UV="$ROOT/.venv/bin/uvicorn"
mkdir -p .data/logs

if [[ ! -x "$UV" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -e ".[dev,web]"
fi

echo "Starting PromptLedger locally..."
nohup "$UV" web.backend.main:app --host 127.0.0.1 --port 8765 > .data/logs/demo-api.log 2>&1 &
echo $! > .data/logs/demo-api.pid

for spec in \
  "8081:services.agent_service.main:app:agent" \
  "8082:services.environment_service.main:app:env" \
  "8083:services.reward_service.main:app:reward" \
  "8084:services.trace_service.main:app:trace" \
  "8085:services.eval_service.main:app:eval" \
  "8086:services.dataset_service.main:app:dataset"; do
  IFS=: read -r port module logname <<< "$spec"
  nohup "$UV" "$module" --host 127.0.0.1 --port "$port" > ".data/logs/${logname}.log" 2>&1 &
  echo $! > ".data/logs/${logname}.pid"
done

sleep 2
echo ""
echo "  Demo UI:   http://127.0.0.1:8765"
echo "  API docs:  http://127.0.0.1:8765/docs"
echo "  Platform:  :8081 agent · :8082 env · :8083 reward · :8084 trace · :8085 eval · :8086 dataset"
echo "  Logs:      .data/logs/"
echo "  Stop:      ./scripts/stop-local.sh"
