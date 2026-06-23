# Go-live & demo recording checklist

Use this before **recording** (portfolio/GitHub launch) and before **deploying** (K8s/public URL).

Run pre-flight anytime:

```bash
./scripts/demo-check.sh   # must print "Ready to record"
```

---

## Status snapshot

| Area | Ready? | Notes |
|------|--------|-------|
| Governance CLI (audit, test, promote, evidence) | ✅ | Core product — demo this heavily |
| 4 vertical demos (Legal, Fintech, Healthcare, General) | ✅ | All pass in CI + demo-check |
| Demo UI + pipeline | ✅ | http://127.0.0.1:8765 |
| GraphRAG (stub indexes bundled) | ✅ | Works offline |
| Agent + Gym + reward + datasets (CLI/API) | ⚠️ | Works; **stub LLM** — say so on camera |
| Eval dashboard in UI | ❌ | Backend exists; no UI panel yet |
| Semantic eval in UI | ❌ | CLI only (`eval run` + OPENAI_API_KEY) |
| Real public sample data (1 vertical) | ❌ | Still synthetic fixtures |
| OSS hygiene (LICENSE, SECURITY) | ❌ | Missing |
| HOST fix (conda `HOST` env) | ⚠️ | Fixed in `run-web.sh` — **commit + push** |
| Public deploy URL | ❌ | Local only |
| K8s production data layer | ❌ | Postgres/Redis in config only |
| Auth on APIs | ❌ | Open endpoints — OK for local demo only |

**Honest pitch for recording:** Lead with **governance + deterministic eval CI**. Frame agent/RL/eval microservices as **implemented architecture + working demo loop**, not full Halluminate parity.

---

## Phase 1 — Must do before recording (P0)

- [ ] **Fix & verify local start**
  ```bash
  unset HOST   # conda sets HOST=arm64-apple-darwin20.0.0 and breaks uvicorn
  ./scripts/run-web.sh
  # → http://127.0.0.1:8765
  ```
- [ ] **Commit uncommitted fixes** (`scripts/run-web.sh` PROMPT_LEDGER_BIND)
- [ ] **`demo-check.sh` green** (audit, 6 scenarios, 4 packs, 4 verticals, agent smoke)
- [ ] **Rehearse `DEMO_RECORD.md`** once end-to-end (~5 min)
- [ ] **Prepare honest script line:** “Deterministic eval in CI is production-ready; live LLM judge and LangGraph workers are on the roadmap.”
- [ ] **Browser checklist:** Legal pipeline green → Healthcare pipeline green → Export evidence JSON → Run agent (RL env)
- [ ] **Terminal split:** `prompt-ledger audit` + `prompt-ledger test` visible on screen

---

## Phase 2 — Strongly recommended for eval-system demo (P1)

Makes the “frontier eval” story credible on camera.

- [ ] **Add Eval panel to UI** — show success rate, avg reward, trajectory count from `/api/agent/evaluate`
- [ ] **One real-data vertical** — e.g. redacted clause or public SEC excerpt in `tests/fixtures/rag/legal_policy_chunks.json` + matching scenario
- [ ] **Optional live semantic eval** — run once before recording:
  ```bash
  export OPENAI_API_KEY=...
  prompt-ledger eval run tests/scenarios/legal_contract_review.yaml
  ```
  Show terminal output; mention cost/latency
- [ ] **Update `DEMO_RECORD.md`** — add Act “Eval + trajectories” (agent run → evaluate → datasets)
- [ ] **Add `GO_LIVE.md` link in README** — this file
- [ ] **CI badge** on README (`prompt-ci.yml`)

---

## Phase 3 — GitHub / portfolio launch (P1)

- [ ] **LICENSE** (MIT or Apache-2.0)
- [ ] **SECURITY.md** (how to report issues)
- [ ] **CHANGELOG.md** — v0.1.0 highlights
- [ ] **Tag release** `v0.1.0` on GitHub
- [ ] **README “Real vs roadmap”** box — 5 bullets of what's stub vs real
- [ ] **Architecture PNG + eval story** in post caption (see chat guide)
- [ ] **Push `main`, `dev`, `staging`**

---

## Phase 4 — Deploy (before claiming “live in prod”) (P2)

- [ ] **Docker image CI** — build + push `promptledger/demo` and `promptledger/platform` to GHCR on tag
- [ ] **One public URL** — Fly.io / Railway / Render for demo API only (8765)
- [ ] **API key auth** — single `PROMPT_LEDGER_API_KEY` on web + platform services
- [ ] **Remove/gate auto-promote on main** — require approval in CI or manual promote
- [ ] **Secrets** — no default Postgres password in ConfigMap for real deploy
- [ ] **K8s smoke test** — `kubectl apply -k deploy/kubernetes/base` + health checks
- [ ] **TLS + real ingress host** (not `promptledger.local`)

---

## Phase 5 — Product truth (post-launch / roadmap) (P3)

Do **not** claim these in the demo until built.

- [ ] Real LLM calls in agent orchestrator (OpenAI + Anthropic adapters)
- [ ] LangGraph supervisor (not stub metadata)
- [ ] Temporal / Celery workers for long-horizon jobs
- [ ] Postgres trajectories (replace SQLite)
- [ ] Langfuse / OTEL wired (not config-only)
- [ ] Real eval benchmark (not same stub run × 3 models)
- [ ] Computer-use tools (Playwright, Browserbase)
- [ ] Next.js product UI (replace static demo)
- [ ] SSO / RBAC

---

## Recording day runbook

```bash
# 1. Clean start
./scripts/stop-local.sh 2>/dev/null || true
unset HOST
./scripts/demo-check.sh

# 2. Start UI (foreground — stable for OBS/Loom)
./scripts/run-web.sh

# 3. Optional: platform services in second terminal
./scripts/start-local.sh   # or skip if not showing microservices

# 4. Open
#    http://127.0.0.1:8765
#    http://127.0.0.1:8765/docs
```

**Stop after recording:** `./scripts/stop-local.sh`

---

## What to show vs what to skip

| Show on camera | Skip or label “roadmap” |
|----------------|-------------------------|
| Demo UI pipeline (4 verticals) | Next.js UI |
| Audit + test CLI | Full LangGraph runtime |
| Evidence JSON export | Computer use (QuickBooks, SAP) |
| GraphRAG context panel | Temporal workflow UI |
| Agent run + reward score | Live multi-model benchmark API |
| Architecture diagram + K8s folder | Terraform EKS apply |
| `prompt-ledger agent datasets` | Paid SaaS billing |

---

## Definition of done

**Recording-ready:** Phase 1 complete + rehearsed once.  
**Launch-ready:** Phase 1 + Phase 2 (eval panel optional but recommended) + Phase 3.  
**Deploy-ready:** Phase 1–4.
