# Error report — `anthropic`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | _none_ | 0 |
| false_present | _none_ | 0 |
| correct_present_wrong_span | _none_ | 0 |
| hallucinated_span | _none_ | 0 |
| parse_fail | Affiliate License-Licensee | 25 |
| parse_fail | Affiliate License-Licensor | 25 |
| parse_fail | Agreement Date | 25 |
| parse_fail | Anti-Assignment | 25 |
| parse_fail | Audit Rights | 25 |
| parse_fail | Cap On Liability | 25 |

## missed_present (0 total)

_No errors in this bucket._

## false_present (0 total)

_No errors in this bucket._

## correct_present_wrong_span (0 total)

_No errors in this bucket._

## hallucinated_span (0 total)

_No errors in this bucket._

## parse_fail (150 total)

### Worst 10 examples

### 1. `cuad-00000` — Affiliate License-Licensee

**Contract:** OTISWORLDWIDECORP_04_03_2020-EX-10.4-INTELLECTUAL PROPERTY AGREEMENT by and among UNITED TECHNOLOGIES CORPORATION, OTIS WORLDWIDE CORPORATION and CARRIER ~1

**Excerpt:**
```
Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee Party and the other members of the Licensee Group, subject to the field restriction of Section 3.1.2, a royalty-free, nonexclusive, perpetual, irrevocable, fully paid-up, worldwide right and license, with the right to sublicense as provided in Section 3.1.3, to Exploit Intellectual Property Rights that are owned by the ...
```

**Gold:** present=True
  - spans: ['Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee Party and the other members of the Licensee Group, subject to the field restriction of Section 3.1.2, a royalty-free, nonexclusive, perpetual, irrevocable, fully paid-up, worldwide right and license, with the right to sublicense as provided in Section 3.1.3, to Exploit Intellectual Property Rights that are owned by the Licensor Party or another member of the Licensor Group immediately following the assignments pursuant to Article II and meet one or more of the following descriptions with respect to the relevant Licensee Party: (a) the Intellectual Property Rights are rights under Licensed Patents or other Intellectual Property Rights that, in each case, as of the Effective Time, are either (A) used in connection with, or necessary for the ongoing conduct of, the current business of the Licensee Party or another member of the Licensee Group, or (B) Contemplated to be Used in the business of the Licensee Party, or another member of the Licensee Group, in the Licensee Group Field; provided, however, that the license granted in this Section 3.1.1(a) does not apply to the Intellectual Property Rights received under or otherwise governed by an Excluded Agreement; and/or (b) the Intellectual Property Rights are embodied in an invention, or proposed invention, that is both (i) described in a Patent or Invention Disclosure held by the Licensor Party or another member of the Licensor Group and (ii) conceived by at least one inventor who, at the time of conception, was employed by a member of the Licensee Group, a non-inclusive list of which inventions and proposed inventions are provided in Schedule 3.1.1(b), provided, however, that the license granted in this Section 3.1.1(b) does not apply to an invention conceived under or otherwise governed by an Excluded Agreement; and/or (c) the Intellectual Property Rights are subject to an assignment to the Licensor Party in Section 2.1.1(b) concerning Performer Foreground-Delivered IPR conceived or created in the course of services concerning which the Licensor Party or another member of the Licensor Group was the Requester and the Licensee Party or another member of the Licensee Group was the Performer; and/or', '4.2.3 UTC, on behalf of itself and the other members of the UTC Group, hereby grants to Otis, Carrier and the other members of the Otis Group and the Carrier Group a limited, non-exclusive, non-transferable, personal and nonsublicensable right to continue temporarily to use, following the Effective Time, any United Technologies Trademark it is using immediately prior to the Effective Time, solely to the extent of such pre- Separation use and in accordance with product quality standards and programs in place at the respective member of the Otis Group or the Carrier Group immediately prior to the Effective Time, and strictly in accordance with this Section 4.2.3; provided that Otis and Carrier shall, and shall cause each of its respective Affiliates (including, after the Effective Time, the members of, respectively, the Otis Group and the Carrier Group) (a) not to hold itself out as having any affiliation with UTC or any member of the UTC Group (except to the extent a third party may infer such affiliation merely due to the limited use of the United Technologies Trademarks as contemplated herein), and (b) to use diligent efforts to eliminate use of the United Technologies Trademarks.', '(d) the Intellectual Property Rights are Performer Background IPR or Patent rights of the Licensor Party or another member of the Licensor Group and is necessary for the Licensee Party or another member of the Licensee Party to Exploit the Performer Foreground-Delivered IPR in the Licensee Group Field, provided, however, that the license granted in this Section 3.1.1(d) applies only to the extent necessary for the Licensee Party or another member of the Licensee Group to Exploit the Performer Foreground-Delivered IPR in the Licensee Group Field. (collectively, "Licensed Intellectual Property Rights").']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 2. `cuad-00001` — Affiliate License-Licensee

**Contract:** BABCOCK_WILCOXENTERPRISES,INC_08_04_2015-EX-10.17-INTELLECTUAL PROPERTY AGREEMENT between THE BABCOCK _ WILCOX COMPANY and BABCOCK _ WILCOX ENTERPRISES, INC.

**Excerpt:**
```
Accordingly, (i) with respect to RemainCo's right and interest in and to the Shared Library Materials, RemainCo, for itself and as representative of all other members of the RemainCo Group, hereby grants to SpinCo (x) a perpetual (subject to Section 4.4), irrevocable, exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Shared Library Materials, including all Know-How and Copyrights embodied therein, for any purpose in the SpinCo Core Field and (y) a perpetual (subject to Section 4.4), irrevocable, non-exclu...
```

**Gold:** present=True
  - spans: ['SpinCo, for itself and as representative of all other members of the SpinCo Group, hereby grants to RemainCo (x) a perpetual, irrevocable, exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the SpinCo Know- How currently or previously used in connection with the RemainCo Business or otherwise in the possession of RemainCo or any member of the RemainCo Group as of Distribution Date (the "Licensed SpinCo Know-How"), for the continued operation of the RemainCo Business and any future extensions of the RemainCo Business in the RemainCo Core Field and (y) a perpetual, irrevocable, non-exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Licensed SpinCo Know-How for the continued operation of the RemainCo Business and any future extensions of the RemainCo Business in any field other than the RemainCo Core Field or the SpinCo Core Field; provided, however, the foregoing licenses shall not extend to (i) SpinCo Know-How', 'RemainCo, for itself and as representative of all other members of the RemainCo Group, hereby grants to SpinCo (x) a perpetual, irrevocable, exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the RemainCo Know-How currently or previously used in connection with the SpinCo Business or otherwise in the possession of SpinCo or any member of the SpinCo Group as of the Distribution Date (the "Licensed RemainCo Know-How"), for the continued operation of the SpinCo Business and any future extensions of the SpinCo Business in the SpinCo Core Field and (y) a perpetual, irrevocable, non-exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Licensed RemainCo Know-How for the continued operation of the SpinCo Business and any future extensions of the SpinCo Business in any field other than the RemainCo Core Field or the SpinCo Core Field; provided, however, the foregoing licenses shall not extend to (i) RemainCo Know-How licensed by RemainCo or any other member of the RemainCo Group if and to the extent the licensing of same to SpinCo would constitute a breach of an agreement with any Third Party executed prior to the Effective Date or result in any expense to RemainCo or any member of the RemainCo Group for payments to such Third Party or (ii) any intellectual property not owned by one or more members of the RemainCo Group, or as to which no member of the RemainCo Group has the right to grant sublicenses, as of the Effective Date.', 'SpinCo may sublicense the Licensed RemainCo Intellectual Property to Affiliates of SpinCo, even if they become Affiliates after the Distribution Date, solely within the scope of its licenses in Article 5, provided that such sublicense shall only be effective for such time as such entity remains an Affiliate of SpinCo', 'licensed by SpinCo or any other member of the SpinCo Group if and to the extent the licensing of same to RemainCo would constitute a breach of an agreement with any Third Party executed prior to the Effective Date or result in any expense to SpinCo or any member of the SpinCo Group for payments to such Third Party or (ii) any intellectual property not owned by one or more members of the SpinCo Group, or as to which no member of the SpinCo Group has the right to grant sublicenses, as of the Effective Date.', "Accordingly, (i) with respect to RemainCo's right and interest in and to the Shared Library Materials, RemainCo, for itself and as representative of all other members of the RemainCo Group, hereby grants to SpinCo (x) a perpetual (subject to Section 4.4), irrevocable, exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Shared Library Materials, including all Know-How and Copyrights embodied therein, for any purpose in the SpinCo Core Field and (y) a perpetual (subject to Section 4.4), irrevocable, non-exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Shared Library Materials, including all Know-How and Copyrights embodied therein, for any purpose in any field other than the RemainCo Core Field or the SpinCo Core Field and (ii) with respect to SpinCo's right and interest in and to the Shared Library Materials, SpinCo, for itself and as representative of all other members of the SpinCo Group, hereby grants to RemainCo (x) a perpetual (subject to Section 4.4), irrevocable, exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Shared Library Materials, including all Know-How and Copyrights embodied therein, for any purpose in the RemainCo Core Field and (y) a perpetual (subject to Section 4.4), irrevocable, non- exclusive, royalty-free, worldwide right and license with the right to grant sublicenses (solely as set forth in Section 5.6) to use the Shared Library Materials, including all Know-How and Copyrights embodied therein, for any purpose in any field other than the SpinCo Core Field or the RemainCo Core Field.", 'RemainCo may sublicense the Licensed SpinCo Intellectual Property to Affiliates of RemainCo, even if they become Affiliates after the Distribution Date, solely within the scope of its licenses in Article 5, provided that such sublicense shall only be effective for such time as such entity remains an Affiliate of RemainCo']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 3. `cuad-00002` — Affiliate License-Licensee

**Contract:** ARMSTRONGFLOORING,INC_01_07_2019-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT

**Excerpt:**
```
age or reputation of any of the Seller Licensed Trademarks or (B) Seller's right, title or interest in and to, any of the Arizona Licensed Trademarks. (b) The Company shall not tarnish or bring into disrepute the reputation of or goodwill associated with the Seller Licensed Trademarks or Arizona. (c) The Company shall use the Seller Licensed Trademarks at all times in compliance with all applicable Laws. (d) The Company shall include trademark and other notices in connection with the use of the Seller Licensed Trademarks as reasonably requested by Arizona from time to time. 6





(e) The C...
```

**Gold:** present=True
  - spans: ['Arizona may sublicense the licenses granted herein to its Affiliates and Third Parties in the ordinary course of business in support of its and its Affiliates\' business, but not for the independent use of Third Parties, and the Company may sublicense the licenses granted herein to Third Parties, its Subsidiaries, AWP, controlled Affiliates, or any holding company that is a direct or indirect parent of the Company in the ordinary course of business in support of its and its Subsidiaries\' or controlled Affiliates\' business, but not for the independent use of Third Parties (each such Affiliate, Third Party, AWP or Subsidiary, a "Sublicensee").']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 4. `cuad-00003` — Affiliate License-Licensee

**Contract:** ReynoldsConsumerProductsInc_20200121_S-1A_EX-10.22_11948918_EX-10.22_Service Agreement

**Excerpt:**
```
ure Agreements. To the extent that any third-party proprietor of information or software to be disclosed or made available to a Recipient in connection with performance of the Services requires a specific form of non-disclosure agreement as a condition of such third party's consent to use the same for the benefit of Recipient or to permit the Recipient access to such information or software, each Party shall, or shall cause its relevant Affiliate to, as a condition to the receipt of such portion of the Services, execute (and shall cause its Personnel to execute, if reasonably required) any ...
```

**Gold:** present=True
  - spans: ['Each Party grants, and shall cause its Affiliates to grant, to the other Party and its Affiliates, a royalty-free, non-exclusive, non- transferable, worldwide license, during the Term, to use the intellectual property owned by such Party or its Affiliates (but excluding any trademarks) only to the extent necessary for the other Party and its Affiliates to provide or receive the Services, as applicable.']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 5. `cuad-00004` — Affiliate License-Licensee

**Contract:** ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
DIALOG may sublicense the foregoing license rights to any of its Affiliates. DIALOG will be responsible for the observance and performance by all such Affiliates of all of DIALOG's obligations pursuant to this Agreement. DIALOG may sublicense the foregoing license rights to Manufacturing Subcontractors solely to the extent necessary and appropriate for them to manufacture, assemble, test and provide support for the Products. DIALOG may not sublicense the foregoing license rights to any other third party without ENERGOUS' prior written consent.   * Confidential Treatment Requested

  Page 6
...
```

**Gold:** present=True
  - spans: ['DIALOG may sublicense the foregoing license rights to any of its Affiliates.', "IALOG's license to possess and use the Deposit Materials does not include any right to disclose, market, sublicense or distribute the Deposit Materials to any third party other than its Affiliates and Manufacturing Subcontractors."]

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 6. `cuad-00005` — Affiliate License-Licensee

**Contract:** ConformisInc_20191101_10-Q_EX-10.6_11861402_EX-10.6_Development Agreement

**Excerpt:**
```
riteria, then Stryker will provide Conformis with a written notice of rejection within the Acceptance Notification Period   describing the defect in view of the relevant Acceptance Criteria and including sufficient detail with respect to such Stryker testing   and testing results as Conformis reasonably requests ("Failure Notice"). Conformis shall have [**] (or such longer period of time   as may be agreed between the parties in good faith should the scope and complexity of the applicable Deliverable warrant some   longer period of time) ("Redelivery Period") following the date it receives ...
```

**Gold:** present=True
  - spans: ['Except as specifically provided in the Distribution Agreement, Conformis shall be prohibited from   developing or assisting another in developing, or causing another to develop, Patient-Specific Instrumentation for Off-The-Shelf   Knee Implants for any Third Party in the field of orthopedics until January 1, 2032 (or earlier, to the extent set forth in Section   2.3.3.4 or Section 2.3.5 of the Distribution Agreement), with the exception that Conformis (including any entity involved in a   Change of Control of Conformis, any such entity an "Acquirer"), may develop Patient-Specific Instrumentation for any Off-The-   Shelf Implants of Conformis, an Acquirer or any of their Affiliates.']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 7. `cuad-00006` — Affiliate License-Licensee

**Contract:** CoherusBiosciencesInc_20200227_10-K_EX-10.29_12021376_EX-10.29_Development Agreement

**Excerpt:**
```
Licensee shall be entitled to grant sublicenses under its license pursuant to Section 2.1 to Affiliates only, provided that any sublicense granted by Licensee under this Section 2.1.2 shall be made through a written agreement in the English language and shall be consistent with the terms of this Agreement. Licensee shall promptly inform Bioeq in writing of any sublicenses granted hereunder and, upon Bioeq's request, shall make a copy of the relevant sublicense agreement available to Bioeq. Licensee may redact the [***] terms and conditions of such sublicense agreement in such copy. Licensee...
```

**Gold:** present=True
  - spans: ['Licensee shall be entitled to grant sublicenses under its license pursuant to Section 2.1 to Affiliates only, provided that any sublicense granted by Licensee under this Section 2.1.2 shall be made through a written agreement in the English language and shall be consistent with the terms of this Agreement.', "For those countries where a specific license is required for a joint owner of a Joint Invention or Joint Improvement to practice such Joint Invention or Joint Improvement, in such country, each Party hereby grants to the other Party a perpetual, irrevocable, non-exclusive, worldwide, royalty-free, fully paid-up license, transferable and sublicensable, under such Party's right, title and interest in and to such Joint Invention or Joint Improvement to freely exploit such Joint Invention or Joint Improvement in such country, subject to the terms and conditions of this Agreement and the licenses granted hereunder."]

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 8. `cuad-00007` — Affiliate License-Licensee

**Contract:** BELLICUMPHARMACEUTICALS,INC_05_07_2019-EX-10.1-Supply Agreement

**Excerpt:**
```
The supply of the Miltenyi Products hereunder conveys to Bellicum the limited, non-exclusive, non-transferable (except as expressly provided herein, including as set forth in Article 17) right to use, and to permit its Subcontractors and Licensees to use the Miltenyi Products solely for Ex Vivo Cell Processing in the manufacture of Bellicum Products for use in the Field in the Territory (including for research, pre-clinical, clinical, regulatory and commercial purposes), in accordance with applicable Regulatory Authority requirements and approvals (including (to the extent applicable) any r...
```

**Gold:** present=True
  - spans: ["Subject to the terms of the Quality Agreement, if applicable, Miltenyi may, at its sole discretion, upon reasonable prior written notice to Bellicum, elect to have the Miltenyi Products, or any one of them or any component thereof, manufactured by an Affiliate of Miltenyi, and further may subcontract the manufacturing of Miltenyi Product or any component thereof, to a Subcontractor; provided that (i) Miltenyi shall reasonably take into account Bellicum's written concerns regarding proposed Affiliate(s) or Subcontractor(s); and (ii) Miltenyi shall be solely and fully responsible for the performance of all delegated and subcontracted activities by its Affiliates and Subcontractor(s), including compliance with the terms of this Agreement and the Quality Agreement (as applicable), and in no event shall any such delegation or subcontract release Miltenyi from any of its obligations under this Agreement. Miltenyi's Subcontractors and Affiliates for the manufacture and/or supply of Miltenyi Products will be listed in the Quality Agreement", "Bellicum shall have the right to transfer Miltenyi Product(s) purchased hereunder, or to request from Miltenyi, by notice in writing, that Miltenyi Deliver any Miltenyi Product(s) purchased hereunder to an Affiliate of Bellicum or a Subcontractor or Licensee of Bellicum Product designated by Bellicum, solely for the purpose of the Permitted Use, subject to the payment to Miltenyi of all additional expenses (if any) incurred by Miltenyi in connection with such provision and transfer of Miltenyi Product(s) to Bellicum's designee; and provided that in each case: (i) each Subcontractor or Licensee of Bellicum to whom Miltenyi Products are transferred shall be bound in writing by limitations and obligations that are consistent with the corresponding limitations and obligations imposed on Bellicum", 'The supply of the Miltenyi Products hereunder conveys to Bellicum the limited, non-exclusive, non-transferable (except as expressly provided herein, including as set forth in Article 17) right to use, and to permit its Subcontractors and Licensees to use the Miltenyi Products solely for Ex Vivo Cell Processing in the manufacture of Bellicum Products for use in the Field in the Territory (including for research, pre-clinical, clinical, regulatory and commercial purposes), in accordance with applicable Regulatory Authority requirements and approvals (including (to the extent applicable) any relevant clinical trial protocol, IND, and/or IRB approval pertaining to such Bellicum Products), in each case consistent with the terms and conditions of this Agreement and in accordance with Applicable Laws (the "Permitted Use"). Bellicum\'s Permitted Use of the Miltenyi Products shall be limited to the Designated Countries, subject to Section 2.3.', 'hereunder and under the Quality Agreement, as applicable; and (ii) notwithstanding the transfer of any Miltenyi Product purchased hereunder, Bellicum will nevertheless continue to remain fully and primarily responsible and liable to Miltenyi for payment of the Product Price and for the use of the Miltenyi Product by any Subcontractor and Licensee to whom a Miltenyi Product is transferred.']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 9. `cuad-00008` — Affiliate License-Licensee

**Contract:** XENCORINC_10_25_2013-EX-10.24-COLLABORATION AGREEMENT (3)

**Excerpt:**
```
ness Partner or its affiliate to manufacture and supply commercial Product); provided that the supply price for Product is no more than [...***...] percent ([...***...]%) of the commercial supply price of Product last proposed by BII during the negotiations between the Parties (or BII and the Business Partner). If the supply price for Product proposed by a third party (which may include a Business Partner or its affiliate) is more than [...***...] percent ([...***...]%) of the commercial supply price of Product last proposed by BII during the negotiations between the Parties (or BII and the...
```

**Gold:** present=True
  - spans: ['In the event that XENCOR pays the Technology Access Fee set forth above, XENCOR shall have the right to use or have used (e.g. by a Business Partner) the Process worldwide for the manufacture of Product in accordance with the terms and conditions of this Agreement, without entering into a contract manufacturing agreement with BII']

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY

### 10. `cuad-00009` — Affiliate License-Licensee

**Contract:** AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_Maintenance Agreement

**Excerpt:**
```
upon successful transmission to the recipient's email account, if such Notice is sent in time to allow it to be accessible by the Addressee before the time allowed for giving such Notice expires, and a confirmation copy is sent by one of the other methods.

(c) The addresses and telephone numbers to which Notices may be given to the Addressees of either Party may be changed by written Notice given by such Party to the other pursuant to this Section.

3.27 Offshore Work Prohibited. None of the Services under this Agreement shall be performed or provided and no Information related to this Agr...
```

**Gold:** present=True
  - spans: ["Vendor hereby grants and promises to grant and have granted to AT&T and its Affiliates a royalty-free, nonexclusive, sublicensable, assignable, transferable, irrevocable, perpetual, world- wide license in and to any applicable Intellectual Property Rights of Vendor to use, copy, modify, distribute, display, perform, import, make, sell, offer to sell, and exploit (and have others do any of the foregoing on or for AT&T's or any of its customers' behalf or benefit) any Intellectual Property Rights of Vendor or any third party that are not included in Material or Paid-For Development but necessary to operate the Cell Sites or receive the full benefit of the Work."]

**Prediction:** present=None, span=None, confidence=None

**API error:** ValueError: Missing API key environment variable: ANTHROPIC_API_KEY
