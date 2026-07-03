# legal-eval

Frontier-grade LLM evaluation for legal contract understanding on **CUAD v1**.

Two packages:

| Directory | What it is |
|-----------|------------|
| [`legal-eval/`](legal-eval/) | Python harness — data, models, metrics, judge, calibration, REPORT.md |
| [`legal-eval-ui/`](legal-eval-ui/) | Static Next.js reader for run output (summary, grid, sample viewer) |

## Latest benchmark — `20260625T183510Z_45633959`

150 lawyer-annotated CUAD clauses · 6 categories · judge validation **PASSED** (κ = 0.754)

| Model | Presence F1 | Span Jaccard | Hallucination | ECE |
|-------|-------------|--------------|---------------|-----|
| Google Gemini 2.5 Flash | **0.897** | 0.690 | 17.1% | 0.100 |
| OpenAI GPT-5.4 mini | **0.887** | 0.669 | 9.9% | 0.085 |
| Bedrock Claude Sonnet 4.6 | **0.882** | 0.699 | 13.4% | 0.053 |

Full tables, failure taxonomy, and methodology: **[legal-eval/README.md](legal-eval/README.md)**

Browse results locally:

```bash
cd legal-eval-ui && npm install && npm run dev
# → http://localhost:3000/runs/20260625T183510Z_45633959/summary
```

## Quick start

```bash
# Harness
cd legal-eval
python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp models.yaml.example models.yaml   # pin model IDs (local, gitignored)
cp .env.example .env                 # API keys (local, gitignored)
set -a && source .env && set +a

make smoke ARGS='--models openai,google,bedrock_claude'
make eval ARGS='--models openai,google,bedrock_claude'
make sync-ui
```

One-shot smoke → eval → sync → UI build (from repo root):

```bash
./scripts/build-legal-eval-product.sh
```

## Layout

```
legal-eval/          # CUAD eval harness (Python)
legal-eval-ui/       # Static results reader (Next.js)
scripts/             # build-legal-eval-product.sh
```

## Task

Models receive a contract excerpt and clause category; they return JSON `{present, span, confidence, reasoning}`. Gold labels come from CUAD v1. Metrics include presence F1 with bootstrap CIs, span Jaccard, hallucination rate, judge κ on borderline spans, and calibration (ECE).
