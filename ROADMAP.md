# Roadmap (issue-shaped)

Use this list to open GitHub issues; order is suggested priority for a **regulated-team** buyer.

## P0 — Product wrapper (control plane)

- [ ] **Promotion requests:** open/approve/decline flow tied to PR or manifest diff (even if MVP is GitHub-only + labels).
- [ ] **Diff views:** prompt text + manifest pin changes in one review surface (can start as CI comment or static HTML export).
- [ ] **Evidence export:** single artifact (JSON/PDF bundle) listing commit, ruleset hash, audit result, scenario list, promoter identity—for internal or external review.
- [ ] **Ownership metadata:** enforce `owner` / `risk_tier` in registry with CODEOWNERS-style routing (docs + optional validator).

## P1 — Semantic evaluation (on top of static checks)

- [ ] **Dataset-driven runs:** optional LLM/API calls in CI or nightly, gated by secrets, with regression baselines.
- [ ] **Pairwise or score-based comparison** between prompt versions on the same scenarios.
- [ ] **Human review queue** hook (export to ticketing or webhook) for high-risk tiers.

## P2 — Enterprise-shaped capabilities

- [ ] **SSO / RBAC** (only if you ship a hosted or private appliance; not required for OSS CLI-only).
- [ ] **Self-hosted / VPC** deployment story for the control plane when it exists.
- [ ] **Audit log retention** policy and export for compliance questionnaires.

## P3 — Moat: policy packs

- [ ] **Pack format:** versioned bundle of governance YAML + scenarios + schemas (e.g. finance-assistant, legal-drafting, high-risk logging).
- [ ] **Pack verifier:** CLI that checks a repo against a pack and emits a signed summary for auditors.

## Ongoing

- [ ] **Rename / packaging** alignment per `PACKAGING.md` before first PyPI publish.
- [ ] **GraphRAG module:** optional integration story (index artifacts + citation in prompts)—separate from core governance CLI.
