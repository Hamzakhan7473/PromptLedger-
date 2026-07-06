# Legal-Eval Report

**Run ID:** `20260706T213619Z_ae12c1e5`  
**Run date (UTC):** 2026-07-06T21:36:19.691439+00:00  
**Eval set SHA-256:** `d6e7a8b9cf5430ae…`

## Judge validation

- **Status:** PASSED (κ ≥ 0.6 required)
- **Cohen's κ:** 1.0000
- **Accuracy vs gold reference:** 1.0
- **Sample size:** 60 scored / 60 sampled

_Judge decisions are trustworthy for borderline span adjudication._

## Task & dataset

Models read a contract excerpt and return structured JSON: `present`, `span`, `confidence`, `reasoning`. Gold labels come from the uploaded eval set — lawyer-reviewed clause presence and verbatim span annotations.

- **Dataset:** `legal_eval_dataset_valid_schema.jsonl`
- **Eval set path:** `/Users/hamzakhan/PromptLedger/legal-eval-api/data/datasets/3d79fead0cf7/eval_set.jsonl`
- **Eval examples:** 20
- **Categories in eval set:** 15 (Arbitration, Assignment, Automatic Renewal, Confidentiality, Contract Term, Data Processing, Data Security, Force Majeure, … (+7 more))
- **Present / absent balance:** 15 present, 5 absent (75% / 25%)

| Category | Present | Absent |
|----------|---------|--------|
| Arbitration | 1 | 0 |
| Assignment | 1 | 1 |
| Automatic Renewal | 1 | 0 |
| Confidentiality | 1 | 1 |
| Contract Term | 1 | 0 |
| Data Processing | 1 | 0 |
| Data Security | 1 | 0 |
| Force Majeure | 1 | 0 |
| Governing Law | 1 | 0 |
| IP Ownership | 1 | 0 |
| Indemnification | 1 | 1 |
| Limitation of Liability | 1 | 0 |
| Payment Terms | 1 | 2 |
| Termination for Convenience | 1 | 0 |
| Warranty | 1 | 0 |

## Per-model results

| Model | Presence F1 (95% CI) | Mean span Jaccard (95% CI) | Hallucination rate | Parse error rate | ECE |
|-------|--------------------|-----------------------------||---------------------|------------------|-----|
| google | 0.909 [0.800, 1.000] | 0.691 [0.609, 0.770] | 0.000 | 0.000 | 0.1425 |
| openai | 0.968 [0.880, 1.000] | 0.691 [0.609, 0.770] | 0.000 | 0.000 | 0.0535 |

## Failure taxonomy

### google

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 7 |
| false_present | 3 |
| hallucinated_span | 0 |
| missed_present | 0 |
| parse_fail | 0 |

### openai

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 7 |
| false_present | 1 |
| hallucinated_span | 0 |
| missed_present | 0 |
| parse_fail | 0 |


### Concrete failure examples

**false_present** — `ex-014` (Assignment)
- Gold present: False; predicted present: True
- Predicted span: 'It does not mention any right to assign the contract.'
- Confidence: 1.0
- Reasoning: The excerpt directly addresses the concept of 'Assignment' by explicitly stating that the agreement 'does not mention any right to assign the contract.' This indicates that the topic of assignment has been considered in relation to the contract, even if it's to note its absence.
- Excerpt: _The agreement describes product specifications, delivery requirements, and inspection procedures. It does not mention any right to assign the contract._

**correct_present_wrong_span** — `ex-017` (Contract Term)
- Gold present: True; predicted present: True
- Predicted span: 'The term of this Agreement shall commence on the Effective Date and continue for two (2) years unless earlier terminated in accordance with this Agreement.'
- Confidence: 1.0
- Reasoning: The excerpt explicitly defines the duration of the agreement, stating its commencement and length, which directly addresses the contract term.
- Excerpt: _The term of this Agreement shall commence on the Effective Date and continue for two (2) years unless earlier terminated in accordance with this Agreement._

**false_present** — `ex-016` (Payment Terms)
- Gold present: False; predicted present: True
- Predicted span: 'Except for obligations to pay fees, neither party shall be responsible for failure to perform due to causes beyond its reasonable control.'
- Confidence: 0.86
- Reasoning: The excerpt expressly mentions an obligation to pay fees, which is a payment-related term. However, it does not provide detailed payment mechanics such as timing, invoicing, or amounts.
- Excerpt: _Except for obligations to pay fees, neither party shall be responsible for failure to perform due to causes beyond its reasonable control._

## Findings

_Write three true statements about model behavior observed in this run. Go beyond the numbers — describe systematic failure modes, category-specific weaknesses, or calibration patterns._

1. **Statement 1:** 
   > _e.g. Model X systematically misses a category when clauses appear only as a cross-reference…_

2. **Statement 2:** 
   > _e.g. High-confidence false positives cluster in categories with overlapping legal language…_

3. **Statement 3:** 
   > _e.g. Span hallucination rate increases on excerpts >6k chars, suggesting context truncation effects…_

## Reproducibility

- Full manifest: `results/20260706T213619Z_ae12c1e5/manifest.json`
- Pinned models: see `models_yaml.pinned` in manifest
- Seeds: `{"eval_set": 42, "bootstrap": 42, "judge_validation": 42}`
