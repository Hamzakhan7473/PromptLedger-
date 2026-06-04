# Demo recording script (≈5 minutes)

Use this for a screen recording, Loom, or live presentation. **Pre-flight first:**

```bash
./scripts/demo-check.sh    # must print "Ready to record"
./scripts/record-demo.sh   # starts UI at http://127.0.0.1:8765
```

Optional terminal split: run `prompt-ledger audit` and `prompt-ledger test` in a second pane for CLI credibility.

---

## 0:00 — Hook (15 sec)

> “AI teams ship prompts like code, but most teams have no CI/CD for them. **PromptLedger** is repo-native governance for Legal, Fintech, Healthcare, and enterprise AI — audits, tests, promotion, and GraphRAG context in one pipeline.”

Show GitHub README architecture image:  
`docs/architecture/kubernetes-deployment-architecture.png`

---

## 0:15 — Open the demo UI (30 sec)

1. Browser → **http://127.0.0.1:8765**
2. Point out sidebar: **Legal · Fintech · Healthcare · General**
3. Note green **API connected** pill

---

## 0:45 — Legal vertical (90 sec)

1. Select **Legal AI**
2. Read headline + “Why teams buy this” bullets
3. Scroll **Live prompt preview** — staging pin, RAG fixture, no LLM cost
4. Click **Run full demo pipeline**
5. Watch steps light up: Audit → Test → Manifest → Promote → GraphRAG
6. Status → **All checks passed**
7. Scroll **GraphRAG context** panel — `{retrieved_context}` for prompts
8. Click **Export evidence JSON** — “this is what compliance gets”

---

## 2:15 — Healthcare vertical (60 sec)

1. Switch to **Healthcare**
2. Run pipeline again — emphasize **not-medical-advice** + empty-context refusal
3. One line: “Same control plane, different pack and governance rules.”

---

## 3:15 — CLI + CI (60 sec)

Terminal:

```bash
export PROMPT_LEDGER_ROOT=$(pwd)
prompt-ledger audit
prompt-ledger test
./scripts/run-all-verticals.sh
```

> “Everything in the UI is also in the CLI and GitHub Actions — same gates before production.”

Show `.github/workflows/prompt-ci.yml` briefly if time.

---

## 3:45 — Agent + RL stack (45 sec)

Terminal or API:

```bash
prompt-ledger agent run --env contract_review --task "Review indemnity cap"
prompt-ledger agent evaluate
```

> “Trajectories capture prompt, state, tool calls, and reward. We export SFT, DPO, and GRPO datasets for the training pipeline — wired to PromptLedger governance for policy compliance.”

Show [docs/architecture/agent-rl-platform.md](docs/architecture/agent-rl-platform.md) diagram if time.

---

## 4:15 — Kubernetes (45 sec)

> “We deploy the same demo API on Kubernetes — Kustomize overlays, HPA, PDB, Ingress.”

```bash
# If cluster available:
kubectl kustomize deploy/kubernetes/overlays/dev | head -40
# Or show architecture diagram + deploy/kubernetes/README.md
```

---

## 5:00 — Close (15 sec)

> “PromptLedger: version prompts in Git, test before you burn LLM budget, promote with evidence, and ground answers with GraphRAG. Repo link in the description.”

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API offline | `pip install -e ".[web]"` then `./scripts/run-web.sh` |
| Audit fails | `prompt-ledger audit` — check `governance/governance.yaml` |
| GraphRAG fails | Bundled indexes in `demo/indexes/` — re-run `demo-check.sh` |
| Port in use | `PORT=8766 ./scripts/run-web.sh` |

## One-liner proof (no UI)

```bash
./scripts/demo-check.sh && ./scripts/run-all-verticals.sh
```
