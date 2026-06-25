# Error report — `openai`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | Cap On Liability | 1 |
| false_present | Affiliate License-Licensee | 1 |
| false_present | Affiliate License-Licensor | 2 |
| false_present | Agreement Date | 11 |
| false_present | Anti-Assignment | 1 |
| false_present | Cap On Liability | 2 |
| correct_present_wrong_span | Affiliate License-Licensee | 4 |
| correct_present_wrong_span | Affiliate License-Licensor | 6 |
| correct_present_wrong_span | Agreement Date | 9 |
| correct_present_wrong_span | Anti-Assignment | 3 |
| correct_present_wrong_span | Audit Rights | 5 |
| correct_present_wrong_span | Cap On Liability | 3 |
| hallucinated_span | Affiliate License-Licensee | 1 |
| hallucinated_span | Affiliate License-Licensor | 1 |
| hallucinated_span | Audit Rights | 3 |
| hallucinated_span | Cap On Liability | 2 |
| parse_fail | _none_ | 0 |

## missed_present (1 total)

### Worst 1 examples

### 1. `cuad-00133` — Cap On Liability

**Contract:** REGANHOLDINGCORP_03_31_2008-EX-10-LICENSE AND HOSTING AGREEMENT

**Excerpt:**
```
nt Indemnification

LMG represents and warrants that (i) no LMG Tools, CSC Software, Other Third Party Software or Documentation provided under this Agreement is the subject of any claim, dispute, demand or litigation ("Claim"), and (ii) LMG has all right, title, ownership interest, and/or  rights necessary to provide such software and Documentation to TAG and that the License, the LMG Tools and Documentation and their license and Use hereunder do not and shall not directly or indirectly violate or infringe upon any copyright, patent, trade secret, or other proprietary or intellectual prope...
```

**Gold:** present=True
  - spans: ["LMG's indemnification obligations under this Section 5.2 will expire twelve (12) months after the Conversion Date.", 'Neither party shall be liable to the other pursuant to this Agreement for any amounts representing loss of profit, loss of business or indirect, consequential, exemplary, or punitive damages of the other party.', "TAG's indemnification obligations under this Section 5.3 will expire twelve (12) months after the Conversion Date."]

**Prediction:** present=False, span=None, confidence=0.93

**Reasoning:** The excerpt includes a limitation of liability clause excluding certain damages, but it does not set a monetary cap or other ceiling on liability. The language expressly preserves indemnification obligations and addresses exclusions rather than a cap.

## false_present (17 total)

### Worst 10 examples

### 1. `cuad-00063` — Agreement Date

**Contract:** PHLVARIABLEINSURANCECOCT_08_17_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
STRATEGIC ALLIANCE AGREEMENT

This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the  "Effective Date"), by and among PHL VARIABLE INSURANCE COMPANY ("PHLVIC"), PHOENIX LIFE INSURANCE COMPANY, ("PLIC"  and, together with PHLVIC, "PHL Variable"), PHOENIX EQUITY PLANNING CORPORATION ("PEPCO" and, together with PHLVIC and PLIC,  the "PHL Parties"), and INVESTORS CAPITAL CORPORATION ("ICC"). Except as otherwise defined, capitalized terms used herein shall have  the meanings given to them in Section 1 Definitions, be...
```

**Gold:** present=False

**Prediction:** present=True, span='This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the  "Effective Date")', confidence=0.99

**Reasoning:** The introductory paragraph expressly states when the agreement is entered into and defines that date as the Effective Date. This is direct agreement-date language.

### 2. `cuad-00065` — Agreement Date

**Contract:** IOVANCEBIOTHERAPEUTICS,INC_08_03_2017-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
Exhibit 10.1   Text Marked By [* * *] Has Been Omitted Pursuant To A Request For Confidential Treatment And Was Filed Separately With The Securities And Exchange Commission.   STRATEGIC ALLIANCE AGREEMENT Effective Date: April 17, 2017   THIS STRATEGIC ALLIANCE AGREEMENT (this "Agreement"), is entered into by and between Lion Biotechnologies, Inc., with a place of business located at 999 Skyway Road, Suite 150, San Carlos, CA 94070 ("LBIO"), and The University of Texas M. D. Anderson Cancer Center, with a place of business located at 1515 Holcombe Blvd., Houston, TX 77030 ("MD Anderson"), a...
```

**Gold:** present=False

**Prediction:** present=True, span='Effective Date: April 17, 2017', confidence=0.99

**Reasoning:** The excerpt expressly states an effective date, which serves as the agreement date language. It appears prominently at the beginning of the agreement.

### 3. `cuad-00071` — Agreement Date

**Contract:** PfHospitalityGroupInc_20150923_10-12G_EX-10.1_9266710_EX-10.1_Franchise Agreement1

**Excerpt:**
```
FORM OF FRANCHISE AGREEMENT Location of the Premises: Agreement Date Franchisee Business Address

Type of Legal Entity (if applicable) State in which entity organized (if applicable) Shareholder / Partner / Member Name Ownership Percentage % (the "Operating Principal") % % % %

Source: PF HOSPITALITY GROUP INC., 10-12G, 9/23/2015





TABLE OF CONTENTS SECTION PAGE 1. RIGHTS GRANTED 2 2. TERM; SUCCESSOR FRANCHISE AGREEMENTS 4 3. FEES 4 4. OPENING DEADLINE 6 5. TRAINING 10 6. OPERATIONS 11 7. PROPRIETARY MARKS 18 8. BUSINESS RECORDS AND REPORTING 19 9. MARKETING FUND AND ADVERTISING 21 10. T...
```

**Gold:** present=False

**Prediction:** present=True, span='This Franchise Agreement (the "Agreement") is entered into as of the Agreement Date shown on the cover page', confidence=0.99

**Reasoning:** The excerpt explicitly references the Agreement Date on the cover page and states the agreement is entered into as of that date. This is direct language addressing the clause category.

### 4. `cuad-00073` — Agreement Date

**Contract:** SLOVAKWIRELESSFINANCECOBV_03_28_2001-EX-4.(B)(II).3-Maintenance and support contract for SICAP(R) modules

**Excerpt:**
```
Exhibit 4(b)(ii).3

                                                                    [LOGO] sicap

                        Maintenance and support contract                               for SICAP(R) modules                                 PPB, VCA and OTA

                              dated 10 October 2000

    This contract replaces in full the Annex 7 "Maintenance and Support for         SICAP(R) modules PPB, VCA and OTA and Sun Hardware" which was an            integral part of the original Swisscom PURCHASE & LICENSE                    CONTRACT, made effective on 06 April 1998.

con...
```

**Gold:** present=False

**Prediction:** present=True, span='dated 10 October 2000', confidence=0.99

**Reasoning:** The excerpt explicitly states the contract is "dated 10 October 2000," which directly identifies the agreement date. This is a clear and substantive agreement-date reference.

### 5. `cuad-00062` — Agreement Date

**Contract:** LohaCompanyltd_20191209_F-1_EX-10.16_11917878_EX-10.16_Supply Agreement

**Excerpt:**
```
Exhibit 10.16 SUPPLY CONTRACT Contract No: Date: The buyer/End-User: Shenzhen LOHAS Supply Chain Management Co., Ltd. ADD: Tel No. : Fax No. : The seller: ADD: The Contract is concluded and signed by the Buyer and Seller on , in Hong Kong. 1. General provisions 1.1 This is a framework agreement, the terms and conditions are applied to all purchase orders which signed by this agreement (hereinafter referred to as the "order"). 1.2 If the provisions of the agreement are inconsistent with the order, the order shall prevail. Not stated in order content will be subject to the provisions of agree...
```

**Gold:** present=False

**Prediction:** present=True, span='The Contract is concluded and signed by the Buyer and Seller on , in Hong Kong.', confidence=0.98

**Reasoning:** The excerpt includes an explicit contract execution date field, even though the actual date is left blank. This is substantively language related to the agreement date.

### 6. `cuad-00066` — Agreement Date

**Contract:** ElPolloLocoHoldingsInc_20200306_10-K_EX-10.16_12041700_EX-10.16_Development Agreement

**Excerpt:**
```
Exhibit 10.16

EL POLLO LOCO® FRANCHISE DEVELOPMENT AGREEMENT

Dated: ____________________

Territory: Developer:

(Disclosure Document Control No. 032619)

TABLE OF CONTENTS 1.DEVELOPMENT RIGHTS IN TERRITORY. 4 2.LIMITATION ON DEVELOPMENT RIGHTS. 5 3.DEVELOPMENT FEE. 9 4.TERM OF DEVELOPMENT AGREEMENT. 10 5.TERRITORY CONFLICTS. 10 6.PROPRIETARY RIGHTS OF EL POLLO LOCO. 11 7.INSURANCE AND INDEMNIFICATION. 11 8.TRANSFER OF RIGHTS. 13 9.ACKNOWLEDGMENT OF SELECTED TERMS AND PROVISIONS OF THE FRANCHISE AGREEMENT. 14 10.TERMINATION BY DEVELOPER; EXPIRATION DATE. 14 11.EVENTS OF DEFAULT. 15 12.EFF...
```

**Gold:** present=False

**Prediction:** present=True, span='dated for identification purposes only as of _____________________, is made and entered into by and between', confidence=0.98

**Reasoning:** The excerpt expressly includes the agreement's date placeholder in the opening paragraph, which is direct agreement-date language. It also shows a separate 'Dated: ____________________' line near the title, reinforcing that the contract addresses the date of the agreement.

### 7. `cuad-00069` — Agreement Date

**Contract:** WatchitMediaInc_20061201_8-K_EX-10.1_4148672_EX-10.1_Content License Agreement

**Excerpt:**
```
Exhibit 10.1



Oceanic Time Warner Cable and Watchit Media Content and License Agreement

Effective Dates: September 1, 2006, August 31, 2007

Watchit agrees to provide Oceanic Time Warner Cable the following content:

- Watchit Gaming Guides - Lunchtime with Ira segments every week

Watchit will provide the content on BetaSp format and reserves the right to modify the content to reflect sponsorship by an advertiser and advertisers.

Oceanic Time Warner Cable agrees to not edit or modify the above content.

Oceanic Time Warner Cable will use the content solely on channel 777, the Las Vegas...
```

**Gold:** present=False

**Prediction:** present=True, span='Effective Dates: September 1, 2006, August 31, 2007', confidence=0.98

**Reasoning:** The excerpt explicitly states effective dates for the agreement, which is direct agreement-date language. It also includes signature lines with date placeholders, reinforcing that date terms are present.

### 8. `cuad-00070` — Agreement Date

**Contract:** FOUNDATIONMEDICINE,INC_02_02_2015-EX-10.2-Collaboration Agreement

**Excerpt:**
```
Exhibit 10.2

EXECUTION COPY

***Text Omitted and Filed Separately with the Securities and Exchange Commission Confidential Treatment Requested Under 17 C.F.R. Sections 200.80(b)(4) and 240.24b-2

Collaboration Agreement

This Agreement is entered into with effect as of the Effective Date (as defined below)

by and between

F. Hoffmann-La Roche Ltd

with an office and place of business at Grenzacherstrasse 124, 4070 Basel, Switzerland ("Roche Basel")

and

Hoffmann-La Roche Inc.

with an office and place of business at 150 Clove Road, Suite 8, Little Falls, New Jersey 07424, U.S.A. ("Roche ...
```

**Gold:** present=False

**Prediction:** present=True, span='This Agreement is entered into with effect as of the Effective Date (as defined below)', confidence=0.98

**Reasoning:** The excerpt expressly references the agreement's effective date, which is the operative agreement date language. Although the exact calendar date is not shown in the excerpt, the clause category is substantively addressed by this statement.

### 9. `cuad-00072` — Agreement Date

**Contract:** GOOSEHEADINSURANCE,INC_04_02_2018-EX-10.6-Franchise Agreement

**Excerpt:**
```
Exhibit 10.6

Goosehead Insurance Agency, LLC Franchise Agreement

Exhibit A Declarations Page 1 1.2 The "Approved Location" under this Agreement will be: . 2 4.1 You elect to pay the Initial Franchise Fee in one of the following ways: (check only one): ☐ In its entirety at the time you enter into this Agreement, in which case the amount of the Initial Franchise Fee shall be: ($ ). ☐ You shall pay a portion of the Initial Franchise Fee at the time you enter into this Agreement in the amount of ($ ), and shall pay the remaining portion of ($ ), plus interest, according to the terms of the 60...
```

**Gold:** present=False

**Prediction:** present=True, span='THIS FRANCHISE AGREEMENT (the "Agreement") is made and entered into as of the "Effective Date" that we have indicated on the signature page of this Agreement', confidence=0.98

**Reasoning:** The excerpt expressly states that the agreement is made and entered into as of the "Effective Date" on the signature page, which is language identifying the agreement date. It also references a "Commencement Date," but the effective date clause is the clearest agreement-date provision.

### 10. `cuad-00074` — Agreement Date

**Contract:** ChinaRealEstateInformationCorp_20090929_F-1_EX-10.32_4771615_EX-10.32_Content License Agreement

**Excerpt:**
```
Exhibit 10.33

EXECUTION VERSION CONFIDENTIAL

DOMAIN NAME AND CONTENT LICENSE AGREEMENT

This Domain Name and Content License Agreement (the "Agreement") is made and entered into, by and between Beijing SINA Internet  Information Service Co., Ltd. ( ), a limited liability company organized under the laws of the People's Republic  of China (hereinafter "Licensor") and Beijing Yisheng Leju Information Services Co., Ltd., a limited liability company organized under the laws of  the People's Republic of China ("Licensee" and together with Licensor, the "Parties" and each a "Party") and is made...
```

**Gold:** present=False

**Prediction:** present=True, span='This Domain Name and Content License Agreement (the "Agreement") is made and entered into, by and between Beijing SINA Internet  Information Service Co., Ltd. ( ), a limited liability company organized under the laws of the People\'s Republic of China (hereinafter "Licensor") and Beijing Yisheng Leju Information Services Co., Ltd., a limited liability company organized under the laws of the People\'s Republic of China ("Licensee" and together with Licensor, the "Parties" and each a "Party") and is made effective as of the Effective  Date (defined below).', confidence=0.98

**Reasoning:** The excerpt expressly identifies when the agreement becomes effective by referencing the "Effective Date" and ties the agreement to that date. Although the actual calendar date is defined elsewhere in the excerpt as the Closing Date, the agreement date language is clearly present.

## correct_present_wrong_span (30 total)

### Worst 10 examples

### 1. `cuad-00103` — Audit Rights

**Contract:** DovaPharmaceuticalsInc_20181108_10-Q_EX-10.2_11414857_EX-10.2_Promotion Agreement

**Excerpt:**
```
CEUTICALS INC., 10-Q, 11/8/2018





primary or a secondary specialty designation of Gastroenterology, Colorectal Surgery or Proctology and that do not have either a primary or a secondary specialty designation of Hepatology shall be deemed to be in the Specialty.

6.5.4 The process described in this Section 6.5 shall be repeated for each Calendar Quarter of the Term; provided, however, that, pursuant to the process described above, if Dova's Third Party Data Source has confirmed that a Target Professional's primary specialty designation should be or should remain Gastroenterology, Colorect...
```

**Gold:** present=True
  - spans: ['Dova shall have the right, at its own expense, during normal business hours and upon reasonable prior notice, through a certified public accounting firm or other auditor selected by Dova and reasonably acceptable to Valeant and upon execution of a confidentiality agreement reasonably satisfactory to Valeant in form and substance, to inspect and audit the applicable records and books maintained by Valeant relating to the Valeant Activities for purposes of verifying Valeant\'s compliance with the terms of this Agreement, provided that (i) such examination shall not take place more often than once per every twelve (12) months during the Term and once during the one (1) year period following the end of the Term, and (ii) such examination shall not cover a period of time that has previously been audited; provided that Dova shall have the right to conduct additional "for cause" audits to the extent necessary to address significant compliance problems relating to Valeant\'s obligations hereunder or in response to any inquiry, inspection, investigation or other requirements of a Government Authority in the Territory relating to the Valeant Activities.', 'Valeant shall bear the out-of-pocket costs and expenses incurred by the Parties in connection with any such inspection or audit, unless the audit shows an undisputed under-reporting or underpayment for that audited period in excess of [***] of the amounts properly determined, in which case, Dova shall reimburse Valeant for its audit fees and reasonable out-of-pocket expenses in connection with said audit, which reimbursement shall be due and payable within [***] of receiving appropriate invoices and other support for such audit-related costs.', 'Valeant shall have the right, at its own expense, during normal business hours and upon reasonable prior notice, through certified public accounting firm or other auditor selected by Valeant and reasonably acceptable to Dova and upon execution of a confidentiality agreement reasonably satisfactory to Dova in form and substance, to inspect and audit the applicable records and books maintained by Dova for purposes of verifying Dova\'s payment obligations within this Agreement, including the applicable records and books of account maintained by Dova, or any Affiliate, as applicable, with respect to Net Sales in order to confirm the accuracy and completeness of such records and books of account and all payments hereunder; provided, however, that (i) such examination shall not take place more often than once per every twelve (12) months during the Term and once during the one (1) year period following the end of the Term, and (ii) such examination shall not cover a period of time that has previously been audited; provided that Valeant shall have the right to conduct additional "for cause" audits to the extent necessary to address significant problems relating to Dova\'s payment obligations hereunder.', "Where necessary, on reasonable request, Dova's audit rights shall include interviewing Sales Representatives and other employees of Valeant.", 'Dova shall bear the out-of-pocket costs and expenses incurred by the Parties in connection with any such inspection or audit, unless the audit shows an undisputed over- payment for that audited period in excess of [***] of the amounts properly determined, in which case, Valeant shall reimburse Dova for its audit fees and reasonable out-of-pocket expenses in connection with said audit, which reimbursement shall be due and payable within [***] of receiving appropriate invoices and other support for such audit-related costs.']

**Prediction:** present=True, span='ARTICLE 7  AUDIT RIGHTS', confidence=0.99
  - token Jaccard vs gold: 0.0952

**Reasoning:** The excerpt expressly includes an article titled "AUDIT RIGHTS" and detailed provisions granting each party inspection and audit rights in Sections 7.1 through 7.3. This is a direct and substantive match for the clause category.

### 2. `cuad-00061` — Agreement Date

**Contract:** NETGEAR,INC_04_21_2003-EX-10.16-AMENDMENT TO THE DISTRIBUTOR AGREEMENT BETWEEN INGRAM MICRO AND NETGEAR

**Excerpt:**
```
term under the Agreement will not be effective unless mutually agreed to in writing and signed by authorized representatives of both parties. Neither party shall be bound by typographical or clerical errors.

G.       Neither party is liable for its failure or delay to perform its obligations under the Agreement due to strikes, wars, revolutions, acts of terrorism, fires, floods, explosions, earthquakes, shortages in labor, components or materials, government regulations, or other causes beyond its control.

H.       This Agreement may not be assigned by either party without prior written p...
```

**Gold:** present=True
  - spans: ['October 1,1996']

**Prediction:** present=True, span='This Amendment is entered into effective October 1,1996 ("Amendment Date") by and between NETGEAR, Inc. ("NETGEAR"), a wholly owned subsidiary of Bay Networks, Inc., and Ingram Micro ("Distributor") acting on behalf of itself and its affiliates.', confidence=0.99
  - token Jaccard vs gold: 0.0968

**Reasoning:** The excerpt expressly states an effective date for the amendment and also references the original agreement's effective date. This is direct agreement-date language.

### 3. `cuad-00130` — Cap On Liability

**Contract:** FEDERATEDGOVERNMENTINCOMESECURITIESINC_04_28_2020-EX-99.SERV AGREE-SERVICES AGREEMENT

**Excerpt:**
```
istered (collectively, "Accounts"); and

WHEREAS, the Adviser desires to engage FASC to provide certain services to Adviser in connection with the services to be provided by the Adviser under the Advisory Agreements;

NOW, THEREFORE, the parties hereto, intending to be legally bound, agree as follows:

1. Services. FASC agrees to provide to the Adviser the services indicated in Exhibit A to this Agreement (the "Services").

2. Fees. For its Services under this Agreement, Adviser agrees to pay FASC the Services Fees calculated and payable in accordance with Exhibit B to this Agreement.

3. R...
```

**Gold:** present=True
  - spans: ['The Adviser and FASC are each hereby expressly put on notice of the limitation of liability set forth in the Declaration of Trust of the other party.']

**Prediction:** present=True, span='Each party agrees that the obligations of the other party pursuant to this Agreement shall be limited solely to such party and its assets, and neither party shall seek satisfaction of any such obligation from the shareholders, trustees, officers, employees or agents of the other party, or any of them.', confidence=0.98
  - token Jaccard vs gold: 0.1250

**Reasoning:** The excerpt includes a liability-limiting provision that restricts recovery to the party and its assets and bars claims against related persons. This is substantively a cap/limitation on liability, even though it is framed as a limitation on sources of satisfaction rather than a numeric cap.

### 4. `cuad-00060` — Agreement Date

**Contract:** ArtaraTherapeuticsInc_20200110_8-K_EX-10.5_11943350_EX-10.5_License Agreement

**Excerpt:**
```
Exhibit 10.5 CERTAIN CONFIDENTIAL INFORMATION CONTAINED IN THIS DOCUMENT, MARKED BY […***…], HAS BEEN OMITTED BECAUSE ARTARA THERAPEUTICS, INC. HAS DETERMINED THE INFORMATION (I) IS NOT MATERIAL AND (II) WOULD LIKELY CAUSE COMPETITIVE HARM TO ARTARA THERAPEUTICS, INC. IF PUBLICLY DISCLOSED. SPONSORED RESEARCH AND LICENSE AGREEMENT This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date"), by and between ArTara, Inc. located at 1 Little West 12t h Street, New York, NY 10014 ("ArTara"), and The University of Iowa, located at c...
```

**Gold:** present=True
  - spans: ['November 28, 2018']

**Prediction:** present=True, span='This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date"), by and between ArTara, Inc.', confidence=0.99
  - token Jaccard vs gold: 0.1500

**Reasoning:** The excerpt expressly states when the agreement is entered into and labels that date as the Effective Date. That is direct agreement-date language.

### 5. `cuad-00057` — Agreement Date

**Contract:** MusclepharmCorp_20170208_10-KA_EX-10.38_9893581_EX-10.38_Co-Branding Agreement

**Excerpt:**
```
ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT   This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date") by and between Marine MP, LLC ("Lender"), for services of Arnold Schwarzenegger ("Endorser"), and Fitness Publications, Inc. ("Fitness") (collectively, Lender, Endorser, and Fitness are referred to as the "AS Parties") and MusclePharm Corporation with its principal place of business in Denver, Colorado and its subsidiaries, (collectively, "MusclePharm" or the "Company").   RECITALS   WHEREAS, the AS Parties have the rights necessary t...
```

**Gold:** present=True
  - spans: ['July 26, 2013']

**Prediction:** present=True, span='This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date")', confidence=0.99
  - token Jaccard vs gold: 0.1765

**Reasoning:** The excerpt explicitly states the date the agreement is entered into and labels it as the Effective Date. This directly satisfies the Agreement Date category.

### 6. `cuad-00134` — Cap On Liability

**Contract:** QIWI_06_16_2017-EX-99.(D)(2)-COOPERATION AGREEMENT

**Excerpt:**
```
e Steering Committee shall consist of three representatives of QIWI Group and three representatives of Otkritie (each, a "Committee Member"). The representatives shall include:

 (a) at least one representative from Otkritie occupying the position of Chief Executive Officer or the Chairman of the Management Board orsimilar within Otkritie Holding JSC, PJSC Khanty-Mansiysk Bank Otkritie or JSC Bank Otkritie Financial Corporation; and

 (b) QIWI's Chief Executive Officer.

Each of Otkritie and QIWI Group shall have the exclusive right to remove and replace any of its designees to the Steering...
```

**Gold:** present=True
  - spans: ["For two (2) years following the Effective Time, QIWI covenants that at least one half of the total transactions processed by the Contact money transfer system during such two-year period shall be settled through PJSC Khanty-Mansiysk Bank Otkritie, provided that QIWI may terminate its obligation under this Clause 4.1 at any time, in which case it shall pay to Otkritie a fee equal to the demonstrated costs incurred by Otkritie for such period starting from 1 September 2014, until the date of termination of QIWI's obligations under this Clause 4.1 in connection with (i) the transfer of settlement bank function to PJSC Khanty-Mansiysk Bank Otkritie ; and (ii) supporting the settlement bank functionality for the Contact money transfer system, provided further that such fee shall in no event exceed RUB 50 000 000 (fifty million roubles)."]

**Prediction:** present=True, span='provided further that such fee shall in no event exceed RUB 50 000 000 (fifty million roubles).', confidence=0.98
  - token Jaccard vs gold: 0.1818

**Reasoning:** The excerpt includes an express monetary ceiling on a fee payable upon termination of obligations, which functions as a cap on liability/payment exposure. Although it is not a broad limitation-of-liability clause, it substantively imposes a maximum amount.

### 7. `cuad-00000` — Affiliate License-Licensee

**Contract:** OTISWORLDWIDECORP_04_03_2020-EX-10.4-INTELLECTUAL PROPERTY AGREEMENT by and among UNITED TECHNOLOGIES CORPORATION, OTIS WORLDWIDE CORPORATION and CARRIER ~1

**Excerpt:**
```
Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee Party and the other members of the Licensee Group, subject to the field restriction of Section 3.1.2, a royalty-free, nonexclusive, perpetual, irrevocable, fully paid-up, worldwide right and license, with the right to sublicense as provided in Section 3.1.3, to Exploit Intellectual Property Rights that are owned by the ...
```

**Gold:** present=True
  - spans: ['Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee Party and the other members of the Licensee Group, subject to the field restriction of Section 3.1.2, a royalty-free, nonexclusive, perpetual, irrevocable, fully paid-up, worldwide right and license, with the right to sublicense as provided in Section 3.1.3, to Exploit Intellectual Property Rights that are owned by the Licensor Party or another member of the Licensor Group immediately following the assignments pursuant to Article II and meet one or more of the following descriptions with respect to the relevant Licensee Party: (a) the Intellectual Property Rights are rights under Licensed Patents or other Intellectual Property Rights that, in each case, as of the Effective Time, are either (A) used in connection with, or necessary for the ongoing conduct of, the current business of the Licensee Party or another member of the Licensee Group, or (B) Contemplated to be Used in the business of the Licensee Party, or another member of the Licensee Group, in the Licensee Group Field; provided, however, that the license granted in this Section 3.1.1(a) does not apply to the Intellectual Property Rights received under or otherwise governed by an Excluded Agreement; and/or (b) the Intellectual Property Rights are embodied in an invention, or proposed invention, that is both (i) described in a Patent or Invention Disclosure held by the Licensor Party or another member of the Licensor Group and (ii) conceived by at least one inventor who, at the time of conception, was employed by a member of the Licensee Group, a non-inclusive list of which inventions and proposed inventions are provided in Schedule 3.1.1(b), provided, however, that the license granted in this Section 3.1.1(b) does not apply to an invention conceived under or otherwise governed by an Excluded Agreement; and/or (c) the Intellectual Property Rights are subject to an assignment to the Licensor Party in Section 2.1.1(b) concerning Performer Foreground-Delivered IPR conceived or created in the course of services concerning which the Licensor Party or another member of the Licensor Group was the Requester and the Licensee Party or another member of the Licensee Group was the Performer; and/or', '4.2.3 UTC, on behalf of itself and the other members of the UTC Group, hereby grants to Otis, Carrier and the other members of the Otis Group and the Carrier Group a limited, non-exclusive, non-transferable, personal and nonsublicensable right to continue temporarily to use, following the Effective Time, any United Technologies Trademark it is using immediately prior to the Effective Time, solely to the extent of such pre- Separation use and in accordance with product quality standards and programs in place at the respective member of the Otis Group or the Carrier Group immediately prior to the Effective Time, and strictly in accordance with this Section 4.2.3; provided that Otis and Carrier shall, and shall cause each of its respective Affiliates (including, after the Effective Time, the members of, respectively, the Otis Group and the Carrier Group) (a) not to hold itself out as having any affiliation with UTC or any member of the UTC Group (except to the extent a third party may infer such affiliation merely due to the limited use of the United Technologies Trademarks as contemplated herein), and (b) to use diligent efforts to eliminate use of the United Technologies Trademarks.', '(d) the Intellectual Property Rights are Performer Background IPR or Patent rights of the Licensor Party or another member of the Licensor Group and is necessary for the Licensee Party or another member of the Licensee Party to Exploit the Performer Foreground-Delivered IPR in the Licensee Group Field, provided, however, that the license granted in this Section 3.1.1(d) applies only to the extent necessary for the Licensee Party or another member of the Licensee Group to Exploit the Performer Foreground-Delivered IPR in the Licensee Group Field. (collectively, "Licensed Intellectual Property Rights").']

**Prediction:** present=True, span='a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant to the applicable Licensee Party and the other members of the Licensee Group', confidence=0.99
  - token Jaccard vs gold: 0.2069

**Reasoning:** The excerpt expressly grants license rights from a Licensor Party to the applicable Licensee Party and other members of the Licensee Group, which is directly on point for an affiliate license to a licensee group. It also repeatedly refers to rights of the Licensee Group and sublicense rights, confirming the affiliate-license structure.

### 8. `cuad-00052` — Agreement Date

**Contract:** EhaveInc_20190515_20-F_EX-4.44_11678816_EX-4.44_License Agreement_ Reseller Agreement

**Excerpt:**
```
Exhibit 4.44 THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018 is made BETWEEN: EHAVE, INC., a company incorporated under the laws of the Province of Ontario, Canada ("Ehave"); - and - COMPANION HEALTHCARE TECHNOLOGIES CORP, a company incorporated under the laws of the Province of Ontario ("CHT") RECITALS: A. Ehave has developed a software platform that provides an end-to-end patient management solution to healthcare professionals and provides that platform to users as a service. B. CHT has developed a business model to bring a similar service that Ehave provides using th...
```

**Gold:** present=True
  - spans: ['October 30, 2018']

**Prediction:** present=True, span='THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018', confidence=0.99
  - token Jaccard vs gold: 0.2500

**Reasoning:** The excerpt explicitly states the agreement date in the opening line. It uses clear dated-as-of language identifying October 30, 2018 as the agreement date.

### 9. `cuad-00008` — Affiliate License-Licensee

**Contract:** XENCORINC_10_25_2013-EX-10.24-COLLABORATION AGREEMENT (3)

**Excerpt:**
```
ness Partner or its affiliate to manufacture and supply commercial Product); provided that the supply price for Product is no more than [...***...] percent ([...***...]%) of the commercial supply price of Product last proposed by BII during the negotiations between the Parties (or BII and the Business Partner). If the supply price for Product proposed by a third party (which may include a Business Partner or its affiliate) is more than [...***...] percent ([...***...]%) of the commercial supply price of Product last proposed by BII during the negotiations between the Parties (or BII and the...
```

**Gold:** present=True
  - spans: ['In the event that XENCOR pays the Technology Access Fee set forth above, XENCOR shall have the right to use or have used (e.g. by a Business Partner) the Process worldwide for the manufacture of Product in accordance with the terms and conditions of this Agreement, without entering into a contract manufacturing agreement with BII']

**Prediction:** present=True, span='XENCOR (or its Business Partner) shall provide written notice to BII that XENCOR (and its Business Partner) will accept the commercial supply price last proposed by BII, and BII and XENCOR (or its Business Partner) will enter into a contract manufacturing agreement reflecting such commercial supply price; provided that, if BII does not agree to enter into such contract manufacturing agreement within [...***...] after such written notice, XENCOR (or its Business Partner) shall be free to enter into an agreement with a third party (which may include an agreement for any Business Partner or its affiliate to manufacture and supply Product).', confidence=0.93
  - token Jaccard vs gold: 0.2667

**Reasoning:** The excerpt expressly allows XENCOR to use the Process through a Business Partner and to enter agreements where a Business Partner or its affiliate manufactures and supplies Product. This is substantively related to a licensee’s affiliate rights under the agreement.

### 10. `cuad-00035` — Affiliate License-Licensor

**Contract:** ArconicRolledProductsCorp_20191217_10-12B_EX-2.7_11923804_EX-2.7_Trademark License Agreement

**Excerpt:**
```
Exhibit 2.7 FORM OF TRADEMARK LICENSE AGREEMENT THIS TRADEMARK LICENSE AGREEMENT (this "Agreement"), made and entered into as of the [ ] day of [ ], 2020 (the "Effective Date"), by and between ARCONIC INC., a corporation organized under the laws of Delaware ("Licensee") and ARCONIC ROLLED PRODUCTS CORP., a corporation organized under the laws of Delaware ("Licensor"). WHEREAS, Licensor and Licensee entered into a Separation and Distribution Agreement having an effective date of the [ ] day of [ ], 2020 ("Separation and Distribution Agreement"); unless specifically defined in this Agreement,...
```

**Gold:** present=True
  - spans: ['Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark: (i) for the Licensed Products as set forth on Schedule 2; and (ii) as set forth on Schedule 1, concerning agreements entered into by Licensee prior to the Effective Date ("Existing Agreements"). For the avoidance of doubt, Licensor also grants to Licensee and its subsidiaries and affiliates a non-exclusive, worldwide royalty-free license for continued use of the Licensed Mark for the production and sale of inventory containing the Licensed Mark applied to such products during the Transition Period as set forth in section 8.2 of the Separation and Distribution Agreement and in Schedule 2 of this Agreement.']

**Prediction:** present=True, span='Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark', confidence=0.99
  - token Jaccard vs gold: 0.2941

**Reasoning:** The excerpt expressly states that the Licensor grants rights "on behalf of itself and its Affiliates," which is direct affiliate-licensor language. It also extends the license to Licensee's subsidiaries and affiliates, reinforcing that affiliate licensing is substantively addressed.

## hallucinated_span (7 total)

### Worst 7 examples

### 1. `cuad-00107` — Audit Rights

**Contract:** SANDRIDGEENERGYINC_08_06_2009-EX-10.6-OPERATIONS AND MAINTENANCE AGREEMENT

**Excerpt:**
```
ative to Owner's business as are usually entered into records and books of account, and the same shall be supported by purchase  orders, invoices, payrolls or other customary or necessary records pertaining thereto. Owner's financial books and records shall be kept in  accordance with GAAP and shall be maintained on an accrual basis, and Owner shall provide Operator with the applicable income tax provisions.  The costs of any audit of Owner's books or records shall be borne by Owner.

6.2 Financial Statements.

     Operator shall deliver to Owner the financial statements of Owner prepared,...
```

**Gold:** present=True
  - spans: ["and records available for inspection by Owner's auditors, and (ii) making such copies of books and records as may be reasonably requested by  such auditors. In no event shall Owner's audits unreasonably interfere with Operator's operations.", "Owner shall have up until two years after the close of a Calendar Year in which to make an audit of Operator's records  for such Calendar Year.", "The costs of any audit of Owner's books or records shall be borne by Owner.", 'Owner shall engage an auditor for this purpose no later than 45 days after the  end of each fiscal year.', "Upon reasonable prior written notice to Operator, Owner shall have the right during normal business hours to audit or examine all books and  records of Operator to the extent they relate to Operator's performance hereunder as well as the relevant books of account of Operator's  contractors, relating to the performance of Operator's obligations under this Agreement. Operator shall cooperate with Owner's auditors by  (i) making the applicable books", 'Owner will be responsible for all costs of any  such audit; provided that if, in any audit, Owner discovers overpayments by Owner of at least $250,000 in the aggregate ("Material  Overpayment"), Operator will reimburse Owner for such Material Overpayment and all reasonable costs incurred by Owner in connection with  such audit ("Audit Costs").']

**Prediction:** present=True, span='Upon reasonable prior written notice to Operator, Owner shall have the right during normal business hours to audit or examine all books and records of Operator to the extent they relate to Operator\'s performance hereunder as well as the relevant books of account of Operator\'s contractors, relating to the performance of Operator\'s obligations under this Agreement. Operator shall cooperate with Owner\'s auditors by (i) making the applicable books and records available for inspection by Owner\'s auditors, and (ii) making such copies of books and records as may be reasonably requested by such auditors. In no event shall Owner\'s audits unreasonably interfere with Operator\'s operations. Owner will be responsible for all costs of any such audit; provided that if, in any audit, Owner discovers overpayments by Owner of at least $250,000 in the aggregate ("Material Overpayment"), Operator will reimburse Owner for such Material Overpayment and all reasonable costs incurred by Owner in connection with such audit ("Audit Costs"). Owner shall have up until two years after the close of a Calendar Year in which to make an audit of Operator\'s records for such Calendar Year.', confidence=0.99

**Reasoning:** The excerpt expressly grants Owner the right to audit or examine Operator's books and records, sets cooperation obligations, and addresses audit costs and timing. This is direct audit-rights language.

### 2. `cuad-00108` — Audit Rights

**Contract:** MRSFIELDSORIGINALCOOKIESINC_01_29_1998-EX-10-FRANCHISE AGREEMENT

**Excerpt:**
```
 its  financial  officer,  attesting  that (1) the reports are true and accurate,  (2) they are prepared in accordance with GAPP on a basis  consistent  with prior periods,  (3) they fully describe and completely disclose the information sought, and (4) the signer has made diligent efforts to ascertain the truth and completeness of the information.

         15.B.   MAINTENANCE OF RECORDS.

         Franchisee  agrees, at all times, he shall keep and maintain  adequate, accurate,  true, and proper records, books, reports, data, and accounts relative to the  franchise  in the English  langua...
```

**Gold:** present=True
  - spans: ["The audit will be conducted at the expense of Pretzel Time, provided that if an audit  disclosed an  understatement  of two percent (2%), as described above,  Franchisee will bear the cost of the audit,  including without limitation,  the charges of attorneys  and any  independent  accountants,  their travel   expenses,   room  and  board,   and   compensation  of  Pretzel  Time's representatives  and  independent  accountants.", "Franchisee shall fully cooperate with Pretzel Time's representatives and independent accountants hired by Pretzel Time to conduct any such inspection or audit.", 'Pretzel  Time or its  designee  shall have the right at any time during business  hours and without prior notice to  Franchisee,  to inspect,  audit and copy or the right to cause to be  inspected,  audited and copied,  the  business records,  bookkeeping and accounting  records,  sales and income tax records and returns and other records of the Franchised Business,  including but not limited to,  daily  cash  reports,  cash  receipts  journal  and  general  ledger,  cash disbursements  journal and weekly payroll register,  monthly bank statements and daily deposit slips and cancelled checks; tax returns,  supplier invoices, dated cash register tapes, weekly inventories, sales reports, financial statements and tax returns and the books and records of any  corporation or  partnership  which holds the Franchise  including the personal financial records and tax returns of the Franchisee during and after the term of the Franchise Agreement.', "To determine  whether  Franchisee  and the Unit are complying with this Agreement and with all Pretzel Time's  standards and operations as prescribed by Pretzel Time,  Pretzel Time or its designated agents shall have the right at any reasonable time and without prior notice to Franchisee to:\n\n         a.  Inspect the Unit;\n\n         b. Observe,  photograph  and video tape the Unit's  operations for such          consecutive or intermittent periods as Pretzel Time deems necessary;\n\n         c. Remove  samples of any  Products,  materials or supplies for testing and analysis;\n\n         d.  Interview personnel of the Unit;\n\n         e.  Interview customers of the Unit; and\n\n         f. Inspect and copy any books,  records and  documents  relating to the          operation  of the Unit.  Franchisee  agrees  to  cooperate  fully  with          Pretzel Time in connection with any such inspections, observations,  photographing,  video  taping,  Product  removal and  interviews. Franchisee  shall present to his customers  such comment or evaluation  forms as Pretzel Time periodically  prescribes and shall  participate  and/or request his customers  to  participate  in any surveys  performed by or on behalf of Pretzel Time.", 'Providing  that in no case will Franchisee be obligated to pay more than ten thousand dollars ($10,000) for such inspection  or audit  costs.']

**Prediction:** present=True, span='Pretzel Time or its designee shall have the right at any time during business hours and without prior notice to Franchisee, to inspect, audit and copy or the right to cause to be inspected, audited and copied, the business records, bookkeeping and accounting records, sales and income tax records and returns and other records of the Franchised Business', confidence=0.99

**Reasoning:** The excerpt expressly grants Pretzel Time the right to inspect, audit, and copy the franchisee’s records without prior notice. It also includes related audit procedures, cooperation requirements, and cost-shifting if an understatement is found.

### 3. `cuad-00126` — Cap On Liability

**Contract:** CORIOINC_07_20_2000-EX-10.5-LICENSE AND HOSTING AGREEMENT

**Excerpt:**
```
reement; and (d) the Software does not infringe any patent,         copyright, trade secret, trademark or other intellectual property rights         of a third party.

7.3     Product Warranty. Commerce One warrants that the Software and         MarketSite.net Service will perform in substantial accordance with the         Documentation, and the media on which the Software is distributed will         be free from defects in materials and workmanship under normal use, for         a period of sixty (60) days from the Effective Date, but in no event not         later than December 31, 1999 (th...
```

**Gold:** present=True
  - spans: ["The foregoing are         Corio's sole and exclusive remedies for breach of product warranty.", 'EXCEPT FOR LIABILITY         ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO EVENT SHALL EITHER         PARTY HAVE ANY LIABILITY TO THE OTHER PARTY FOR ANY LOST PROFITS OR         COSTS OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, OR FOR ANY         INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES HOWEVER CAUSED AND UNDER ANY         THEORY OF LIABILITY AND WHETHER OR NOT SUCH PARTY HAS BEEN ADVISED OF         THE POSSIBILITY OF SUCH DAMAGE.', "EXCEPT FOR LIABILITY ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO         EVENT SHALL EITHER PARTY'S LIABILITY ARISING OUT OF THIS AGREEMENT OR         THE USE OR PERFORMANCE OF THE SOFTWARE EXCEED THE TOTAL AMOUNT ACTUALLY         PAID BY CORIO HEREUNDER FOR THE TRANSACTION WHICH THE LIABILITY RELATES         TO DURING THE TWELVE (12) MONTHS IMMEDIATELY PRIOR TO THE FILING OF THE         CAUSE OF ACTION TO WHICH THE LIABILITY RELATES. EXCEPT FOR LIABILITY         ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO EVENT SHALL EITHER         PARTY HAVE ANY LIABILITY TO THE OTHER PARTY FOR ANY LOST PROFITS OR         COSTS OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, OR FOR ANY         INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES HOWEVER CAUSED AND UNDER ANY         THEORY OF LIABILITY AND WHETHER OR NOT SUCH PARTY HAS BEEN ADVISED OF         THE POSSIBILITY OF SUCH DAMAGE."]

**Prediction:** present=True, span="IN NO EVENT SHALL EITHER PARTY'S LIABILITY ARISING OUT OF THIS AGREEMENT OR THE USE OR PERFORMANCE OF THE SOFTWARE EXCEED THE TOTAL AMOUNT ACTUALLY PAID BY CORIO HEREUNDER FOR THE TRANSACTION WHICH THE LIABILITY RELATES TO DURING THE TWELVE (12) MONTHS IMMEDIATELY PRIOR TO THE FILING OF THE CAUSE OF ACTION TO WHICH THE LIABILITY RELATES.", confidence=0.99

**Reasoning:** The excerpt expressly limits each party's liability to the amount paid by Corio in the prior 12 months, which is a clear cap on liability. It also excludes certain consequential damages, reinforcing the limitation.

### 4. `cuad-00131` — Cap On Liability

**Contract:** STAMPSCOMINC_06_24_1999-EX-10.18-SPONSORSHIP AGREEMENT

**Excerpt:**
```
 conflict with, or result in a      material default under any other contract or agreement to which Intuit is a      party, or by which it is bound; and (iii) it has the right to make      available on the Intuit Sites the Banner Advertisements, Sponsor Client      Graphics, Links and other advertisements placed hereunder.

16.3 By Client.  Client will defend and/or settle any third party claim brought      ---------      against Intuit, its affiliates, officers, directors, employees, consultants      and agents arising from:  (1) a breach of Client's representations or      warranties unde...
```

**Gold:** present=True
  - spans: ['THE LIABILITY OF EITHER PARTY FOR DAMAGES OR ALLEGED DAMAGES      HEREUNDER (EXCEPT UNDER SECTIONS 15 AND 16), WHETHER IN CONTRACT, TORT OR      ANY OTHER LEGAL THEORY, IS LIMITED TO, AND WILL NOT EXCEED, THE AMOUNTS TO      BE PAID BY CLIENT TO INTUIT HEREUNDER.', 'BASED ON BREACH OF CONTRACT, TORT (INCLUDING NEGLIGENCE) OR OTHERWISE,      WHETHER OR NOT THAT PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH      DAMAGE.', 'EXCEPT UNDER SECTIONS 15 AND 16, IN NO EVENT WILL EITHER PARTY BE LIABLE TO      THE OTHER FOR ANY SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES, WHETHER']

**Prediction:** present=True, span='THE LIABILITY OF EITHER PARTY FOR DAMAGES OR ALLEGED DAMAGES HEREUNDER (EXCEPT UNDER SECTIONS 15 AND 16), WHETHER IN CONTRACT, TORT OR ANY OTHER LEGAL THEORY, IS LIMITED TO, AND WILL NOT EXCEED, THE AMOUNTS TO BE PAID BY CLIENT TO INTUIT HEREUNDER.', confidence=0.99

**Reasoning:** The excerpt includes an explicit limitation of liability clause that caps damages at the amounts paid by Client to Intuit. This is substantively a cap on liability.

### 5. `cuad-00030` — Affiliate License-Licensor

**Contract:** GSITECHNOLOGYINC_11_16_2009-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT between SONY ELECTRONICS INC. and GSI TECHNOLOGY, INC.

**Excerpt:**
```
ined herein, including the following terms, which shall have the meanings set forth below:     1





     1.1 IP Agreement     The term "IP Agreement" means this Intellectual Property Agreement, including all attached Exhibits hereto, and any  amendments or supplements agreed to in writing and signed by SONY and PURCHASER.     1.2 Asset Purchase Agreement     The term "Asset Purchase Agreement" means the Asset Purchase Agreement dated August 28, 2009 between SONY and  PURCHASER to which this IP Agreement is attached as Exhibit F.     1.3 Effective Date     The term "Effective Date" means t...
```

**Gold:** present=True
  - spans: ['SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free  license (a) under the Licensed Patents to make, have made, use, offer to sell, sell, otherwise dispose of, and import any Competing Products  (including, without limitation, the SRAM Products); and (b) to use, reproduce, modify, prepare derivative works of, perform, display, and otherwise  practice and exploit in any manner any and all of the SRAM Intellectual Property in connection with the use and exploitation of the', 'Transferred Assets, and to make, have made, use, offer to sell, sell, otherwise dispose of, and import Competing Products (including, without  limitation, SRAM Products).']

**Prediction:** present=True, span='SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free license', confidence=0.98

**Reasoning:** The excerpt expressly states that SONY grants the license “on behalf of itself and its Affiliates,” which is direct affiliate-licensor language. This is substantively about an affiliate granting or being included in the licensor side of the license.

### 6. `cuad-00100` — Audit Rights

**Contract:** IVILLAGEINC_03_17_1999-EX-10.16-SPONSORSHIP AGREEMENT

**Excerpt:**
```
 work together in good faith to amend or terminate this Agreement.

2.       Promotion.

         A. During the Production Period, iVillage will design, develop, construct and host a Ford bridge site (the "Bridge Site") which shall include approximately [*] pages of content and other interactive material such as a travel planner or a car design feature. During the Promotion Period, iVillage will continue to host, maintain and update the Bridge Site. Upon receipt from iVillage of the proposed Bridge Site design and content, FMM shall have no more than five (5) business days in which to provi...
```

**Gold:** present=True
  - spans: ['All traffic reports shall be audited by the third party traffic auditor selected pursuant to Section 2.C.(ii).', 'During the Promotion Period, iVillage traffic shall be          audited by a third party traffic auditor listed on Exhibit A and          iVillage shall provide FMM with relevant reports on a biweekly basis.']

**Prediction:** present=True, span='During the Promotion Period, iVillage traffic shall be audited by a third party traffic auditor listed on Exhibit A and iVillage shall provide FMM with relevant reports on a biweekly basis.', confidence=0.98

**Reasoning:** The excerpt expressly requires that iVillage traffic be audited by a third-party traffic auditor and that reports be provided to FMM. This is substantive audit-related language, even though it does not spell out broader inspection or access rights.

### 7. `cuad-00005` — Affiliate License-Licensee

**Contract:** ConformisInc_20191101_10-Q_EX-10.6_11861402_EX-10.6_Development Agreement

**Excerpt:**
```
riteria, then Stryker will provide Conformis with a written notice of rejection within the Acceptance Notification Period   describing the defect in view of the relevant Acceptance Criteria and including sufficient detail with respect to such Stryker testing   and testing results as Conformis reasonably requests ("Failure Notice"). Conformis shall have [**] (or such longer period of time   as may be agreed between the parties in good faith should the scope and complexity of the applicable Deliverable warrant some   longer period of time) ("Redelivery Period") following the date it receives ...
```

**Gold:** present=True
  - spans: ['Except as specifically provided in the Distribution Agreement, Conformis shall be prohibited from   developing or assisting another in developing, or causing another to develop, Patient-Specific Instrumentation for Off-The-Shelf   Knee Implants for any Third Party in the field of orthopedics until January 1, 2032 (or earlier, to the extent set forth in Section   2.3.3.4 or Section 2.3.5 of the Distribution Agreement), with the exception that Conformis (including any entity involved in a   Change of Control of Conformis, any such entity an "Acquirer"), may develop Patient-Specific Instrumentation for any Off-The-   Shelf Implants of Conformis, an Acquirer or any of their Affiliates.']

**Prediction:** present=True, span='Subject to the limitations set forth in this Agreement, the Joint IP may be used freely by either Party or its Affiliates and licensed to Third Parties by Conformis and its Affiliates, on the one hand, outside of the Buyer Field or by Stryker and its Affiliates, on the other hand, within the Buyer Field, in each case, without the consent of, or duty to account to or notify, the other Party', confidence=0.93

**Reasoning:** The excerpt expressly addresses licensing rights involving Affiliates, including use and licensing by each party and its Affiliates. This is substantively related to an affiliate license arrangement for the licensee side.

## parse_fail (0 total)

_No errors in this bucket._
