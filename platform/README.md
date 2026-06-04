# PromptLedger Agent + RL Platform

Layered stack for multi-environment agents, trajectory logging, rewards, and RL dataset export.

| Layer | Config | Code |
|-------|--------|------|
| RL Environments | [config/environments.yaml](./config/environments.yaml) | `src/prompt_ledger/platform/environments.py` |
| Tools | [config/tools.yaml](./config/tools.yaml) | `src/prompt_ledger/platform/tools.py` |
| LLM Router | [config/models.yaml](./config/models.yaml) | `src/prompt_ledger/platform/router.py` |
| Trajectory Store | [config/observability.yaml](./config/observability.yaml) | `src/prompt_ledger/platform/trajectory_store.py` |
| Reward Engine | — | `src/prompt_ledger/platform/reward.py` |
| Evaluation | — | `src/prompt_ledger/platform/evaluation.py` |
| Orchestrator | — | `src/prompt_ledger/platform/orchestrator.py` |
| Dataset / RL | — | `src/prompt_ledger/platform/dataset.py` |

**Architecture diagram:** [docs/architecture/agent-rl-platform.md](../docs/architecture/agent-rl-platform.md)

**API (monolith):** `POST /api/agent/run`, `GET /api/agent/environments`

**Microservices:** [services/README.md](../services/README.md) — ports 8081–8086, K8s manifests in `deploy/kubernetes/platform/`

**CLI:** `prompt-ledger agent run --env legal --task "..."`

```bash
./scripts/platform-services.sh
```
