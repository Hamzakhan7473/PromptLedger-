# Error report — `google`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | _none_ | 0 |
| false_present | Assignment | 1 |
| false_present | Indemnification | 1 |
| false_present | Payment Terms | 1 |
| correct_present_wrong_span | Arbitration | 1 |
| correct_present_wrong_span | Automatic Renewal | 1 |
| correct_present_wrong_span | Confidentiality | 1 |
| correct_present_wrong_span | Contract Term | 1 |
| correct_present_wrong_span | Force Majeure | 1 |
| correct_present_wrong_span | IP Ownership | 1 |
| correct_present_wrong_span | Termination for Convenience | 1 |
| hallucinated_span | _none_ | 0 |
| parse_fail | _none_ | 0 |

## missed_present (0 total)

_No errors in this bucket._

## false_present (3 total)

### Worst 3 examples

### 1. `ex-014` — Assignment

**Contract:** Manufacturing Supply Agreement

**Excerpt:**
```
The agreement describes product specifications, delivery requirements, and inspection procedures. It does not mention any right to assign the contract.
```

**Gold:** present=False

**Prediction:** present=True, span='It does not mention any right to assign the contract.', confidence=1.0

**Reasoning:** The excerpt directly addresses the concept of 'Assignment' by explicitly stating that the agreement 'does not mention any right to assign the contract.' This indicates that the topic of assignment has been considered in relation to the contract, even if it's to note its absence.

### 2. `ex-019` — Indemnification

**Contract:** Beta Testing Agreement

**Excerpt:**
```
The parties may exchange notices by email or certified mail. This section does not provide any indemnity obligation.
```

**Gold:** present=False

**Prediction:** present=True, span='This section does not provide any indemnity obligation.', confidence=1.0

**Reasoning:** The excerpt explicitly mentions 'indemnity obligation' and states that it is not provided, thereby substantively addressing the concept of indemnification by denying its presence in that section.

### 3. `ex-002` — Payment Terms

**Contract:** Strategic Partnership Agreement

**Excerpt:**
```
The parties agree to cooperate in good faith during the term of this Agreement. No payment schedule is stated in this section.
```

**Gold:** present=False

**Prediction:** present=True, span='No payment schedule is stated in this section.', confidence=0.95

**Reasoning:** The excerpt explicitly mentions 'No payment schedule is stated in this section,' directly addressing the concept of payment terms, even if it's to state their absence within that specific section.

## correct_present_wrong_span (7 total)

### Worst 7 examples

### 1. `ex-017` — Contract Term

**Contract:** Reseller Agreement

**Excerpt:**
```
The term of this Agreement shall commence on the Effective Date and continue for two (2) years unless earlier terminated in accordance with this Agreement.
```

**Gold:** present=True
  - spans: ['continue for two (2) years unless earlier terminated']

**Prediction:** present=True, span='The term of this Agreement shall commence on the Effective Date and continue for two (2) years unless earlier terminated in accordance with this Agreement.', confidence=1.0
  - token Jaccard vs gold: 0.3636

**Reasoning:** The excerpt explicitly defines the duration of the agreement, stating its commencement and length, which directly addresses the contract term.

### 2. `ex-009` — Arbitration

**Contract:** Commercial Agreement

**Excerpt:**
```
Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration administered in New York, New York.
```

**Gold:** present=True
  - spans: ['resolved by binding arbitration administered in New York, New York']

**Prediction:** present=True, span='Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration administered in New York, New York.', confidence=1.0
  - token Jaccard vs gold: 0.4000

**Reasoning:** The excerpt explicitly states that disputes 'shall be resolved by binding arbitration', directly addressing the Arbitration clause category.

### 3. `ex-010` — Automatic Renewal

**Contract:** Service Subscription Agreement

**Excerpt:**
```
This Agreement will automatically renew for successive one-year terms unless either party gives written notice of non-renewal at least thirty (30) days before the end of the then-current term.
```

**Gold:** present=True
  - spans: ['automatically renew for successive one-year terms unless either party gives written notice of non-renewal']

**Prediction:** present=True, span='This Agreement will automatically renew for successive one-year terms unless either party gives written notice of non-renewal at least thirty (30) days before the end of the then-current term.', confidence=1.0
  - token Jaccard vs gold: 0.5333

**Reasoning:** The excerpt explicitly states that the agreement 'will automatically renew for successive one-year terms,' which directly addresses the concept of automatic renewal.

### 4. `ex-005` — Confidentiality

**Contract:** Mutual Non-Disclosure Agreement

**Excerpt:**
```
Each party shall keep confidential all non-public business, technical, and financial information received from the other party.
```

**Gold:** present=True
  - spans: ['keep confidential all non-public business, technical, and financial information']

**Prediction:** present=True, span='Each party shall keep confidential all non-public business, technical, and financial information received from the other party.', confidence=1.0
  - token Jaccard vs gold: 0.5882

**Reasoning:** The excerpt explicitly states that 'Each party shall keep confidential all non-public business, technical, and financial information,' which directly addresses the concept of confidentiality.

### 5. `ex-011` — Force Majeure

**Contract:** Logistics Services Agreement

**Excerpt:**
```
Neither party shall be liable for delay or failure to perform due to events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action.
```

**Gold:** present=True
  - spans: ['events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action']

**Prediction:** present=True, span='Neither party shall be liable for delay or failure to perform due to events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action.', confidence=1.0
  - token Jaccard vs gold: 0.5926

**Reasoning:** The excerpt explicitly states that neither party is liable for non-performance due to events beyond their reasonable control, which is the core definition of a Force Majeure clause. It also lists common examples of such events.

### 6. `ex-003` — Termination for Convenience

**Contract:** Vendor Services Agreement

**Excerpt:**
```
Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.
```

**Gold:** present=True
  - spans: ['terminate this Agreement for convenience upon sixty (60) days prior written notice']

**Prediction:** present=True, span='Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.', confidence=1.0
  - token Jaccard vs gold: 0.6667

**Reasoning:** The excerpt explicitly states that 'Either party may terminate this Agreement for convenience,' directly matching the clause category.

### 7. `ex-008` — IP Ownership

**Contract:** Independent Contractor Agreement

**Excerpt:**
```
All inventions, works of authorship, and deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client.
```

**Gold:** present=True
  - spans: ['deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client']

**Prediction:** present=True, span='All inventions, works of authorship, and deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client.', confidence=1.0
  - token Jaccard vs gold: 0.6842

**Reasoning:** The excerpt explicitly states that inventions, works of authorship, and deliverables created by the Contractor for the Client shall be owned by the Client, directly addressing intellectual property ownership.

## hallucinated_span (0 total)

_No errors in this bucket._

## parse_fail (0 total)

_No errors in this bucket._
