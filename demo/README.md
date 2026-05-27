# PromptLedger interactive demo

Multi-vertical showcase for **Legal**, **Fintech**, **Healthcare**, and **General enterprise AI**.

## Run the demo UI

```bash
cd ..
./scripts/run-web.sh
```

Open **http://127.0.0.1:8765** (or set `PORT=8765`).

## Presenter flow (5 minutes)

1. **Pick a vertical** in the sidebar — each maps to a real prompt ID, pack, and RAG fixtures in this repo.
2. **Walk the live prompt preview** — staging pin + fixture chunks; no LLM spend.
3. Click **Run full demo pipeline** — audit → scenarios → manifest → promote (dry-run) → GraphRAG context.
4. Expand **GraphRAG context** — show how community summaries land in `{retrieved_context}`.
5. **Export evidence JSON** — one file for security / compliance reviewers.

Repeat for a second vertical (e.g. Legal → Healthcare) to show the same control plane across genres.

## CLI (per vertical)

```bash
export PROMPT_LEDGER_ROOT=$(pwd)
prompt-ledger audit
prompt-ledger test
prompt-ledger pack verify packs/legal-assistant

# Full vertical demo payload (JSON)
python -c "import json; from prompt_ledger.demo import run_vertical_demo; print(json.dumps(run_vertical_demo('legal'), indent=2))"
```

## Verticals

| ID | Prompt | Pack |
|----|--------|------|
| `legal` | `legal.contract_review` | `packs/legal-assistant` |
| `fintech` | `finance.transaction_classification` | `packs/finance-assistant` |
| `healthcare` | `healthcare.clinical_guidance` | `packs/healthcare-assistant` |
| `general` | `general.policy_support` | `packs/general-assistant` |

Corpus text for GraphRAG lives under `demo/corpora/`. Pre-built stub indexes ship in `demo/indexes/` so demos work without Go; the UI will rebuild indexes when Go is available.
