# Roadmap (issue-shaped)

Use this list to open GitHub issues; order is suggested priority for a **regulated-team** buyer.

## P0 — Product wrapper (control plane)

- [x] **Promotion requests:** `prompt-ledger approval request|approve|decline|status` (`.promptledger/approval.yaml`).
- [x] **Diff views:** `prompt-ledger diff` (manifest + prompt text).
- [x] **Evidence export:** `prompt-ledger evidence -o …` (JSON bundle; CI artifact).
- [x] **Ownership metadata:** audit checks `owner` / `risk_tier` on registry packs.

## P1 — Semantic evaluation (on top of static checks)

- [x] **Dataset-driven runs:** `prompt-ledger eval run` (OPENAI_API_KEY; optional in CI).
- [x] **Pairwise or score-based comparison:** `prompt-ledger eval compare`.
- [x] **Human review queue** hook: `PROMPT_LEDGER_REVIEW_WEBHOOK_URL` on `evidence --notify-review`.

## P2 — Enterprise-shaped capabilities

- [ ] **SSO / RBAC** (only if you ship a hosted or private appliance; not required for OSS CLI-only).
- [ ] **Self-hosted / VPC** deployment story for the control plane when it exists.
- [ ] **Audit log retention** policy and export for compliance questionnaires.

## P3 — Moat: policy packs

- [x] **Pack format:** `packs/finance-assistant/` (governance + scenarios + schemas).
- [x] **Pack verifier:** `prompt-ledger pack verify <dir>`.

## Ongoing

- [ ] **Rename / packaging** alignment per `PACKAGING.md` before first PyPI publish.

## GraphRAG (Go) — completed

- [x] Label-propagation + weighted entity graph
- [x] Hierarchical meta-communities (`-algo hierarchical`)
- [x] `batch`, `context`, `validate`, `serve` (REST), `query --json`
- [x] Public API `pkg/graphrag` + `pkg/contextfmt` for PromptLedger
- [x] Index metadata (`meta.community_algorithm`, counts)
- [x] **GraphRAG bridge:** `graphrag_index` in scenarios + `prompt-ledger render --graphrag-index`
- [x] **CLI extensions:** `validate-manifest`, `render`, `promote --dry-run --set --require-approval`, `--json` on audit/test
