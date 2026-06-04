#!/bin/sh
set -eu
export PROMPT_LEDGER_ROOT="${PROMPT_LEDGER_ROOT:-/app}"
export PYTHONPATH="/app:/app/src:${PYTHONPATH:-}"

case "${SERVICE}" in
  agent-service)
    MODULE="services.agent_service.main:app"
    PORT="${PORT:-8081}"
    ;;
  environment-service)
    MODULE="services.environment_service.main:app"
    PORT="${PORT:-8082}"
    ;;
  reward-service)
    MODULE="services.reward_service.main:app"
    PORT="${PORT:-8083}"
    ;;
  trace-service)
    MODULE="services.trace_service.main:app"
    PORT="${PORT:-8084}"
    ;;
  eval-service)
    MODULE="services.eval_service.main:app"
    PORT="${PORT:-8085}"
    ;;
  dataset-service)
    MODULE="services.dataset_service.main:app"
    PORT="${PORT:-8086}"
    ;;
  *)
    echo "Unknown SERVICE=${SERVICE}" >&2
    exit 1
    ;;
esac

exec uvicorn "$MODULE" --host 0.0.0.0 --port "$PORT"
