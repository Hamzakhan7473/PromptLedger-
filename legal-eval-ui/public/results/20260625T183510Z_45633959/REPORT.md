# Legal-Eval Report

**Run ID:** `20260625T183510Z_45633959`  
**Run date (UTC):** 2026-06-25T18:35:10.732395+00:00  
**Eval set SHA-256:** `187a9b90cea40049…`

## Judge validation

- **Status:** PASSED (κ ≥ 0.6 required)
- **Cohen's κ:** 0.7541
- **Accuracy vs CUAD reference:** 0.9
- **Sample size:** 60 scored / 60 sampled

_Judge decisions are trustworthy for borderline span adjudication._

## Task & dataset

Models read a contract excerpt and return structured JSON: `present`, `span`, `confidence`, `reasoning`. Gold labels come from **CUAD v1** (Atticus Project) — 41 legal clause categories, lawyer-review annotations.

- **Eval examples:** 150
- **Categories in eval set:** 6
- **Present / absent balance:** 72 present, 78 absent (48% / 52%)

| Category | Present | Absent |
|----------|---------|--------|
| Affiliate License-Licensee | 12 | 13 |
| Affiliate License-Licensor | 12 | 13 |
| Agreement Date | 12 | 13 |
| Anti-Assignment | 12 | 13 |
| Audit Rights | 12 | 13 |
| Cap On Liability | 12 | 13 |

## Per-model results

| Model | Presence F1 (95% CI) | Mean span Jaccard (95% CI) | Hallucination rate | Parse error rate | ECE |
|-------|--------------------|-----------------------------||---------------------|------------------|-----|
| anthropic | 0.000 n/a | 0.000 n/a | 0.000 | 1.000 | 0.0 |
| bedrock_claude | 0.882 [0.824, 0.934] | 0.699 [0.625, 0.777] | 0.134 | 0.000 | 0.0532 |
| google | 0.897 [0.844, 0.945] | 0.690 [0.625, 0.757] | 0.171 | 0.000 | 0.100334 |
| open | 0.000 n/a | 0.000 n/a | 0.000 | 1.000 | 0.0 |
| openai | 0.887 [0.826, 0.934] | 0.669 [0.598, 0.735] | 0.099 | 0.000 | 0.084599 |

## Failure taxonomy

### anthropic

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 0 |
| false_present | 0 |
| hallucinated_span | 0 |
| missed_present | 0 |
| parse_fail | 150 |

### bedrock_claude

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 27 |
| false_present | 13 |
| hallucinated_span | 9 |
| missed_present | 5 |
| parse_fail | 0 |

### google

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 27 |
| false_present | 14 |
| hallucinated_span | 12 |
| missed_present | 2 |
| parse_fail | 0 |

### open

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 0 |
| false_present | 0 |
| hallucinated_span | 0 |
| missed_present | 0 |
| parse_fail | 150 |

### openai

| Bucket | Count |
|--------|-------|
| correct_present_wrong_span | 30 |
| false_present | 17 |
| hallucinated_span | 7 |
| missed_present | 1 |
| parse_fail | 0 |


### Concrete failure examples

**parse_fail** — `cuad-00000` (Affiliate License-Licensee)
- Gold present: True; predicted present: None
- Predicted span: None
- Confidence: None
- Excerpt: _Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee P..._

**missed_present** — `cuad-00128` (Cap On Liability)
- Gold present: True; predicted present: False
- Predicted span: None
- Confidence: 0.85
- Reasoning: The excerpt contains a Limitation of Liability clause (Section 13.5) that excludes certain types of damages (consequential, incidental, punitive, etc.), but it does not impose a monetary cap or ceiling on the total amount of liability either party may face. A "Cap on Liability" clause specifically limits the maximum dollar amount recoverable, which is absent here.
- Excerpt: _itee shall have reasonably concluded, based upon a written opinion from outside legal counsel, that there is a conflict of interest between the Indemnifying Party and the Indemnitee in the defense of such Claim, in which case the Indemnifying Party shall pay the fees and expen..._

**false_present** — `cuad-00065` (Agreement Date)
- Gold present: False; predicted present: True
- Predicted span: 'Effective Date: April 17, 2017'
- Confidence: 1.0
- Reasoning: The excerpt explicitly states the effective date of the agreement at the very beginning, identifying "Effective Date: April 17, 2017" and further referencing it as "the date set forth above (the 'Effective Date')" in the body of the agreement.
- Excerpt: _Exhibit 10.1   Text Marked By [* * *] Has Been Omitted Pursuant To A Request For Confidential Treatment And Was Filed Separately With The Securities And Exchange Commission.   STRATEGIC ALLIANCE AGREEMENT Effective Date: April 17, 2017   THIS STRATEGIC ALLIANCE AGREEMENT (this..._

## Findings

_Write three true statements about model behavior observed in this run. Go beyond the numbers — describe systematic failure modes, category-specific weaknesses, or calibration patterns._

1. **Statement 1:** 
   > _e.g. Model X systematically misses `Anti-Assignment` clauses when they appear only as a cross-reference…_

2. **Statement 2:** 
   > _e.g. High-confidence false positives cluster in categories with overlapping legal language…_

3. **Statement 3:** 
   > _e.g. Span hallucination rate increases on excerpts >6k chars, suggesting context truncation effects…_

## Reproducibility

- Full manifest: `results/20260625T183510Z_45633959/manifest.json`
- Pinned models: see `models_yaml.pinned` in manifest
- Seeds: `{"eval_set": 42, "bootstrap": 42, "judge_validation": 42}`
