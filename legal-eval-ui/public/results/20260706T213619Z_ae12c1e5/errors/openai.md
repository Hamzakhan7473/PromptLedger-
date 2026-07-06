# Error report — `openai`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | _none_ | 0 |
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

## false_present (1 total)

### Worst 1 examples

### 1. `ex-016` — Payment Terms

**Contract:** Cloud Services Agreement

**Excerpt:**
```
Except for obligations to pay fees, neither party shall be responsible for failure to perform due to causes beyond its reasonable control.
```

**Gold:** present=False

**Prediction:** present=True, span='Except for obligations to pay fees, neither party shall be responsible for failure to perform due to causes beyond its reasonable control.', confidence=0.86

**Reasoning:** The excerpt expressly mentions an obligation to pay fees, which is a payment-related term. However, it does not provide detailed payment mechanics such as timing, invoicing, or amounts.

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

**Prediction:** present=True, span='The term of this Agreement shall commence on the Effective Date and continue for two (2) years unless earlier terminated in accordance with this Agreement.', confidence=0.99
  - token Jaccard vs gold: 0.3636

**Reasoning:** The excerpt expressly states the agreement's duration and start date, which directly addresses the contract term. It also includes an early termination qualifier.

### 2. `ex-009` — Arbitration

**Contract:** Commercial Agreement

**Excerpt:**
```
Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration administered in New York, New York.
```

**Gold:** present=True
  - spans: ['resolved by binding arbitration administered in New York, New York']

**Prediction:** present=True, span='Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration administered in New York, New York.', confidence=0.99
  - token Jaccard vs gold: 0.4000

**Reasoning:** The excerpt expressly requires disputes to be resolved by binding arbitration, which directly addresses the arbitration clause category. The language is clear and substantive.

### 3. `ex-010` — Automatic Renewal

**Contract:** Service Subscription Agreement

**Excerpt:**
```
This Agreement will automatically renew for successive one-year terms unless either party gives written notice of non-renewal at least thirty (30) days before the end of the then-current term.
```

**Gold:** present=True
  - spans: ['automatically renew for successive one-year terms unless either party gives written notice of non-renewal']

**Prediction:** present=True, span='This Agreement will automatically renew for successive one-year terms unless either party gives written notice of non-renewal at least thirty (30) days before the end of the then-current term.', confidence=0.99
  - token Jaccard vs gold: 0.5333

**Reasoning:** The excerpt expressly states that the agreement will automatically renew for successive one-year terms. It also specifies the non-renewal notice requirement, which is directly related to automatic renewal.

### 4. `ex-005` — Confidentiality

**Contract:** Mutual Non-Disclosure Agreement

**Excerpt:**
```
Each party shall keep confidential all non-public business, technical, and financial information received from the other party.
```

**Gold:** present=True
  - spans: ['keep confidential all non-public business, technical, and financial information']

**Prediction:** present=True, span='Each party shall keep confidential all non-public business, technical, and financial information received from the other party.', confidence=0.99
  - token Jaccard vs gold: 0.5882

**Reasoning:** The excerpt expressly requires each party to keep non-public information confidential, which is a direct confidentiality obligation. This substantively addresses the confidentiality clause category.

### 5. `ex-011` — Force Majeure

**Contract:** Logistics Services Agreement

**Excerpt:**
```
Neither party shall be liable for delay or failure to perform due to events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action.
```

**Gold:** present=True
  - spans: ['events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action']

**Prediction:** present=True, span='Neither party shall be liable for delay or failure to perform due to events beyond its reasonable control, including acts of God, war, pandemic, labor disputes, or governmental action.', confidence=0.99
  - token Jaccard vs gold: 0.5926

**Reasoning:** This language expressly excuses performance delays or failures caused by events beyond a party's reasonable control, which is the core concept of a force majeure clause. The listed examples are classic force majeure events.

### 6. `ex-003` — Termination for Convenience

**Contract:** Vendor Services Agreement

**Excerpt:**
```
Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.
```

**Gold:** present=True
  - spans: ['terminate this Agreement for convenience upon sixty (60) days prior written notice']

**Prediction:** present=True, span='Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.', confidence=0.99
  - token Jaccard vs gold: 0.6667

**Reasoning:** The excerpt expressly states that either party may terminate the agreement "for convenience" with 60 days' prior written notice, which directly matches the clause category.

### 7. `ex-008` — IP Ownership

**Contract:** Independent Contractor Agreement

**Excerpt:**
```
All inventions, works of authorship, and deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client.
```

**Gold:** present=True
  - spans: ['deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client']

**Prediction:** present=True, span='All inventions, works of authorship, and deliverables created by Contractor specifically for Client under this Agreement shall be owned by Client.', confidence=0.99
  - token Jaccard vs gold: 0.6842

**Reasoning:** The excerpt expressly allocates ownership of inventions, works of authorship, and deliverables to the Client. This is direct IP ownership language.

## hallucinated_span (0 total)

_No errors in this bucket._

## parse_fail (0 total)

_No errors in this bucket._
