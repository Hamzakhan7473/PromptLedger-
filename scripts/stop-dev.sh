#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

for port in 8765 3000; do
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    kill $pids 2>/dev/null || true
    echo "Stopped port $port (pid $pids)"
  fi
done

rm -f .data/logs/demo-api.pid .data/logs/legal-eval-ui.pid
