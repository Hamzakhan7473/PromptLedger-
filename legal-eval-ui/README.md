# legal-eval-ui

Static reader for [legal-eval](../legal-eval) harness output. No backend, API routes, or database — all data is read from `public/results/<run_id>/` at build/dev time.

## Copy a run from the harness

After `make eval` in `legal-eval`, copy the run folder:

```bash
cp -R legal-eval/results/<run_id> legal-eval-ui/public/results/<run_id>
# eval_set.jsonl is required for Sample Viewer:
cp legal-eval/data/eval_set.jsonl legal-eval-ui/public/results/<run_id>/eval_set.jsonl
```

Expected files:

| File | Required |
|------|----------|
| `manifest.json` | yes |
| `metrics.json` | yes |
| `errors_summary.json` | yes |
| `eval_set.jsonl` | yes (Sample Viewer) |
| `raw/<model>.jsonl` | yes |
| `judge/validation.json` | yes |
| `calibration/ece.json` | yes |
| `judge/<model>_decisions.jsonl` | optional |

A **`demo`** run is included under `public/results/demo/` for local development.

## Run

```bash
npm install
npm run dev          # development
npm run build && npm run start   # production
```

Open [http://localhost:3000](http://localhost:3000) → pick a run.

## Full product build (eval → sync → UI)

From repo root, with API keys in `legal-eval/.env` (see `legal-eval/.env.example`):

```bash
cd legal-eval
cp .env.example .env   # fill in OPENAI_API_KEY, GOOGLE_API_KEY, etc.
set -a && source .env && set +a

# smoke → eval → sync → npm build
../scripts/build-legal-eval-product.sh

# or step by step:
make eval ARGS='--models openai,google,bedrock_claude'
make sync-ui
cd ../legal-eval-ui && npm run build
```

## Views

### Summary (`/runs/<run_id>/summary`)

- **Trust banner**: judge validation κ, pass/fail, warning when κ &lt; 0.6
- **Per-model table**: presence F1 with 95% CI interval, span Jaccard, hallucination rate, parse rate, ECE
- **Calibration curves**: PNG from harness when present; otherwise reliability plot from `ece.json` bins
- **Failure taxonomy chart**: harness bucket counts per model; click a bar → filtered Comparison Grid

### Sample Viewer (`/runs/<run_id>/samples`)

- Sidebar: all eval examples (id, category, gold present/absent)
- Main panel: contract excerpt with **gold spans** (amber) and **per-model predicted spans** (distinct colors); **overlap** shown in teal
- Hallucinated spans (not a substring of excerpt) flagged in red, not highlighted in text
- Per-model: presence score, confidence, reasoning, judge verdict when adjudicated

### Comparison Grid (`/runs/<run_id>/grid`)

- Rows = examples, columns = models, fixed **gold** column (Y/N)
- Cell colors: correct (`ok`), wrong span (`span`), false present (`fp`), missed (`miss`), parse fail (`err`)
- Click a cell → Sample Viewer for that example
- Filters: category, outcome bucket, **disagreements only** (models differ on presence)
