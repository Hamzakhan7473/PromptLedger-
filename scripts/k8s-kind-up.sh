#!/usr/bin/env bash
# Local Kubernetes demo: kind cluster + image load + dev overlay.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLUSTER="${CLUSTER:-promptledger}"
IMAGE="${IMAGE:-promptledger/demo:dev}"

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is required: https://kind.sigs.k8s.io/" >&2
  exit 1
fi
if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required" >&2
  exit 1
fi

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  kind create cluster --name "$CLUSTER" --config "$ROOT/deploy/kubernetes/kind/cluster.yaml"
fi

export IMAGE
"$ROOT/scripts/k8s-build.sh"
kind load docker-image "$IMAGE" --name "$CLUSTER"
IMAGE="$IMAGE" "$ROOT/scripts/k8s-apply.sh" dev

echo
echo "PromptLedger on kind:"
echo "  kubectl -n promptledger get pods,svc"
echo "  kubectl -n promptledger port-forward svc/promptledger-api 8765:80"
echo "  open http://127.0.0.1:8765"
