# Platform microservices

| Service | Port | Role |
|---------|------|------|
| **agent-service** | 8081 | LangGraph supervisor, Temporal/Celery stubs, long-horizon tasks |
| **environment-service** | 8082 | Gym API: `reset()`, `step()`, `reward()`, `done()` |
| **reward-service** | 8083 | `0.4·correctness + 0.2·citations + 0.15·latency + 0.15·cost + 0.1·compliance` |
| **trace-service** | 8084 | Trajectory store (`state_i`, `action_i`, `observation_i`) |
| **eval-service** | 8085 | Benchmark GPT-4o, Claude, Gemini |
| **dataset-service** | 8086 | SFT, preference, DPO, GRPO JSONL |

## Local (Docker Compose)

```bash
docker compose -f deploy/compose/platform-services.yml up --build
```

## Local (process)

```bash
./scripts/platform-services.sh
```

## Kubernetes

```bash
kubectl apply -k deploy/kubernetes/platform
```

See [deploy/kubernetes/platform/README.md](../deploy/kubernetes/platform/README.md) and [deploy/helm/promptledger-platform](../deploy/helm/promptledger-platform).
