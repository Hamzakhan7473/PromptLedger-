#!/usr/bin/env bash
# Stop local demo API and platform microservices.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

for p in 8765 8081 8082 8083 8084 8085 8086; do
  lsof -ti :"$p" 2>/dev/null | xargs kill -9 2>/dev/null || true
done

if [[ -d .data/logs ]]; then
  rm -f .data/logs/*.pid
fi

echo "Stopped PromptLedger local services."
