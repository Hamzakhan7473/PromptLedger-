#!/usr/bin/env bash
# Apply a Kustomize overlay (dev | staging | production).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OVERLAY="${1:-dev}"
KUSTOMIZE_PATH="$ROOT/deploy/kubernetes/overlays/$OVERLAY"
if [[ ! -d "$KUSTOMIZE_PATH" ]]; then
  echo "Unknown overlay: $OVERLAY (expected dev, staging, or production)" >&2
  exit 1
fi
kubectl apply -k "$KUSTOMIZE_PATH"
echo "Applied overlay: $OVERLAY"
