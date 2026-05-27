#!/usr/bin/env bash
# Build the PromptLedger demo container image.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${IMAGE:-promptledger/demo:latest}"
docker build -f "$ROOT/deploy/docker/Dockerfile" -t "$IMAGE" "$ROOT"
echo "Built $IMAGE"
