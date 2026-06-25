# Error report — `google`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | Affiliate License-Licensor | 1 |
| missed_present | Cap On Liability | 1 |
| false_present | Affiliate License-Licensee | 1 |
| false_present | Affiliate License-Licensor | 1 |
| false_present | Agreement Date | 10 |
| false_present | Audit Rights | 1 |
| false_present | Cap On Liability | 1 |
| correct_present_wrong_span | Affiliate License-Licensee | 2 |
| correct_present_wrong_span | Affiliate License-Licensor | 4 |
| correct_present_wrong_span | Agreement Date | 10 |
| correct_present_wrong_span | Anti-Assignment | 2 |
| correct_present_wrong_span | Audit Rights | 5 |
| correct_present_wrong_span | Cap On Liability | 4 |
| hallucinated_span | Affiliate License-Licensee | 3 |
| hallucinated_span | Affiliate License-Licensor | 1 |
| hallucinated_span | Anti-Assignment | 2 |
| hallucinated_span | Audit Rights | 3 |
| hallucinated_span | Cap On Liability | 3 |
| parse_fail | _none_ | 0 |

## missed_present (2 total)

### Worst 2 examples

### 1. `cuad-00028` — Affiliate License-Licensor

**Contract:** GOOSEHEADINSURANCE,INC_04_02_2018-EX-10.6-Franchise Agreement

**Excerpt:**
```
Franchised Business; (b) furnish us with a copy of your articles of organization and operating agreement, as well as such other documents as we may reasonably request, and any amendments thereto; (c) prepare and furnish to us, upon request, a current list of all members and managers in your LLC; and (d) maintain stop transfer instructions on your records against the transfer of equity securities and will only issue securities upon the face of which bear a legend, in a form satisfactory to us, which references the transfer restrictions imposed by this Agreement. 8.10.4 Guarantees. You agree ...
```

**Gold:** present=True
  - spans: ['You hereby grant to us (and agree to obtain from your affiliates, owners, employees, and/or contractors), a perpetual, non-exclusive, and worldwide right to use any such ideas, concepts, methods, techniques and products in any businesses that we and/or our affiliates, franchisees and designees operate. We will have the right to use those ideas, concepts, methods, techniques, and/or products without making payment to you. You agree not to use or allow any other person or entity to use any such concept, method, technique or product']

**Prediction:** present=False, span=None, confidence=0.95

**Reasoning:** The excerpt discusses the franchisee granting rights to the licensor and its affiliates (Section 8.14), but it does not contain any language where the licensor grants a license to its own affiliates. The category 'Affiliate License-Licensor' implies the licensor is granting a license to its affiliates, which is not present.

### 2. `cuad-00133` — Cap On Liability

**Contract:** REGANHOLDINGCORP_03_31_2008-EX-10-LICENSE AND HOSTING AGREEMENT

**Excerpt:**
```
nt Indemnification

LMG represents and warrants that (i) no LMG Tools, CSC Software, Other Third Party Software or Documentation provided under this Agreement is the subject of any claim, dispute, demand or litigation ("Claim"), and (ii) LMG has all right, title, ownership interest, and/or  rights necessary to provide such software and Documentation to TAG and that the License, the LMG Tools and Documentation and their license and Use hereunder do not and shall not directly or indirectly violate or infringe upon any copyright, patent, trade secret, or other proprietary or intellectual prope...
```

**Gold:** present=True
  - spans: ["LMG's indemnification obligations under this Section 5.2 will expire twelve (12) months after the Conversion Date.", 'Neither party shall be liable to the other pursuant to this Agreement for any amounts representing loss of profit, loss of business or indirect, consequential, exemplary, or punitive damages of the other party.', "TAG's indemnification obligations under this Section 5.3 will expire twelve (12) months after the Conversion Date."]

**Prediction:** present=False, span=None, confidence=0.9

**Reasoning:** The excerpt contains a 'Limitation of Liability' clause which excludes certain types of damages (e.g., loss of profit, consequential, punitive damages) and specifies carve-outs for indemnification and certain breaches. However, it does not impose a specific monetary cap or maximum amount on either party's overall liability.

## false_present (14 total)

### Worst 10 examples

### 1. `cuad-00016` — Affiliate License-Licensee

**Contract:** AMBASSADOREYEWEARGROUPINC_11_17_1997-EX-10.28-ENDORSEMENT AGREEMENT

**Excerpt:**
```
Exhibit 10.28

                              ENDORSEMENT AGREEMENT

            This Endorsement Agreement ("Agreement") is made and entered into as of August 24, 1995, by and among the following parties:

                  (a) Kathy Ireland, Inc. ("KI Inc."), furnishing the services       of Kathy Ireland ("KI"), c/o The Sterling/Winters Co., 1900 Avenue of the       Stars, Suite #1640, Los Angeles, California 90067;

                  (b) The Sterling/Winters Co. ("SW"), 1900 Avenue of the Stars,       Suite #1640, Los Angeles, California 90067; and

                  (c) Diplomat Ambassa...
```

**Gold:** present=False

**Prediction:** present=True, span='Diplomat agrees to pay KI, Inc. as royalty a sum equal to  % of the net wholesale volume of the products covered by this Agreement by Diplomat and its affiliated, associated, or subsidiary companies.', confidence=1.0

**Reasoning:** The clause explicitly states that royalties are based on the wholesale volume of products sold by 'Diplomat and its affiliated, associated, or subsidiary companies,' indicating that the license's scope extends to the licensee's affiliates.

### 2. `cuad-00062` — Agreement Date

**Contract:** LohaCompanyltd_20191209_F-1_EX-10.16_11917878_EX-10.16_Supply Agreement

**Excerpt:**
```
Exhibit 10.16 SUPPLY CONTRACT Contract No: Date: The buyer/End-User: Shenzhen LOHAS Supply Chain Management Co., Ltd. ADD: Tel No. : Fax No. : The seller: ADD: The Contract is concluded and signed by the Buyer and Seller on , in Hong Kong. 1. General provisions 1.1 This is a framework agreement, the terms and conditions are applied to all purchase orders which signed by this agreement (hereinafter referred to as the "order"). 1.2 If the provisions of the agreement are inconsistent with the order, the order shall prevail. Not stated in order content will be subject to the provisions of agree...
```

**Gold:** present=False

**Prediction:** present=True, span='Date: The buyer/End-User: Shenzhen LOHAS Supply Chain Management Co., Ltd. ADD: Tel No. : Fax No. : The seller: ADD: The Contract is concluded and signed by the Buyer and Seller on , in Hong Kong.', confidence=1.0

**Reasoning:** The excerpt explicitly includes a 'Date:' field and states 'The Contract is concluded and signed by the Buyer and Seller on', indicating the presence of an agreement date clause, even if the specific date is a blank placeholder.

### 3. `cuad-00063` — Agreement Date

**Contract:** PHLVARIABLEINSURANCECOCT_08_17_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
STRATEGIC ALLIANCE AGREEMENT

This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the  "Effective Date"), by and among PHL VARIABLE INSURANCE COMPANY ("PHLVIC"), PHOENIX LIFE INSURANCE COMPANY, ("PLIC"  and, together with PHLVIC, "PHL Variable"), PHOENIX EQUITY PLANNING CORPORATION ("PEPCO" and, together with PHLVIC and PLIC,  the "PHL Parties"), and INVESTORS CAPITAL CORPORATION ("ICC"). Except as otherwise defined, capitalized terms used herein shall have  the meanings given to them in Section 1 Definitions, be...
```

**Gold:** present=False

**Prediction:** present=True, span='This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the  "Effective Date")', confidence=1.0

**Reasoning:** The introductory paragraph explicitly states when the agreement is entered into, defining it as the 'Effective Date'. This directly addresses the agreement date.

### 4. `cuad-00065` — Agreement Date

**Contract:** IOVANCEBIOTHERAPEUTICS,INC_08_03_2017-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
Exhibit 10.1   Text Marked By [* * *] Has Been Omitted Pursuant To A Request For Confidential Treatment And Was Filed Separately With The Securities And Exchange Commission.   STRATEGIC ALLIANCE AGREEMENT Effective Date: April 17, 2017   THIS STRATEGIC ALLIANCE AGREEMENT (this "Agreement"), is entered into by and between Lion Biotechnologies, Inc., with a place of business located at 999 Skyway Road, Suite 150, San Carlos, CA 94070 ("LBIO"), and The University of Texas M. D. Anderson Cancer Center, with a place of business located at 1515 Holcombe Blvd., Houston, TX 77030 ("MD Anderson"), a...
```

**Gold:** present=False

**Prediction:** present=True, span='Effective Date: April 17, 2017', confidence=1.0

**Reasoning:** The excerpt explicitly states the 'Effective Date' of the Strategic Alliance Agreement as April 17, 2017, and defines it as the date the agreement is entered into.

### 5. `cuad-00066` — Agreement Date

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

**Prediction:** present=True, span='Dated: ____________________', confidence=1.0

**Reasoning:** The excerpt explicitly includes a placeholder for the agreement date, indicating its presence in the document structure.

### 6. `cuad-00069` — Agreement Date

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

**Prediction:** present=True, span='Effective Dates: September 1, 2006', confidence=1.0

**Reasoning:** The excerpt explicitly states the 'Effective Dates' for the agreement, which includes the start date of the agreement's operation.

### 7. `cuad-00070` — Agreement Date

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

**Prediction:** present=True, span='This Agreement is entered into with effect as of the Effective Date (as defined below)', confidence=1.0

**Reasoning:** The excerpt explicitly states that the agreement is entered into 'with effect as of the Effective Date (as defined below)', directly addressing the agreement's commencement date.

### 8. `cuad-00071` — Agreement Date

**Contract:** PfHospitalityGroupInc_20150923_10-12G_EX-10.1_9266710_EX-10.1_Franchise Agreement1

**Excerpt:**
```
FORM OF FRANCHISE AGREEMENT Location of the Premises: Agreement Date Franchisee Business Address

Type of Legal Entity (if applicable) State in which entity organized (if applicable) Shareholder / Partner / Member Name Ownership Percentage % (the "Operating Principal") % % % %

Source: PF HOSPITALITY GROUP INC., 10-12G, 9/23/2015





TABLE OF CONTENTS SECTION PAGE 1. RIGHTS GRANTED 2 2. TERM; SUCCESSOR FRANCHISE AGREEMENTS 4 3. FEES 4 4. OPENING DEADLINE 6 5. TRAINING 10 6. OPERATIONS 11 7. PROPRIETARY MARKS 18 8. BUSINESS RECORDS AND REPORTING 19 9. MARKETING FUND AND ADVERTISING 21 10. T...
```

**Gold:** present=False

**Prediction:** present=True, span='This Franchise Agreement (the "Agreement") is entered into as of the Agreement Date shown on the cover page between Pizza Fusion Holding, Inc., a Florida corporation, and the individual or legal entity identified on the cover page ("Franchisee").', confidence=1.0

**Reasoning:** The excerpt explicitly mentions and defines the 'Agreement Date' as the date the Franchise Agreement is entered into, referring to its location on the cover page.

### 9. `cuad-00072` — Agreement Date

**Contract:** GOOSEHEADINSURANCE,INC_04_02_2018-EX-10.6-Franchise Agreement

**Excerpt:**
```
Exhibit 10.6

Goosehead Insurance Agency, LLC Franchise Agreement

Exhibit A Declarations Page 1 1.2 The "Approved Location" under this Agreement will be: . 2 4.1 You elect to pay the Initial Franchise Fee in one of the following ways: (check only one): ☐ In its entirety at the time you enter into this Agreement, in which case the amount of the Initial Franchise Fee shall be: ($ ). ☐ You shall pay a portion of the Initial Franchise Fee at the time you enter into this Agreement in the amount of ($ ), and shall pay the remaining portion of ($ ), plus interest, according to the terms of the 60...
```

**Gold:** present=False

**Prediction:** present=True, span='THIS FRANCHISE AGREEMENT (the "Agreement") is made and entered into as of the "Effective Date" that we have indicated on the signature page of this Agreement by and between:', confidence=1.0

**Reasoning:** The excerpt explicitly states that the Franchise Agreement is 'made and entered into as of the "Effective Date" that we have indicated on the signature page,' which directly defines the agreement date.

### 10. `cuad-00073` — Agreement Date

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

**Prediction:** present=True, span='dated 10 October 2000', confidence=1.0

**Reasoning:** The contract explicitly states 'dated 10 October 2000', which is the agreement date for this specific maintenance and support contract.

## correct_present_wrong_span (27 total)

### Worst 10 examples

### 1. `cuad-00130` — Cap On Liability

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

**Prediction:** present=True, span='FASC shall not be responsible for any error of judgment or mistake of law or for any loss suffered by the Advisor or any Account in connection with the matters to which this Agreement relates, except a loss resulting from willful malfeasance, bad faith or gross negligence on its part in the performance of its duties or from reckless disregard by it of its obligations and duties under this Agreement.', confidence=1.0
  - token Jaccard vs gold: 0.0938

**Reasoning:** Section 4(a) explicitly limits the liability of FASC by specifying the types of errors or losses for which it will not be responsible, except under conditions of willful malfeasance, bad faith, gross negligence, or reckless disregard. This directly addresses the concept of a cap or limitation on liability.

### 2. `cuad-00054` — Agreement Date

**Contract:** ASIANDRAGONGROUPINC_08_11_2005-EX-10.5-Reseller Agreement

**Excerpt:**
```
Exhibit 10.5

Reseller Agreement

This Agreement is made and entered into by and between 695014 B.C. Ltd. dba Galaxy Telecom, having a principal office at 200 - 375 Water Street, Vancouver, British Columbia V6B 5C6 Canada ("Galaxy") and Galaxy Telnet SRL, having a principal office at Aleea Malinului, Nr. 11, Bl. D, Scara C, Apt. 43, Constanta, Judetul Constanta, Romania ("Telnet") as of the 1s t day of June, 2004.

WHEREAS: Galaxy is a wholesale provider of Voice over Internet Protocol ("VoIP") telephony and related services and products. Telnet is a provider of VoIP telephony and related s...
```

**Gold:** present=True
  - spans: ['1s t day of June, 2004.']

**Prediction:** present=True, span='This Agreement is made and entered into by and between 695014 B.C. Ltd. dba Galaxy Telecom, having a principal office at 200 - 375 Water Street, Vancouver, British Columbia V6B 5C6 Canada ("Galaxy") and Galaxy Telnet SRL, having a principal office at Aleea Malinului, Nr. 11, Bl. D, Scara C, Apt. 43, Constanta, Judetul Constanta, Romania ("Telnet") as of the 1s t day of June, 2004.', confidence=1.0
  - token Jaccard vs gold: 0.1132

**Reasoning:** The excerpt explicitly states the date the agreement was made and entered into as 'the 1st day of June, 2004'. This directly addresses the agreement date.

### 3. `cuad-00057` — Agreement Date

**Contract:** MusclepharmCorp_20170208_10-KA_EX-10.38_9893581_EX-10.38_Co-Branding Agreement

**Excerpt:**
```
ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT   This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date") by and between Marine MP, LLC ("Lender"), for services of Arnold Schwarzenegger ("Endorser"), and Fitness Publications, Inc. ("Fitness") (collectively, Lender, Endorser, and Fitness are referred to as the "AS Parties") and MusclePharm Corporation with its principal place of business in Denver, Colorado and its subsidiaries, (collectively, "MusclePharm" or the "Company").   RECITALS   WHEREAS, the AS Parties have the rights necessary t...
```

**Gold:** present=True
  - spans: ['July 26, 2013']

**Prediction:** present=True, span='This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date")', confidence=1.0
  - token Jaccard vs gold: 0.1765

**Reasoning:** The excerpt explicitly states the date on which the agreement was entered into and defines it as the 'Effective Date', directly addressing the agreement date.

### 4. `cuad-00134` — Cap On Liability

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

**Prediction:** present=True, span='provided further that such fee shall in no event exceed RUB 50 000 000 (fifty million roubles)', confidence=1.0
  - token Jaccard vs gold: 0.1818

**Reasoning:** The excerpt explicitly states a maximum amount for a fee that one party would pay to the other, which functions as a cap on a specific financial obligation. This directly addresses the concept of a 'Cap On Liability'.

### 5. `cuad-00060` — Agreement Date

**Contract:** ArtaraTherapeuticsInc_20200110_8-K_EX-10.5_11943350_EX-10.5_License Agreement

**Excerpt:**
```
Exhibit 10.5 CERTAIN CONFIDENTIAL INFORMATION CONTAINED IN THIS DOCUMENT, MARKED BY […***…], HAS BEEN OMITTED BECAUSE ARTARA THERAPEUTICS, INC. HAS DETERMINED THE INFORMATION (I) IS NOT MATERIAL AND (II) WOULD LIKELY CAUSE COMPETITIVE HARM TO ARTARA THERAPEUTICS, INC. IF PUBLICLY DISCLOSED. SPONSORED RESEARCH AND LICENSE AGREEMENT This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date"), by and between ArTara, Inc. located at 1 Little West 12t h Street, New York, NY 10014 ("ArTara"), and The University of Iowa, located at c...
```

**Gold:** present=True
  - spans: ['November 28, 2018']

**Prediction:** present=True, span='This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date")', confidence=1.0
  - token Jaccard vs gold: 0.1875

**Reasoning:** The excerpt explicitly states the date on which the agreement was entered into, identifying it as 'November 28, 2018' and defining it as the 'Effective Date'.

### 6. `cuad-00052` — Agreement Date

**Contract:** EhaveInc_20190515_20-F_EX-4.44_11678816_EX-4.44_License Agreement_ Reseller Agreement

**Excerpt:**
```
Exhibit 4.44 THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018 is made BETWEEN: EHAVE, INC., a company incorporated under the laws of the Province of Ontario, Canada ("Ehave"); - and - COMPANION HEALTHCARE TECHNOLOGIES CORP, a company incorporated under the laws of the Province of Ontario ("CHT") RECITALS: A. Ehave has developed a software platform that provides an end-to-end patient management solution to healthcare professionals and provides that platform to users as a service. B. CHT has developed a business model to bring a similar service that Ehave provides using th...
```

**Gold:** present=True
  - spans: ['October 30, 2018']

**Prediction:** present=True, span='THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018', confidence=1.0
  - token Jaccard vs gold: 0.2500

**Reasoning:** The excerpt explicitly states the date of the agreement in the introductory paragraph. Additionally, the 'Effective Date' is defined as 'the date first written above', confirming the presence of the agreement date.

### 7. `cuad-00035` — Affiliate License-Licensor

**Contract:** ArconicRolledProductsCorp_20191217_10-12B_EX-2.7_11923804_EX-2.7_Trademark License Agreement

**Excerpt:**
```
Exhibit 2.7 FORM OF TRADEMARK LICENSE AGREEMENT THIS TRADEMARK LICENSE AGREEMENT (this "Agreement"), made and entered into as of the [ ] day of [ ], 2020 (the "Effective Date"), by and between ARCONIC INC., a corporation organized under the laws of Delaware ("Licensee") and ARCONIC ROLLED PRODUCTS CORP., a corporation organized under the laws of Delaware ("Licensor"). WHEREAS, Licensor and Licensee entered into a Separation and Distribution Agreement having an effective date of the [ ] day of [ ], 2020 ("Separation and Distribution Agreement"); unless specifically defined in this Agreement,...
```

**Gold:** present=True
  - spans: ['Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark: (i) for the Licensed Products as set forth on Schedule 2; and (ii) as set forth on Schedule 1, concerning agreements entered into by Licensee prior to the Effective Date ("Existing Agreements"). For the avoidance of doubt, Licensor also grants to Licensee and its subsidiaries and affiliates a non-exclusive, worldwide royalty-free license for continued use of the Licensed Mark for the production and sale of inventory containing the Licensed Mark applied to such products during the Transition Period as set forth in section 8.2 of the Separation and Distribution Agreement and in Schedule 2 of this Agreement.']

**Prediction:** present=True, span='Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark', confidence=1.0
  - token Jaccard vs gold: 0.2941

**Reasoning:** The excerpt explicitly states that the 'Licensor on behalf of itself and its Affiliates hereby grants to Licensee' the license, indicating that the Licensor's affiliates are involved in the granting of the license.

### 8. `cuad-00083` — Anti-Assignment

**Contract:** EtonPharmaceuticalsInc_20191114_10-Q_EX-10.1_11893941_EX-10.1_Development Agreement

**Excerpt:**
```
of the United State of America, without regard to its conflict of laws principles. To the extent that it may otherwise by applicable, the Parties hereby expressly agree to unconditionally waive and exclude from the operation of this Agreement the United Nations Convention on Contracts for the International Sale of Goods, concluded at Vienna, on 11 April 1980, as amended and as may be amended further from time to time. This Agreement has been negotiated and drafted by the Parties in the English language. Any translation into any other language shall not be an official version thereof. In the...
```

**Gold:** present=True
  - spans: ['The Parties shall not assign, encumber or otherwise transfer this Agreement or any part of it to any Third Party, without the prior written consent of the other Party.']

**Prediction:** present=True, span='15.8 Assignment. The terms and provisions hereof shall inure to the benefit of, and be binding upon the Parties and their respective successors and permitted assigns. The Parties shall not assign, encumber or otherwise transfer this Agreement or any part of it to any Third Party, without the prior written consent of the other Party. Notwithstanding the foregoing, each Party may assign the rights and obligations under this Agreement in whole, without consent of the other Party, to a Third Party or Affiliate in connection with the transfer or sale of all or substantially all of its business or in the event of a merger, consolidation or change in control provided that the assignee assumes in writing and becomes directly obligated to the other Party to perform all of the obligations of assignor under this Agreement.', confidence=1.0
  - token Jaccard vs gold: 0.3151

**Reasoning:** The excerpt contains a dedicated section titled 'Assignment' (15.8) which explicitly states that parties 'shall not assign, encumber or otherwise transfer this Agreement or any part of it to any Third Party, without the prior written consent of the other Party,' clearly indicating an anti-assignment provision.

### 9. `cuad-00036` — Affiliate License-Licensor

**Contract:** FIBROGENINC_10_01_2014-EX-10.11-COLLABORATION AGREEMENT

**Excerpt:**
```
rategy, such payment shall be increased by an additional U.S. $[ * ] for a total of U.S. $[ * ]   U.S. $[ * ]

2.   Upon the first [ * ] in the Astellas Territory for the [ * ]; provided, that in the event Astellas chooses the Bridging Strategy, such payment shall be increased by an additional U.S. $[ * ] for a total of U.S. $[ * ].   U.S. $[ * ]

3.   Upon the first [ * ] in the Astellas Territory for the [ * ]; provided, that in the event Astellas chooses the Bridging Strategy, such payment shall be increased by an additional U.S. $[ * ] for a total of U.S. $[ * ].   U.S. $[ * ]

4.



Up...
```

**Gold:** present=True
  - spans: ['FG shall have access to and the right to use for any purpose, any Data developed by or on behalf of Astellas or its Affiliates or Sublicensees in the course of the Development Program with respect to indications within the Field for Lead Compounds.']

**Prediction:** present=True, span='FG and Astellas may each provide copies or summaries of Data to its Affiliates and/or its permitted Sublicensees to the extent reasonably necessary for the development and commercialization of Lead Compounds in accordance with this Agreement, or in the case of FG of products other than Lead Compounds.', confidence=0.9
  - token Jaccard vs gold: 0.3333

**Reasoning:** The excerpt states that FG (the licensor) may provide data to its affiliates for development and commercialization. This provision grants its affiliates the right to use this data for specified purposes, which functions as a license from the licensor to its affiliates.

### 10. `cuad-00050` — Agreement Date

**Contract:** GopageCorp_20140221_10-K_EX-10.1_8432966_EX-10.1_Content License Agreement

**Excerpt:**
```
CONFIDENTIAL

  PSiTECHCORPORATION   WEBSITE CONTENT LICENSE AGREEMENT     This Content License Agreement ("Agreement"), dated as of Feb 10, 2014 (the "Effective Date"), is by and between PSiTech Corporation, a BVI Corporation, with offices located at 303, 3rdFl, St. Georges Bldg, 2 Ice House St, Central, Hong Kong("Licensor"), and Empirical Ventures, Inc., a Nevada corporation with offices located at 100, 40 Lake Bellevue Dr, Bellevue, WA("Licensee").     WHEREAS, Licensee owns, operates and controls the Licensee Site (as defined below);     WHEREAS, Licensor owns or otherwise has the righ...
```

**Gold:** present=True
  - spans: ['Feb 10, 2014']

**Prediction:** present=True, span='dated as of Feb 10, 2014 (the "Effective Date")', confidence=1.0
  - token Jaccard vs gold: 0.3333

**Reasoning:** The excerpt explicitly states the date the agreement is 'dated as of' and refers to it as the 'Effective Date', directly addressing the agreement date.

## hallucinated_span (12 total)

### Worst 10 examples

### 1. `cuad-00005` — Affiliate License-Licensee

**Contract:** ConformisInc_20191101_10-Q_EX-10.6_11861402_EX-10.6_Development Agreement

**Excerpt:**
```
riteria, then Stryker will provide Conformis with a written notice of rejection within the Acceptance Notification Period   describing the defect in view of the relevant Acceptance Criteria and including sufficient detail with respect to such Stryker testing   and testing results as Conformis reasonably requests ("Failure Notice"). Conformis shall have [**] (or such longer period of time   as may be agreed between the parties in good faith should the scope and complexity of the applicable Deliverable warrant some   longer period of time) ("Redelivery Period") following the date it receives ...
```

**Gold:** present=True
  - spans: ['Except as specifically provided in the Distribution Agreement, Conformis shall be prohibited from   developing or assisting another in developing, or causing another to develop, Patient-Specific Instrumentation for Off-The-Shelf   Knee Implants for any Third Party in the field of orthopedics until January 1, 2032 (or earlier, to the extent set forth in Section   2.3.3.4 or Section 2.3.5 of the Distribution Agreement), with the exception that Conformis (including any entity involved in a   Change of Control of Conformis, any such entity an "Acquirer"), may develop Patient-Specific Instrumentation for any Off-The-   Shelf Implants of Conformis, an Acquirer or any of their Affiliates.']

**Prediction:** present=True, span='Subject to the limitations set forth in this Agreement, the Joint IP may be used freely by either Party or its Affiliates and licensed to Third Parties by Conformis and its Affiliates, on the one hand, outside of the Buyer Field or by Stryker and its Affiliates, on the other hand, within the Buyer Field, in each case, without the consent of, or duty to account to or notify, the other Party', confidence=1.0

**Reasoning:** The excerpt explicitly states that 'the Joint IP may be used freely by either Party or its Affiliates' and can be 'licensed to Third Parties by Conformis and its Affiliates' or 'by Stryker and its Affiliates'. This grants the licensees (Conformis and Stryker) the right to use the IP through their affiliates and to have their affiliates participate in sublicensing to third parties, which directly addresses the 'Affiliate License-Licensee' category.

### 2. `cuad-00007` — Affiliate License-Licensee

**Contract:** BELLICUMPHARMACEUTICALS,INC_05_07_2019-EX-10.1-Supply Agreement

**Excerpt:**
```
The supply of the Miltenyi Products hereunder conveys to Bellicum the limited, non-exclusive, non-transferable (except as expressly provided herein, including as set forth in Article 17) right to use, and to permit its Subcontractors and Licensees to use the Miltenyi Products solely for Ex Vivo Cell Processing in the manufacture of Bellicum Products for use in the Field in the Territory (including for research, pre-clinical, clinical, regulatory and commercial purposes), in accordance with applicable Regulatory Authority requirements and approvals (including (to the extent applicable) any r...
```

**Gold:** present=True
  - spans: ["Subject to the terms of the Quality Agreement, if applicable, Miltenyi may, at its sole discretion, upon reasonable prior written notice to Bellicum, elect to have the Miltenyi Products, or any one of them or any component thereof, manufactured by an Affiliate of Miltenyi, and further may subcontract the manufacturing of Miltenyi Product or any component thereof, to a Subcontractor; provided that (i) Miltenyi shall reasonably take into account Bellicum's written concerns regarding proposed Affiliate(s) or Subcontractor(s); and (ii) Miltenyi shall be solely and fully responsible for the performance of all delegated and subcontracted activities by its Affiliates and Subcontractor(s), including compliance with the terms of this Agreement and the Quality Agreement (as applicable), and in no event shall any such delegation or subcontract release Miltenyi from any of its obligations under this Agreement. Miltenyi's Subcontractors and Affiliates for the manufacture and/or supply of Miltenyi Products will be listed in the Quality Agreement", "Bellicum shall have the right to transfer Miltenyi Product(s) purchased hereunder, or to request from Miltenyi, by notice in writing, that Miltenyi Deliver any Miltenyi Product(s) purchased hereunder to an Affiliate of Bellicum or a Subcontractor or Licensee of Bellicum Product designated by Bellicum, solely for the purpose of the Permitted Use, subject to the payment to Miltenyi of all additional expenses (if any) incurred by Miltenyi in connection with such provision and transfer of Miltenyi Product(s) to Bellicum's designee; and provided that in each case: (i) each Subcontractor or Licensee of Bellicum to whom Miltenyi Products are transferred shall be bound in writing by limitations and obligations that are consistent with the corresponding limitations and obligations imposed on Bellicum", 'The supply of the Miltenyi Products hereunder conveys to Bellicum the limited, non-exclusive, non-transferable (except as expressly provided herein, including as set forth in Article 17) right to use, and to permit its Subcontractors and Licensees to use the Miltenyi Products solely for Ex Vivo Cell Processing in the manufacture of Bellicum Products for use in the Field in the Territory (including for research, pre-clinical, clinical, regulatory and commercial purposes), in accordance with applicable Regulatory Authority requirements and approvals (including (to the extent applicable) any relevant clinical trial protocol, IND, and/or IRB approval pertaining to such Bellicum Products), in each case consistent with the terms and conditions of this Agreement and in accordance with Applicable Laws (the "Permitted Use"). Bellicum\'s Permitted Use of the Miltenyi Products shall be limited to the Designated Countries, subject to Section 2.3.', 'hereunder and under the Quality Agreement, as applicable; and (ii) notwithstanding the transfer of any Miltenyi Product purchased hereunder, Bellicum will nevertheless continue to remain fully and primarily responsible and liable to Miltenyi for payment of the Product Price and for the use of the Miltenyi Product by any Subcontractor and Licensee to whom a Miltenyi Product is transferred.']

**Prediction:** present=True, span="Bellicum shall have the right to transfer Miltenyi Product(s) purchased hereunder, or to request from Miltenyi, by notice in writing, that Miltenyi Deliver any Miltenyi Product(s) purchased hereunder to an Affiliate of Bellicum or a Subcontractor or Licensee of Bellicum Product designated by Bellicum, solely for the purpose of the Permitted Use, subject to the payment to Miltenyi of all additional expenses (if any) incurred by Miltenyi in connection with such provision and transfer of Miltenyi Product(s) to Bellicum's designee; and provided that in each case: (i) each Subcontractor or Licensee of Bellicum to whom Miltenyi Products are transferred shall be bound in writing by limitations and obligations that are consistent with the corresponding limitations and obligations imposed on Bellicum hereunder and under the Quality Agreement, as applicable; and (ii) notwithstanding the transfer of any Miltenyi Product purchased hereunder, Bellicum will nevertheless continue to remain fully and primarily responsible and liable to Miltenyi for payment of the Product Price and for the use of the Miltenyi Product by any Subcontractor and Licensee to whom a Miltenyi Product is transferred.", confidence=1.0

**Reasoning:** The excerpt explicitly grants Bellicum the right to transfer Miltenyi Products to an 'Affiliate of Bellicum or a Subcontractor or Licensee of Bellicum Product' for the Permitted Use, thereby extending the license to them. This directly addresses the 'Affiliate License-Licensee' category.

### 3. `cuad-00009` — Affiliate License-Licensee

**Contract:** AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_Maintenance Agreement

**Excerpt:**
```
upon successful transmission to the recipient's email account, if such Notice is sent in time to allow it to be accessible by the Addressee before the time allowed for giving such Notice expires, and a confirmation copy is sent by one of the other methods.

(c) The addresses and telephone numbers to which Notices may be given to the Addressees of either Party may be changed by written Notice given by such Party to the other pursuant to this Section.

3.27 Offshore Work Prohibited. None of the Services under this Agreement shall be performed or provided and no Information related to this Agr...
```

**Gold:** present=True
  - spans: ["Vendor hereby grants and promises to grant and have granted to AT&T and its Affiliates a royalty-free, nonexclusive, sublicensable, assignable, transferable, irrevocable, perpetual, world- wide license in and to any applicable Intellectual Property Rights of Vendor to use, copy, modify, distribute, display, perform, import, make, sell, offer to sell, and exploit (and have others do any of the foregoing on or for AT&T's or any of its customers' behalf or benefit) any Intellectual Property Rights of Vendor or any third party that are not included in Material or Paid-For Development but necessary to operate the Cell Sites or receive the full benefit of the Work."]

**Prediction:** present=True, span="Vendor hereby grants and promises to grant and have granted to AT&T and its Affiliates a royalty-free, nonexclusive, sublicensable, assignable, transferable, irrevocable, perpetual, world-wide license in and to any applicable Intellectual Property Rights of Vendor to use, copy, modify, distribute, display, perform, import, make, sell, offer to sell, and exploit (and have others do any of the foregoing on or for AT&T's or any of its customers' behalf or benefit) any Intellectual Property Rights of Vendor or any third party that are not included in Material or Paid-For Development but necessary to operate the Cell Sites or receive the full benefit of the Work.", confidence=1.0

**Reasoning:** The clause explicitly states that Vendor grants a license to 'AT&T and its Affiliates', indicating that the licensee's affiliates are also granted the license.

### 4. `cuad-00030` — Affiliate License-Licensor

**Contract:** GSITECHNOLOGYINC_11_16_2009-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT between SONY ELECTRONICS INC. and GSI TECHNOLOGY, INC.

**Excerpt:**
```
ined herein, including the following terms, which shall have the meanings set forth below:     1





     1.1 IP Agreement     The term "IP Agreement" means this Intellectual Property Agreement, including all attached Exhibits hereto, and any  amendments or supplements agreed to in writing and signed by SONY and PURCHASER.     1.2 Asset Purchase Agreement     The term "Asset Purchase Agreement" means the Asset Purchase Agreement dated August 28, 2009 between SONY and  PURCHASER to which this IP Agreement is attached as Exhibit F.     1.3 Effective Date     The term "Effective Date" means t...
```

**Gold:** present=True
  - spans: ['SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free  license (a) under the Licensed Patents to make, have made, use, offer to sell, sell, otherwise dispose of, and import any Competing Products  (including, without limitation, the SRAM Products); and (b) to use, reproduce, modify, prepare derivative works of, perform, display, and otherwise  practice and exploit in any manner any and all of the SRAM Intellectual Property in connection with the use and exploitation of the', 'Transferred Assets, and to make, have made, use, offer to sell, sell, otherwise dispose of, and import Competing Products (including, without  limitation, SRAM Products).']

**Prediction:** present=True, span='SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free license (a) under the Licensed Patents to make, have made, use, offer to sell, sell, otherwise dispose of, and import any Competing Products (including, without limitation, the SRAM Products)', confidence=1.0

**Reasoning:** The clause explicitly states that SONY, the licensor, grants the license 'on behalf of itself and its Affiliates,' indicating that the license extends from SONY's affiliates as well.

### 5. `cuad-00075` — Anti-Assignment

**Contract:** LOYALTYPOINTINC_11_16_2004-EX-10.2-RESELLER AGREEMENT

**Excerpt:**
```
No right or interest in this Agreement shall be assigned by                   Schoolpop without prior written permission of AEIS, which                   shall not be unreasonably withheld.

c.       This Agreement shall be deemed to have been made and executed                   in the State of Missouri and any dispute arising thereunder                   shall be resolved in accordance with the laws of the State of                   Missouri, without reference to its rules governing conflicts                   of law.

d.       Either party may terminate this Agreement with written notice ...
```

**Gold:** present=True
  - spans: ['No right or interest in this Agreement shall be assigned by                   Schoolpop without prior written permission of AEIS, which                   shall not be unreasonably withheld.', 'This Agreement (a) may not be assigned by Seller without the written          consent of AEIS, except to an entity controlling, controlled by or          under common control with Seller, provided, however, Schoolpop shall          remain liable for the obligations contained herein including the          attachments and Exhibits thereto, and (b) may be modified only by an          agreement in writing signed on behalf of AEIS by an executive officer.']

**Prediction:** present=True, span='This Agreement (a) may not be assigned by Seller without the written consent of AEIS, except to an entity controlling, controlled by or under common control with Seller, provided, however, Schoolpop shall remain liable for the obligations contained herein including the attachments and Exhibits thereto', confidence=1.0

**Reasoning:** The contract explicitly states that the agreement 'may not be assigned by Seller without the written consent of AEIS,' which is a direct anti-assignment provision, even with a specified exception.

### 6. `cuad-00082` — Anti-Assignment

**Contract:** KENTUCKYUTILITIESCO_03_25_2003-EX-10.65-TRANSPORTATION AGREEMENT

**Excerpt:**
```
bpart G, Part 284 of the FERC Regulations.   ARTICLE X - RESPONSIBILITY DURING TRANSPORTATION   Except as herein specified, the responsibility for gas during transportation shall be as stated in the General Terms and Conditions of Transporter's FERC Gas Tariff Volume No. 1.   ARTICLE XI - WARRANTIES   11.1 In addition to the warranties set forth in Article IX of the General Terms and Conditions of Transporter's FERC Gas Tariff, Shipper warrants the following:   (a) Shipper warrants that all upstream and downstream transportation arrangements are in place, or will be in place as of the reque...
```

**Gold:** present=True
  - spans: ["Otherwise, Shipper shall not assign this Agreement or any of its rights hereunder, except in accord with Article III, Section 11 of the General Terms and Conditions of Transporter's FERC Gas Tariff."]

**Prediction:** present=True, span="ARTICLE XIV - ASSIGNMENTS\n14.1 Either Party may assign or pledge this Agreement and all rights and obligations hereunder under the provisions of any mortgage, deed of trust, indenture, or other instrument which it has executed or may execute hereafter as security for indebtedness. Either Party may, without relieving itself of its obligation under this Agreement, assignment any of its rights hereunder to a company with which it is affiliated. Otherwise, Shipper shall not assign this Agreement or any of its rights hereunder, except in accord with Article III, Section 11 of the General Terms and Conditions of Transporter's FERC Gas Tariff.\n14.2 Any person which shall succeed by purchase, merger, or consolidation to the properties, substantially as an entirety, of either Party hereto shall be entitled to the rights and shall be subject to the obligations of its predecessor in interest under this Agreement.", confidence=1.0

**Reasoning:** Article XIV, explicitly titled 'ASSIGNMENTS', directly addresses the assignment of rights and obligations under the agreement. It specifies conditions under which assignments are permitted and, crucially, includes a restriction stating, 'Otherwise, Shipper shall not assign this Agreement or any of its rights hereunder, except in accord with Article III, Section 11 of the General Terms and Conditions of Transporter's FERC Gas Tariff,' which is a clear anti-assignment provision.

### 7. `cuad-00100` — Audit Rights

**Contract:** IVILLAGEINC_03_17_1999-EX-10.16-SPONSORSHIP AGREEMENT

**Excerpt:**
```
 work together in good faith to amend or terminate this Agreement.

2.       Promotion.

         A. During the Production Period, iVillage will design, develop, construct and host a Ford bridge site (the "Bridge Site") which shall include approximately [*] pages of content and other interactive material such as a travel planner or a car design feature. During the Promotion Period, iVillage will continue to host, maintain and update the Bridge Site. Upon receipt from iVillage of the proposed Bridge Site design and content, FMM shall have no more than five (5) business days in which to provi...
```

**Gold:** present=True
  - spans: ['All traffic reports shall be audited by the third party traffic auditor selected pursuant to Section 2.C.(ii).', 'During the Promotion Period, iVillage traffic shall be          audited by a third party traffic auditor listed on Exhibit A and          iVillage shall provide FMM with relevant reports on a biweekly basis.']

**Prediction:** present=True, span='During the Promotion Period, iVillage traffic shall be audited by a third party traffic auditor listed on Exhibit A and iVillage shall provide FMM with relevant reports on a biweekly basis.', confidence=1.0

**Reasoning:** The excerpt explicitly states that 'iVillage traffic shall be audited by a third party traffic auditor' and that 'All traffic reports shall be audited by the third party traffic auditor selected pursuant to Section 2.C.(ii),' clearly establishing audit rights.

### 8. `cuad-00107` — Audit Rights

**Contract:** SANDRIDGEENERGYINC_08_06_2009-EX-10.6-OPERATIONS AND MAINTENANCE AGREEMENT

**Excerpt:**
```
ative to Owner's business as are usually entered into records and books of account, and the same shall be supported by purchase  orders, invoices, payrolls or other customary or necessary records pertaining thereto. Owner's financial books and records shall be kept in  accordance with GAAP and shall be maintained on an accrual basis, and Owner shall provide Operator with the applicable income tax provisions.  The costs of any audit of Owner's books or records shall be borne by Owner.

6.2 Financial Statements.

     Operator shall deliver to Owner the financial statements of Owner prepared,...
```

**Gold:** present=True
  - spans: ["and records available for inspection by Owner's auditors, and (ii) making such copies of books and records as may be reasonably requested by  such auditors. In no event shall Owner's audits unreasonably interfere with Operator's operations.", "Owner shall have up until two years after the close of a Calendar Year in which to make an audit of Operator's records  for such Calendar Year.", "The costs of any audit of Owner's books or records shall be borne by Owner.", 'Owner shall engage an auditor for this purpose no later than 45 days after the  end of each fiscal year.', "Upon reasonable prior written notice to Operator, Owner shall have the right during normal business hours to audit or examine all books and  records of Operator to the extent they relate to Operator's performance hereunder as well as the relevant books of account of Operator's  contractors, relating to the performance of Operator's obligations under this Agreement. Operator shall cooperate with Owner's auditors by  (i) making the applicable books", 'Owner will be responsible for all costs of any  such audit; provided that if, in any audit, Owner discovers overpayments by Owner of at least $250,000 in the aggregate ("Material  Overpayment"), Operator will reimburse Owner for such Material Overpayment and all reasonable costs incurred by Owner in connection with  such audit ("Audit Costs").']

**Prediction:** present=True, span='6.5 Independent Audits.\n\n     Upon reasonable prior written notice to Operator, Owner shall have the right during normal business hours to audit or examine all books and  records of Operator to the extent they relate to Operator\'s performance hereunder as well as the relevant books of account of Operator\'s  contractors, relating to the performance of Operator\'s obligations under this Agreement. Operator shall cooperate with Owner\'s auditors by  (i) making the applicable books\n\n16\n\nand records available for inspection by Owner\'s auditors, and (ii) making such copies of books and records as may be reasonably requested by  such auditors. In no event shall Owner\'s audits unreasonably interfere with Operator\'s operations. Owner will be responsible for all costs of any  such audit; provided that if, in any audit, Owner discovers overpayments by Owner of at least $250,000 in the aggregate ("Material  Overpayment"), Operator will reimburse Owner for such Material Overpayment and all reasonable costs incurred by Owner in connection with  such audit ("Audit Costs"). Owner shall have up until two years after the close of a Calendar Year in which to make an audit of Operator\'s records  for such Calendar Year. Except for any bill or statement with respect to which an Adjustment Claim is made within the two-year audit period, the  bills and statements rendered for the Calendar Year prior to such two-year audit period shall be conclusively established as correct. An  "Adjustment Claim" shall mean a written claim by Owner to Operator requesting a refund or other financial adjustment in respect of any  overpayment by O', confidence=1.0

**Reasoning:** The excerpt includes a dedicated section titled '6.5 Independent Audits' which explicitly grants the Owner the right to audit the Operator's books and records, detailing the conditions, scope, and financial implications of such audits. This directly addresses the 'Audit Rights' category.

### 9. `cuad-00108` — Audit Rights

**Contract:** MRSFIELDSORIGINALCOOKIESINC_01_29_1998-EX-10-FRANCHISE AGREEMENT

**Excerpt:**
```
 its  financial  officer,  attesting  that (1) the reports are true and accurate,  (2) they are prepared in accordance with GAPP on a basis  consistent  with prior periods,  (3) they fully describe and completely disclose the information sought, and (4) the signer has made diligent efforts to ascertain the truth and completeness of the information.

         15.B.   MAINTENANCE OF RECORDS.

         Franchisee  agrees, at all times, he shall keep and maintain  adequate, accurate,  true, and proper records, books, reports, data, and accounts relative to the  franchise  in the English  langua...
```

**Gold:** present=True
  - spans: ["The audit will be conducted at the expense of Pretzel Time, provided that if an audit  disclosed an  understatement  of two percent (2%), as described above,  Franchisee will bear the cost of the audit,  including without limitation,  the charges of attorneys  and any  independent  accountants,  their travel   expenses,   room  and  board,   and   compensation  of  Pretzel  Time's representatives  and  independent  accountants.", "Franchisee shall fully cooperate with Pretzel Time's representatives and independent accountants hired by Pretzel Time to conduct any such inspection or audit.", 'Pretzel  Time or its  designee  shall have the right at any time during business  hours and without prior notice to  Franchisee,  to inspect,  audit and copy or the right to cause to be  inspected,  audited and copied,  the  business records,  bookkeeping and accounting  records,  sales and income tax records and returns and other records of the Franchised Business,  including but not limited to,  daily  cash  reports,  cash  receipts  journal  and  general  ledger,  cash disbursements  journal and weekly payroll register,  monthly bank statements and daily deposit slips and cancelled checks; tax returns,  supplier invoices, dated cash register tapes, weekly inventories, sales reports, financial statements and tax returns and the books and records of any  corporation or  partnership  which holds the Franchise  including the personal financial records and tax returns of the Franchisee during and after the term of the Franchise Agreement.', "To determine  whether  Franchisee  and the Unit are complying with this Agreement and with all Pretzel Time's  standards and operations as prescribed by Pretzel Time,  Pretzel Time or its designated agents shall have the right at any reasonable time and without prior notice to Franchisee to:\n\n         a.  Inspect the Unit;\n\n         b. Observe,  photograph  and video tape the Unit's  operations for such          consecutive or intermittent periods as Pretzel Time deems necessary;\n\n         c. Remove  samples of any  Products,  materials or supplies for testing and analysis;\n\n         d.  Interview personnel of the Unit;\n\n         e.  Interview customers of the Unit; and\n\n         f. Inspect and copy any books,  records and  documents  relating to the          operation  of the Unit.  Franchisee  agrees  to  cooperate  fully  with          Pretzel Time in connection with any such inspections, observations,  photographing,  video  taping,  Product  removal and  interviews. Franchisee  shall present to his customers  such comment or evaluation  forms as Pretzel Time periodically  prescribes and shall  participate  and/or request his customers  to  participate  in any surveys  performed by or on behalf of Pretzel Time.", 'Providing  that in no case will Franchisee be obligated to pay more than ten thousand dollars ($10,000) for such inspection  or audit  costs.']

**Prediction:** present=True, span="16.      AUDITS AND INSPECTIONS.\n\n         16.A.    AUDITS.\n\n         Pretzel  Time or its  designee  shall have the right at any time during business  hours and without prior notice to  Franchisee,  to inspect,  audit and copy or the right to cause to be  inspected,  audited and copied,  the  business records,  bookkeeping and accounting  records,  sales and income tax records and returns and other records of the Franchised Business,  including but not limited to,  daily  cash  reports,  cash  receipts  journal  and  general  ledger,  cash disbursements  journal and weekly payroll register,  monthly bank statements and daily deposit slips and cancelled checks; tax returns,  supplier invoices, dated cash register tapes, weekly inventories, sales reports, financial statements and tax returns and the books and records of any  corporation or  partnership  which holds the Franchise  including the personal financial records and tax returns of the Franchisee during and after the term of the Franchise Agreement.  Franchisee agrees to maintain on the premises  all sales and  operational  information  for four weeks.\n\n         Any such  inspection  or audit will take place at a time which will not interfere with  Franchisee's  normal business.  Franchisee shall fully cooperate with Pretzel Time's representatives and independent accountants hired by Pretzel Time to conduct any such inspection or audit.  If Pretzel Time deems  necessary, Franchisee shall deliver to Pretzel Time or its designated  agents copies of all bookkeeping  records not already in the  possession of Pretzel  Time,  including customer  records,  cash  register  tapes,  sales and  purchase  records and tax records,  to enable Pretzel Time or its representative or designee to adequately audit Franchisee's  gross sales.  Franchisee hereby waives any right to withhold tax records relative to the Franchise as privileged information. Each report and\n\n\n\nfinancial  statement  shall be signed and verified by  Franchisee  in the manner Pretzel Time prescribes.  Pretzel Time reserves the right to require  Franchisee to have audited or reviewed financial statements prepared on an annual basis.\n\n         In the event  that an audit  discloses  that  Franchisee's  actual  net revenues exceed  Franchisee's  reported net revenues by two percent (2%) or more for any thirty day  period,  Franchisee  is  obligated  to pay to Pretzel  Time, within  fifteen (15) days after receipt of the  inspection or audit report,  the royalty of seven percent (7%) and the  Advertising  Fund Fee of one percent (1%) of the amount of such  understatement  plus interest from the date such payments were originally due. The audit will be conducted at the expense of Pretzel Time, provided that if an audit  disclosed an  understatement  of two percent (2%), as described above,  Franchisee will bear the cost of the audit,  including without limitation,  the charges of attorneys  and any  independent  accountants,  their travel   expenses,   room  and  board,   and   compensation  of  Pretzel  Time's representatives  and  independent  accountants.  Providing  that in no case will Franchisee be obligated to pay more than ten thousand dollars ($10,000) for such inspection  or audit  costs.  The  foregoing  remedies  shall be in  addition to Pretzel Time's other remedies and rights under this Agreement or applicable law.", confidence=1.0

**Reasoning:** The excerpt contains a dedicated section titled 'AUDITS AND INSPECTIONS' and a subsection 'AUDITS' which explicitly grants Pretzel Time the right to inspect, audit, and copy the franchisee's business records. It also details the procedures, cooperation requirements, and financial implications of such audits.

### 10. `cuad-00126` — Cap On Liability

**Contract:** CORIOINC_07_20_2000-EX-10.5-LICENSE AND HOSTING AGREEMENT

**Excerpt:**
```
reement; and (d) the Software does not infringe any patent,         copyright, trade secret, trademark or other intellectual property rights         of a third party.

7.3     Product Warranty. Commerce One warrants that the Software and         MarketSite.net Service will perform in substantial accordance with the         Documentation, and the media on which the Software is distributed will         be free from defects in materials and workmanship under normal use, for         a period of sixty (60) days from the Effective Date, but in no event not         later than December 31, 1999 (th...
```

**Gold:** present=True
  - spans: ["The foregoing are         Corio's sole and exclusive remedies for breach of product warranty.", 'EXCEPT FOR LIABILITY         ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO EVENT SHALL EITHER         PARTY HAVE ANY LIABILITY TO THE OTHER PARTY FOR ANY LOST PROFITS OR         COSTS OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, OR FOR ANY         INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES HOWEVER CAUSED AND UNDER ANY         THEORY OF LIABILITY AND WHETHER OR NOT SUCH PARTY HAS BEEN ADVISED OF         THE POSSIBILITY OF SUCH DAMAGE.', "EXCEPT FOR LIABILITY ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO         EVENT SHALL EITHER PARTY'S LIABILITY ARISING OUT OF THIS AGREEMENT OR         THE USE OR PERFORMANCE OF THE SOFTWARE EXCEED THE TOTAL AMOUNT ACTUALLY         PAID BY CORIO HEREUNDER FOR THE TRANSACTION WHICH THE LIABILITY RELATES         TO DURING THE TWELVE (12) MONTHS IMMEDIATELY PRIOR TO THE FILING OF THE         CAUSE OF ACTION TO WHICH THE LIABILITY RELATES. EXCEPT FOR LIABILITY         ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO EVENT SHALL EITHER         PARTY HAVE ANY LIABILITY TO THE OTHER PARTY FOR ANY LOST PROFITS OR         COSTS OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, OR FOR ANY         INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES HOWEVER CAUSED AND UNDER ANY         THEORY OF LIABILITY AND WHETHER OR NOT SUCH PARTY HAS BEEN ADVISED OF         THE POSSIBILITY OF SUCH DAMAGE."]

**Prediction:** present=True, span="EXCEPT FOR LIABILITY ARISING UNDER SECTION 8 OF THIS AGREEMENT, IN NO EVENT SHALL EITHER PARTY'S LIABILITY ARISING OUT OF THIS AGREEMENT OR THE USE OR PERFORMANCE OF THE SOFTWARE EXCEED THE TOTAL AMOUNT ACTUALLY PAID BY CORIO HEREUNDER FOR THE TRANSACTION WHICH THE LIABILITY RELATES TO DURING THE TWELVE (12) MONTHS IMMEDIATELY PRIOR TO THE FILING OF THE CAUSE OF ACTION TO WHICH THE LIABILITY RELATES.", confidence=1.0

**Reasoning:** Section 9, titled 'LIMITATION OF LIABILITY', explicitly states that 'in no event shall either party's liability... exceed the total amount actually paid by Corio hereunder for the transaction... during the twelve (12) months immediately prior to the filing of the cause of action'. This language directly establishes a monetary cap on liability.

## parse_fail (0 total)

_No errors in this bucket._
