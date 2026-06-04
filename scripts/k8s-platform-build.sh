#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${IMAGE:-promptledger/platform:latest}"
docker build -f "$ROOT/deploy/docker/Dockerfile.platform" -t "$IMAGE" "$ROOT"
echo "Built $IMAGE — deploy with: kubectl apply -k deploy/kubernetes/platform"
