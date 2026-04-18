# Positioning

## One-liner

**Repo-native AI change control for teams that must prove process:** version prompts and manifests in Git, run policy and contract checks in CI, promote pins across environments, and retain evidence—not a generic hosted prompt editor.

## Who it’s for (ICP)

**Primary:** Fintech and adjacent regulated deployments where model/prompt change needs traceability: who changed what, which rules passed, which tests ran, what shipped to production.

**Secondary:** Legal-tech and professional services where citation, confidentiality, and human-review checkpoints matter—often as a second wedge after finance.

**Early design partners, not core ACV:** Agencies and lean product teams—good for UX and workflow feedback; weaker as the sole long-term revenue story unless they adopt formal approval needs.

## Wedge

Sell **governance + evidence**, not “another prompt registry.” Differentiators to lean into:

- **Policy-as-code** merged with per-version overrides (bans, markers, RAG grounding, refusal behavior, output schemas).
- **Deterministic preflight** (render, placeholders, fixtures, golden JSON vs schema) so CI answers “does it still conform?” without billing LLM calls on every commit.
- **Manifest-based promotion** (environment pins) with optional hooks—aligned with PR review and branch protection, not a black-box UI as source of truth.

## Non-goals (today)

- Replacing LangSmith / PromptLayer / W&B as the full observability or online-eval platform.
- Being the primary semantic-quality judge without human or dataset context—static checks are necessary, not sufficient.
- A multi-user web control plane or SSO/RBAC in this open-source core (see `ROADMAP.md`).

## Competitive frame

Category leaders already ship versioning, envs, evals, and enterprise controls. PromptLedger’s angle is **Git-first change control and audit-ready gates**, not feature parity with hosted platforms. Closest mental model for buyers: **release and approval workflows for AI behavior** (cf. feature-flag / config control products), with evidence export for review.

## Honest boundary

Strength: **contract and policy enforcement before merge and promote.**  
Gap: **semantic regression and production feedback** must be layered on (datasets, LLM-as-judge, traces)—see `ROADMAP.md`.
