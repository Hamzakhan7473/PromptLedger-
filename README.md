# PromptLedger

CI/CD for prompt governance: static audits, correctness-first RAG checks, scenario tests, and automated promotion of approved prompt versions.

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
```

## Layout

- `governance/` — global rules (banned phrases, RAG/citation requirements).
- `prompts/registry/` — versioned prompt packs per domain.
- `tests/scenarios/` — executable scenarios (render + schema + grounding checks).
- `graphrag/` — Go implementation of a GraphRAG-style index + global query pipeline ([details](graphrag/README.md)).
- `.github/workflows/` — audit, test, and promote pipeline.

## Strategy and delivery

- [POSITIONING.md](POSITIONING.md) — ICP, wedge, non-goals.
- [PACKAGING.md](PACKAGING.md) — PyPI/GitHub naming before publish.
- [ROADMAP.md](ROADMAP.md) — prioritized backlog (control plane, semantic eval, packs).
