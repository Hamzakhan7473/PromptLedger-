# legal-eval

Frontier-grade LLM evaluation for legal contract understanding on CUAD.

## Latest result

After running `make eval`, open the deliverable report:

**[`results/latest/REPORT.md`](results/latest/REPORT.md)** (symlink to the most recent run)

The report includes judge validation (κ), per-model presence F1 with 95% CIs, span grounding, calibration (ECE), failure taxonomy, and a Findings section for qualitative conclusions.

Full reproducibility metadata lives in `results/<run_id>/manifest.json` (pinned model IDs, eval-set hash, seeds).

## One-command eval

```bash
cd legal-eval
python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Pin model IDs in models.yaml, then export API keys:
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GOOGLE_API_KEY=...

make eval
# equivalent: ./scripts/run_all.sh
```

Pipeline steps (single timestamped `run_id`):

1. **Data** — CUAD → `data/eval_set.jsonl`
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
| Eval set only | `python -m legaleval.data.cuad` |
| Models only | `python -m legaleval.run --models all --eval-set data/eval_set.jsonl --run-id <id>` |
| Metrics | `python -m legaleval.metrics --run-id <id> --eval-set data/eval_set.jsonl` |
| Judge | `python -m legaleval.judge adjudicate …` / `validate …` |
| Calibration | `python -m legaleval.calibration --run-id <id> --eval-set data/eval_set.jsonl` |
| Errors | `python -m legaleval.report --run-id <id> --eval-set data/eval_set.jsonl` |

## Task

Models receive a contract excerpt and clause category; they return JSON `{present, span, confidence, reasoning}`. Gold labels come from **CUAD v1** (510 contracts, 41 categories). The frozen eval set balances 6 categories × 25 examples (~50/50 present/absent).
