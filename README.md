# PromptLedger

CI/CD for prompt governance: static audits, correctness-first RAG checks, scenario tests, and automated promotion of approved prompt versions.

## Interactive demo (Legal · Fintech · Healthcare · Enterprise AI)

```bash
./scripts/run-web.sh
# → http://127.0.0.1:8765
```

Pick a vertical in the sidebar and click **Run full demo pipeline** to show audit → test → manifest → promote → GraphRAG in one flow. See [demo/README.md](demo/README.md).

## Kubernetes deployment

Run the same demo on a cluster (kind, EKS, GKE, AKS):

```bash
./scripts/k8s-kind-up.sh
# → http://127.0.0.1:8765
```

Manifests use **Kustomize** (base + dev/staging/production overlays), probes, HPA, PDB, NetworkPolicy, and a multi-stage Dockerfile. See [deploy/kubernetes/README.md](deploy/kubernetes/README.md).

**Architecture diagram (FigJam):** [docs/architecture/kubernetes-deployment-architecture.jam](docs/architecture/kubernetes-deployment-architecture.jam) — open in [Figma FigJam](https://www.figma.com/figjam/) for the full Kubernetes deployment walkthrough.

## Quick start

```bash
cd PromptLedger
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
prompt-ledger audit
prompt-ledger test
```

Promotion (typically from CI on the default branch):

```bash
prompt-ledger promote --environment production
prompt-ledger validate-manifest
prompt-ledger evidence -o evidence/bundle.json --env staging
prompt-ledger approval request && prompt-ledger approval approve
prompt-ledger promote --require-approval --dry-run
prompt-ledger diff --env-a staging --env-b production
prompt-ledger render -p legal.contract_review --env staging --fixture tests/fixtures/rag/legal_policy_chunks.json
prompt-ledger pack verify packs/finance-assistant
```

Semantic eval (requires `OPENAI_API_KEY`):

```bash
prompt-ledger eval run tests/scenarios/legal_contract_review.yaml
```

## Layout

- `governance/` — global rules (banned phrases, RAG/citation requirements).
- `prompts/registry/` — versioned prompt packs per domain.
- `tests/scenarios/` — executable scenarios (render + schema + grounding checks).
- `graphrag/` — Go GraphRAG: label-prop communities, hierarchical summaries, REST API, PromptLedger context export ([details](graphrag/README.md)).
- `.github/workflows/` — audit, test, and promote pipeline.
- `deploy/kubernetes/` — Kustomize manifests (Ingress, HPA, PDB, NetworkPolicy).
- `docs/architecture/` — FigJam Kubernetes deployment diagram.

## Strategy and delivery

- [POSITIONING.md](POSITIONING.md) — ICP, wedge, non-goals.
- [PACKAGING.md](PACKAGING.md) — PyPI/GitHub naming before publish.
- [ROADMAP.md](ROADMAP.md) — prioritized backlog (control plane, semantic eval, packs).
