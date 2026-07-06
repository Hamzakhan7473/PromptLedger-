# legal-eval

Frontier-grade LLM evaluation for **legal clause presence detection and span extraction** on any JSONL eval set you provide.

## Eval set format (primary interface)

Each line of `eval_set.jsonl` is one `EvalExample`:

```json
{
  "id": "ex-001",
  "contract_excerpt": "Section 3. Assignment. No party may assign without prior written consent.",
  "category": "Anti-Assignment",
  "present": true,
  "gold_spans": ["No party may assign without prior written consent"],
  "contract_title": "Master Services Agreement"
}
```

| Field | Meaning |
|-------|---------|
| `id` | Stable example identifier |
| `contract_excerpt` | Contract text shown to the model |
| `category` | Clause type label (any string — not limited to CUAD) |
| `present` | Whether the category is substantively present |
| `gold_spans` | Verbatim reference span(s) when `present=true`; `[]` when absent |
| `contract_title` | Human-readable contract name |

Upload this JSONL via the API/UI, or point the CLI at it with `--eval-set PATH`.

**Optional CUAD adapter:** To build a balanced sample from [CUAD v1](https://huggingface.co/datasets/theatticusproject/cuad) (6 categories × 25 examples, ~50/50 present/absent):

```bash
python -m legaleval.data.cuad          # writes data/eval_set.jsonl
# or, on first pipeline run without an existing file:
python -m legaleval.pipeline --build-cuad-if-missing
```

## Latest result — `20260625T183510Z_45633959`

**Run date (UTC):** 2026-06-25 · **Eval examples:** 150 (6 CUAD categories, ~50/50 present/absent)

### Judge validation

| Metric | Value |
|--------|-------|
| Status | **PASSED** (κ ≥ 0.6 required) |
| Cohen's κ | **0.754** |
| Accuracy vs gold reference | 0.90 |
| Sample size | 60 / 60 |

### Per-model results (production models)

| Model | Provider | Presence F1 (95% CI) | Span Jaccard (95% CI) | Hallucination | Parse errors | ECE |
|-------|----------|----------------------|------------------------|---------------|--------------|-----|
| **google** | Gemini 2.5 Flash | **0.897** [0.844, 0.945] | 0.690 [0.625, 0.757] | 17.1% | 0% | 0.100 |
| **openai** | GPT-5.4 mini | **0.887** [0.826, 0.934] | 0.669 [0.598, 0.735] | 9.9% | 0% | 0.085 |
| **bedrock_claude** | Claude Sonnet 4.6 (Bedrock) | **0.882** [0.824, 0.934] | 0.699 [0.625, 0.777] | 13.4% | 0% | 0.053 |

**Takeaways:** All three frontier models achieve ~0.88–0.90 presence F1 on lawyer-annotated clauses. Google leads on presence F1; Bedrock has the lowest ECE (best calibration). OpenAI has the lowest hallucination rate (9.9%). Dominant failure mode across models is **correct presence, wrong span** (~27–30 examples each).

### Failure taxonomy (production models)

| Bucket | google | openai | bedrock_claude |
|--------|--------|--------|----------------|
| correct_present_wrong_span | 27 | 30 | 27 |
| false_present | 14 | 17 | 13 |
| hallucinated_span | 12 | 7 | 9 |
| missed_present | 2 | 1 | 5 |
| parse_fail | 0 | 0 | 0 |

### Browse results in the UI

Static reader: [legal-eval-ui](../legal-eval-ui) — run synced to `public/results/20260625T183510Z_45633959/`

- [Summary](http://localhost:3000/runs/20260625T183510Z_45633959/summary) · [Grid](http://localhost:3000/runs/20260625T183510Z_45633959/grid) · [Samples](http://localhost:3000/runs/20260625T183510Z_45633959/samples)

Full machine-readable report: [`results/20260625T183510Z_45633959/REPORT.md`](results/20260625T183510Z_45633959/REPORT.md) (local; not committed — regenerate via `make eval`).

## One-command eval

```bash
cd legal-eval
python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Pin model IDs in models.yaml (copy from models.yaml.example; local, gitignored), then API keys in .env:
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GOOGLE_API_KEY=...

make eval
# scope models: make eval ARGS='--models openai,google,bedrock_claude'

# Pre-flight (3 examples per model):
make smoke ARGS='--models openai,google,bedrock_claude'

# Sync latest run to legal-eval-ui:
make sync-ui
```

`make eval` runs the pipeline with `--build-cuad-if-missing` when `data/eval_set.jsonl` is absent. For your own dataset:

```bash
python -m legaleval.pipeline --eval-set path/to/my_eval_set.jsonl --models openai
```

Pipeline steps (single timestamped `run_id`):

1. **Data** — load `--eval-set` JSONL (or build CUAD sample if `--build-cuad-if-missing`)
2. **Models** — all providers in `models.yaml`
3. **Metrics** — presence, span grounding, reliability
4. **Judge** — borderline span adjudication (Jaccard 0.2–0.7)
5. **Judge validate** — κ ≥ 0.6 gate (aborts if failed)
6. **Calibration** — ECE + reliability curves
7. **Errors** — failure taxonomy markdown
8. **Manifest + REPORT.md**

Outputs under `results/<run_id>/`:

```
results/<run_id>/
  manifest.json      # models, hashes, seeds
  REPORT.md          # deliverable summary
  metrics.json
  errors_summary.json
  raw/<model>.jsonl
  judge/validation.json
  calibration/ece.json, <model>.png
  errors/<model>.md
```

## Setup

```bash
pip install -e ".[dev]"   # or: uv sync --extra dev
pytest
```

## Individual stages

| Stage | Command |
|-------|---------|
| CUAD sample (optional) | `python -m legaleval.data.cuad` |
| Models only | `python -m legaleval.run --models all --eval-set data/eval_set.jsonl --run-id <id>` |
| Metrics | `python -m legaleval.metrics --run-id <id> --eval-set data/eval_set.jsonl` |
| Judge | `python -m legaleval.judge adjudicate …` / `validate …` |
| Calibration | `python -m legaleval.calibration --run-id <id> --eval-set data/eval_set.jsonl` |
| Errors | `python -m legaleval.report --run-id <id> --eval-set data/eval_set.jsonl` |

## Task

Models receive a contract excerpt and clause category; they return JSON `{present, span, confidence, reasoning}`. Gold labels come from your eval set JSONL. CUAD v1 is supported as an optional adapter to generate a balanced benchmark set (510 contracts, 41 categories in the full corpus; default sample uses 6 categories × 25 examples).
