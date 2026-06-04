# Kubernetes platform microservices

Six services on top of the PromptLedger control plane:

| Deployment | Service | Port | API prefix |
|------------|---------|------|------------|
| `agent-service` | LangGraph / Temporal / multi-agent | 8081 | `/api/v1/agent` |
| `environment-service` | Gym `reset` `step` `reward` `done` | 8082 | `/api/v1/env` |
| `reward-service` | Weighted reward formula | 8083 | `/api/v1/reward` |
| `trace-service` | Trajectory store | 8084 | `/api/v1/trace` |
| `eval-service` | Model benchmarks | 8085 | `/api/v1/eval` |
| `dataset-service` | SFT / DPO / GRPO export | 8086 | `/api/v1/datasets` |

## Deploy

```bash
# Build platform image
docker build -f deploy/docker/Dockerfile.platform -t promptledger/platform:latest .

# With demo API namespace
kubectl apply -k deploy/kubernetes/base
kubectl apply -k deploy/kubernetes/platform
```

Ingress host: **platform.promptledger.local**

## Stack (roadmap wiring)

- **Postgres / Redis / S3** — URLs in `platform-services-config` ConfigMap
- **Qdrant** — vector retrieval
- **Langfuse + OTEL + Prometheus** — observability env vars
- **Helm / ArgoCD / Terraform** — see `deploy/helm/` and `deploy/terraform/`

Architecture: [docs/architecture/microservices-kubernetes.md](../../docs/architecture/microservices-kubernetes.md)
