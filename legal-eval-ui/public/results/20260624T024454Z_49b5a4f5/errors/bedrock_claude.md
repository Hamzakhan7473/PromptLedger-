# Error report — `bedrock_claude`

## Summary (counts per bucket per category)

| Bucket | Category | Count |
|--------|----------|-------|
| missed_present | Affiliate License-Licensor | 2 |
| missed_present | Cap On Liability | 3 |
| false_present | Affiliate License-Licensee | 2 |
| false_present | Affiliate License-Licensor | 1 |
| false_present | Agreement Date | 10 |
| correct_present_wrong_span | Affiliate License-Licensee | 3 |
| correct_present_wrong_span | Affiliate License-Licensor | 4 |
| correct_present_wrong_span | Agreement Date | 10 |
| correct_present_wrong_span | Anti-Assignment | 2 |
| correct_present_wrong_span | Audit Rights | 5 |
| correct_present_wrong_span | Cap On Liability | 3 |
| hallucinated_span | Affiliate License-Licensee | 1 |
| hallucinated_span | Affiliate License-Licensor | 1 |
| hallucinated_span | Anti-Assignment | 3 |
| hallucinated_span | Audit Rights | 3 |
| hallucinated_span | Cap On Liability | 1 |
| parse_fail | _none_ | 0 |

## missed_present (5 total)

### Worst 5 examples

### 1. `cuad-00128` — Cap On Liability

**Contract:** CytodynInc_20200109_10-Q_EX-10.5_11941634_EX-10.5_License Agreement

**Excerpt:**
```
itee shall have reasonably concluded, based upon a written opinion from outside legal counsel, that there is a conflict of interest between the Indemnifying Party and the Indemnitee in the defense of such Claim, in which case the Indemnifying Party shall pay the fees and expenses of one (1) law firm serving as counsel for the Indemnitee in relation to such Third Party Claim. (c) Cooperation. The Indemnitee shall reasonably cooperate with the Indemnifying Party and its legal representatives in the investigation and defense of any Claim. The Indemnifying Party shall keep the Indemnitee inform...
```

**Gold:** present=True
  - spans: ["EXCEPT FOR A PARTY'S OBLIGATIONS SET FORTH IN THIS ARTICLE 13, AND ANY BREACH OF ARTICLE 10 (CONFIDENTIALITY), IN NO EVENT WILL EITHER PARTY BE LIABLE TO THE OTHER PARTY (OR THE OTHER PARTY'S AFFILIATES OR SUBLICENSEES) IN CONNECTION WITH THIS AGREEMENT FOR LOST REVENUE, LOST PROFITS, LOST ROYALTIES, LOST SAVINGS, LOSS OF USE, DAMAGE TO GOODWILL, OR ANY CONSEQUENTIAL, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR INDIRECT DAMAGES IN CONNECTION WITH THIS AGREEMENT, HOWEVER CAUSED, UNDER ANY THEORY OF LIABILITY, INCLUDING CONTRACT, NEGLIGENCE, OR STRICT LIABILITY, EVEN IF THAT PARTY HAS BEEN PLACED ON NOTICE OF THE POSSIBILITY OF SUCH DAMAGES.", "FOR CLARITY AND NOTWITHSTANDING THE PROVISIONS OF THE FIRST SENTENCE OF THIS SECTION 13.5, ROYALTIES AND MILESTONES PAYABLE TO CYTODYN IN CONNECTION WITH VYERA'S COMMERCIALIZATION OF LICENSED PRODUCTS IN ACCORDANCE WITH THE TERMS OF THIS AGREEMENT COULD CONSTITUTE DIRECT DAMAGES TO THE EXTENT AWARDED IN ACCORDANCE WITH ARTICLE 12."]

**Prediction:** present=False, span=None, confidence=0.85

**Reasoning:** The excerpt contains a Limitation of Liability clause (Section 13.5) that excludes certain types of damages (consequential, incidental, punitive, etc.), but it does not impose a monetary cap or ceiling on the total amount of liability either party may face. A "Cap on Liability" clause specifically limits the maximum dollar amount recoverable, which is absent here.

### 2. `cuad-00129` — Cap On Liability

**Contract:** EtonPharmaceuticalsInc_20191114_10-Q_EX-10.1_11893941_EX-10.1_Development Agreement

**Excerpt:**
```
tively, "Aucta Indemnified Parties") harmless from and against any and all Losses arising out of or resulting from any Third Party Claims made or suits brought against Aucta Indemnified Parties which arise or result from (i) ETON's material breach of any of its representations, warranties or covenants set forth in this Agreement, or any of its obligations hereunder; (ii) ETON's marketing, distribution, or sale of any Product on or after the Effective Date, including, without limitation, any Claim for personal injury or death, to the extent such Third Party Claims arise from the period time ...
```

**Gold:** present=True
  - spans: ['NOTWITHSTANDING ANYTHING TO THE CONTRARY HEREIN, NEITHER PARTY SHALL BE LIABLE FOR ANY INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL OR EXEMPLARY DAMAGES, WHETHER FORESEEABLE OR NOT, THAT ARE IN ANY WAY RELATED TO THIS AGREEMENT.']

**Prediction:** present=False, span=None, confidence=0.85

**Reasoning:** The excerpt contains a limitation of liability clause (Section 14.1) that excludes indirect, special, incidental, consequential, or exemplary damages, but it does not impose a monetary cap or ceiling on the total amount of liability. A "Cap On Liability" clause specifically limits the maximum dollar amount recoverable, which is not present here.

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

**Prediction:** present=False, span=None, confidence=0.85

**Reasoning:** While Section 4 addresses limitation of liability and indemnification, it does not impose a specific monetary cap or ceiling on the amount of liability either party may face. The limitation language only carves out liability for willful malfeasance, bad faith, gross negligence, or reckless disregard, and Section 4(c) limits obligations to the party's own assets — but neither provision sets a quantitative cap on damages or liability.

### 4. `cuad-00026` — Affiliate License-Licensor

**Contract:** TomOnlineInc_20060501_20-F_EX-4.46_749700_EX-4.46_Co-Branding Agreement

**Excerpt:**
```
 applicable fees, scope of work and appropriate project timelines, as well as any requirements, considerations, or objectives which differ from the general provisions of this Agreement. If any provision of a Statement of Work conflicts with any of the terms and conditions of this Agreement, the provisions of this Agreement shall take precedence.

  1.48 "Subsidiary" and "Holding Company" each have the meaning set out in Section 736 of the Companies Act 1985 of the United Kingdom.

  1.49 "Term" shall have the meaning set forth in Section 6.1 herein.

  1.50 "Third Party Affiliate Partner" s...
```

**Gold:** present=True
  - spans: ['Skype further agrees that in the event that, prior to such time as the Company-Skype Branded Application is updated or upgraded to include the Mobile Technology, Skype or any of its Affiliates makes available to Skype users a new software product which allows access to services available through the Skype Software but on or through mobile communication devices (but in any event excluding Skype Zones), it will license that software product to the Company and Online BVI on the terms and conditions set forth in this Agreement with respect to the Skype Software and the Company-Skype Branded Application customized therefrom, and references to the Skype Software in this Agreement shall be deemed to include such software product.']

**Prediction:** present=False, span=None, confidence=0.75

**Reasoning:** The excerpt does not contain a clause where the licensor grants a license specifically to or through an affiliate. While affiliates are mentioned (e.g., "Skype or any of its Affiliates"), the licensing language in Section 2.1 is directed at the Company and Online BVI directly, not structured as an affiliate license grant from a licensor to its affiliate. There is no substantive provision addressing the licensor's right to license through or to affiliates as a distinct clause category.

### 5. `cuad-00031` — Affiliate License-Licensor

**Contract:** ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
alf of ENERGOUS after the Effective Date that is not a Product Update; provided, however, that "New Products" exclude any product developed by a successor or acquirer of ENERGOUS.   1.18  "Patent" means any United States or foreign patent or patent application, including any provisional application, continuation, continuation-in-part, divisional, registration, confirmation, revalidation, reissue, PCT application, patent term extension, supplementary protection certificate, and utility model, as well as all foreign counterparts of any of the foregoing, and related extensions or restorations ...
```

**Gold:** present=True
  - spans: ['Subject to the restrictions set out in Section 2.2, ENERGOUS hereby grants to DIALOG a non-exclusive (subject to Section 2.5), irrevocable, worldwide, sub-licensable (solely in accordance with Section 2.4), royalty-bearing license during the Term under all Product IP to:   (a) repackage or have repackaged the Product Die into various package formats or layouts, and to integrate the Product Die into MCMs, which may incorporate DIALOG or third party intellectual property (such repackaged Product Die, MCMs and Products, are individually and/or collectively referred to as the "Licensed Products");   (b) have the Licensed Products manufactured, tested and packaged by Manufacturing Subcontractors;   (c) Sell, offer for Sale, import, export and support the Licensed Products, including without limitation, providing system design, troubleshooting and failure analysis support for DIALOG\'s customers and their customers;   (d) use and modify the Tooling and Documentation for the purposes of paragraphs (a) to (d) of this Section 2.1.', '"Product IP" means (a) all Intellectual Property Rights in and to the Products, including all Product Updates, (b) any other Inventions and work products created or developed in connection with research and development or manufacturing efforts relating to the Products, including all Intellectual Property Rights therein and (c) all Intellectual Property Rights in and to the Mask Sets and Tooling, in each of the foregoing cases, that are owned or controlled by ENERGOUS, its Affiliates or any successor or assign.']

**Prediction:** present=False, span=None, confidence=0.75

**Reasoning:** The excerpt grants a license from ENERGOUS to DIALOG and references ENERGOUS' Affiliates in the context of ownership of Product IP (Section 1.23), but there is no clause that specifically grants DIALOG's affiliates the right to use the licensed IP, nor does it grant rights to ENERGOUS' affiliates as licensors. The "Affiliate License-Licensor" category typically refers to a provision where the licensor's affiliates are also granted or extend license rights, which is not substantively addressed here.

## false_present (13 total)

### Worst 10 examples

### 1. `cuad-00065` — Agreement Date

**Contract:** IOVANCEBIOTHERAPEUTICS,INC_08_03_2017-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
Exhibit 10.1   Text Marked By [* * *] Has Been Omitted Pursuant To A Request For Confidential Treatment And Was Filed Separately With The Securities And Exchange Commission.   STRATEGIC ALLIANCE AGREEMENT Effective Date: April 17, 2017   THIS STRATEGIC ALLIANCE AGREEMENT (this "Agreement"), is entered into by and between Lion Biotechnologies, Inc., with a place of business located at 999 Skyway Road, Suite 150, San Carlos, CA 94070 ("LBIO"), and The University of Texas M. D. Anderson Cancer Center, with a place of business located at 1515 Holcombe Blvd., Houston, TX 77030 ("MD Anderson"), a...
```

**Gold:** present=False

**Prediction:** present=True, span='Effective Date: April 17, 2017', confidence=1.0

**Reasoning:** The excerpt explicitly states the effective date of the agreement at the very beginning, identifying "Effective Date: April 17, 2017" and further referencing it as "the date set forth above (the 'Effective Date')" in the body of the agreement.

### 2. `cuad-00073` — Agreement Date

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

**Prediction:** present=True, span='dated 10 October 2000', confidence=0.97

**Reasoning:** The excerpt explicitly states the contract is "dated 10 October 2000," which is a clear agreement date. It also references the original contract made effective on 06 April 1998, further supporting the presence of date-related language.

### 3. `cuad-00063` — Agreement Date

**Contract:** PHLVARIABLEINSURANCECOCT_08_17_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT

**Excerpt:**
```
STRATEGIC ALLIANCE AGREEMENT

This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the  "Effective Date"), by and among PHL VARIABLE INSURANCE COMPANY ("PHLVIC"), PHOENIX LIFE INSURANCE COMPANY, ("PLIC"  and, together with PHLVIC, "PHL Variable"), PHOENIX EQUITY PLANNING CORPORATION ("PEPCO" and, together with PHLVIC and PLIC,  the "PHL Parties"), and INVESTORS CAPITAL CORPORATION ("ICC"). Except as otherwise defined, capitalized terms used herein shall have  the meanings given to them in Section 1 Definitions, be...
```

**Gold:** present=False

**Prediction:** present=True, span='This agreement ("Agreement"), is entered into as of the date on which the Registration Statement is declared effective by the SEC (the "Effective Date"), by and among PHL VARIABLE INSURANCE COMPANY ("PHLVIC"), PHOENIX LIFE INSURANCE COMPANY, ("PLIC" and, together with PHLVIC, "PHL Variable"), PHOENIX EQUITY PLANNING CORPORATION ("PEPCO" and, together with PHLVIC and PLIC, the "PHL Parties"), and INVESTORS CAPITAL CORPORATION ("ICC").', confidence=0.95

**Reasoning:** The excerpt defines the "Effective Date" as "the date on which the Registration Statement is declared effective by the SEC," which is the agreement date. This is substantively addressed in the introductory paragraph and further defined in Section 1.16.

### 4. `cuad-00069` — Agreement Date

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

**Prediction:** present=True, span='Effective Dates: September 1, 2006, August 31, 2007', confidence=0.95

**Reasoning:** The excerpt explicitly states the effective dates of the agreement as "September 1, 2006, August 31, 2007," which directly addresses the Agreement Date clause category. This defines the temporal scope and start/end dates of the agreement.

### 5. `cuad-00020` — Affiliate License-Licensee

**Contract:** EdietsComInc_20001030_10QSB_EX-10.4_2606646_EX-10.4_Co-Branding Agreement

**Excerpt:**
```
EXHIBIT 10.4

                              CO-BRANDING AGREEMENT

         THIS CO-BRANDING AGREEMENT (the "Agreement") is made as of May 22, 2000 (the "Effective Date"), by and between WOMEN.COM NETWORKS, INC., a Delaware corporation having a place of business at 1820 Gateway Drive Suite 150, San Mateo, CA 94404 ("Women.com"), and EDIETS.COM, INC., a Delaware corporation, having its principal place of business at 3467 West Hillsboro Boulevard, Suite 2, Deerfield Beach, Florida 33442 ("eDiets").

         WHEREAS, eDiets maintains a site on the Internet, currently located at http://www.eDi...
```

**Gold:** present=False

**Prediction:** present=True, span='eDiets hereby grants to Women.com, subject to the terms and conditions of this Agreement, a non-exclusive, nontransferable, worldwide, royalty-free license to use, copy, reproduce and display the editorial content and other data, branding and other identification provided by eDiets to Women.com in connection with this Agreement (the "eDiets Content") on the Women.com Sites: (i) for publication in the Diet Center and elsewhere throughout the Women.com Sites; (ii) for the promotion of eDiets and the Diet Center on the Women.com Sites and in collateral advertising materials; and (iii) for such other purposes as are consistent with or otherwise authorized under this Agreement.', confidence=0.92

**Reasoning:** Section 2.1 explicitly grants Women.com a license to use eDiets content, making Women.com the licensee in an affiliate/co-branding relationship. The license is non-exclusive, nontransferable, worldwide, and royalty-free, covering use, copying, reproduction, and display of eDiets Content on the Women.com Sites — this is characteristic of an affiliate license-licensee clause.

### 6. `cuad-00016` — Affiliate License-Licensee

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

**Prediction:** present=True, span='Diplomat agrees to pay KI, Inc. as royalty a sum equal to  % of the net wholesale volume of the products covered by this Agreement by Diplomat and its affiliated, associated, or subsidiary companies.', confidence=0.85

**Reasoning:** The agreement grants Diplomat a license to use KI's name and likeness, and the royalty clause explicitly includes sales by "Diplomat and its affiliated, associated, or subsidiary companies" in the royalty calculation. This indicates the license extends to Diplomat's affiliates, addressing the Affiliate License-Licensee category.

### 7. `cuad-00066` — Agreement Date

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

**Prediction:** present=True, span='THIS FRANCHISE DEVELOPMENT AGREEMENT ("Agreement") dated for identification purposes only as of _____________________, is made and entered into by and between EL POLLO LOCO, INC., a Delaware corporation', confidence=0.85

**Reasoning:** The excerpt contains a placeholder for the agreement date in two locations, indicating the contract structure includes an Agreement Date clause. While the actual date is blank (to be filled in), the field is explicitly present in the document header and the recital section.

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

**Prediction:** present=True, span='This Agreement is entered into with effect as of the Effective Date (as defined below)', confidence=0.85

**Reasoning:** The excerpt references an "Effective Date" as the operative date of the agreement, stating "This Agreement is entered into with effect as of the Effective Date (as defined below)." While the specific calendar date is not spelled out in this excerpt, the agreement date concept is substantively addressed through the Effective Date definition and its reference in Section 1.26 of the Table of Contents.

### 9. `cuad-00071` — Agreement Date

**Contract:** PfHospitalityGroupInc_20150923_10-12G_EX-10.1_9266710_EX-10.1_Franchise Agreement1

**Excerpt:**
```
FORM OF FRANCHISE AGREEMENT Location of the Premises: Agreement Date Franchisee Business Address

Type of Legal Entity (if applicable) State in which entity organized (if applicable) Shareholder / Partner / Member Name Ownership Percentage % (the "Operating Principal") % % % %

Source: PF HOSPITALITY GROUP INC., 10-12G, 9/23/2015





TABLE OF CONTENTS SECTION PAGE 1. RIGHTS GRANTED 2 2. TERM; SUCCESSOR FRANCHISE AGREEMENTS 4 3. FEES 4 4. OPENING DEADLINE 6 5. TRAINING 10 6. OPERATIONS 11 7. PROPRIETARY MARKS 18 8. BUSINESS RECORDS AND REPORTING 19 9. MARKETING FUND AND ADVERTISING 21 10. T...
```

**Gold:** present=False

**Prediction:** present=True, span='This Franchise Agreement (the "Agreement") is entered into as of the Agreement Date shown on the cover page between Pizza Fusion Holding, Inc., a Florida corporation, and the individual or legal entity identified on the cover page ("Franchisee").', confidence=0.85

**Reasoning:** The excerpt references "Agreement Date" on the cover page as a field to be filled in, and the body of the agreement states it is "entered into as of the Agreement Date shown on the cover page." While no specific date value is provided (this is a form agreement), the Agreement Date clause is substantively addressed as a defined reference point for the contract's execution date.

### 10. `cuad-00072` — Agreement Date

**Contract:** GOOSEHEADINSURANCE,INC_04_02_2018-EX-10.6-Franchise Agreement

**Excerpt:**
```
Exhibit 10.6

Goosehead Insurance Agency, LLC Franchise Agreement

Exhibit A Declarations Page 1 1.2 The "Approved Location" under this Agreement will be: . 2 4.1 You elect to pay the Initial Franchise Fee in one of the following ways: (check only one): ☐ In its entirety at the time you enter into this Agreement, in which case the amount of the Initial Franchise Fee shall be: ($ ). ☐ You shall pay a portion of the Initial Franchise Fee at the time you enter into this Agreement in the amount of ($ ), and shall pay the remaining portion of ($ ), plus interest, according to the terms of the 60...
```

**Gold:** present=False

**Prediction:** present=True, span='THIS FRANCHISE AGREEMENT (the "Agreement") is made and entered into as of the "Effective Date" that we have indicated on the signature page of this Agreement', confidence=0.85

**Reasoning:** The excerpt references an "Effective Date" on the signature page as the date the Agreement is made and entered into, which constitutes agreement date language. While the actual date is not filled in, the mechanism for establishing the agreement date is clearly defined.

## correct_present_wrong_span (27 total)

### Worst 10 examples

### 1. `cuad-00060` — Agreement Date

**Contract:** ArtaraTherapeuticsInc_20200110_8-K_EX-10.5_11943350_EX-10.5_License Agreement

**Excerpt:**
```
Exhibit 10.5 CERTAIN CONFIDENTIAL INFORMATION CONTAINED IN THIS DOCUMENT, MARKED BY […***…], HAS BEEN OMITTED BECAUSE ARTARA THERAPEUTICS, INC. HAS DETERMINED THE INFORMATION (I) IS NOT MATERIAL AND (II) WOULD LIKELY CAUSE COMPETITIVE HARM TO ARTARA THERAPEUTICS, INC. IF PUBLICLY DISCLOSED. SPONSORED RESEARCH AND LICENSE AGREEMENT This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date"), by and between ArTara, Inc. located at 1 Little West 12t h Street, New York, NY 10014 ("ArTara"), and The University of Iowa, located at c...
```

**Gold:** present=True
  - spans: ['November 28, 2018']

**Prediction:** present=True, span='This Sponsored Research and License Agreement (this "Agreement") is entered into on November 28, 2018 (the "Effective Date"), by and between ArTara, Inc. located at 1 Little West 12t h Street, New York, NY 10014 ("ArTara"), and The University of Iowa, located at c/o Division of Sponsored Programs, 2 Gilmore Hall, Iowa City, IA 52242 ("University").', confidence=1.0
  - token Jaccard vs gold: 0.0667

**Reasoning:** The excerpt explicitly states the date on which the agreement was entered into, identifying it as the "Effective Date." This directly addresses the Agreement Date clause category.

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

**Prediction:** present=True, span='This Amendment is entered into effective October 1,1996 ("Amendment Date") by and between NETGEAR, Inc. ("NETGEAR"), a wholly owned subsidiary of Bay Networks, Inc., and Ingram Micro ("Distributor") acting on behalf of itself and its affiliates.\n\nNETGEAR and Distributor having previously entered into a Distributor Agreement ("Agreement") with an Effective Date of March 1,1996', confidence=0.98
  - token Jaccard vs gold: 0.0811

**Reasoning:** The excerpt contains multiple explicit agreement dates. The original Distributor Agreement has an Effective Date of March 1, 1996; the first Amendment is entered into effective October 1, 1996; and Amendment #2 is entered into on July 15, 1998. These are all substantive references to agreement dates.

### 3. `cuad-00055` — Agreement Date

**Contract:** SPIENERGYCO,LTD_07_10_2014-EX-10-Cooperation Agreement of 50MWp Photovoltaic Grid-connected Power Generation Project in Yangqiao of~1

**Excerpt:**
```
Exhibit 10.47   Cooperation Agreement of 50MWp Photovoltaic Grid-connected Power Generation Project in Yangqiao of Fenyi County   Party A: People's Government of Fenyi County Party B: Xinyu Xinwei New Energy Co., Ltd.   Party A welcomes and supports Party B to invest and develop new energy project in Fenyi County, and Party B is willing to invest and build 50MWp photovoltaic grid-connected power generation project in Fenyi County; both parties, in the principle of equality, mutual benefits, win-win cooperation and solid progress, reach the following cooperation agreement as for relevant mat...
```

**Gold:** present=True
  - spans: ['June 25, 2014']

**Prediction:** present=True, span="Party A: People's Government of Fenyi County (seal) Rao Cheng (signature) June 25, 2014   Party B: Xinyu Xinwei New Energy Co., Ltd. (seal) Xiahou Min (signature) June 25, 2014", confidence=0.99
  - token Jaccard vs gold: 0.1250

**Reasoning:** The excerpt explicitly states the date on which both parties signed the agreement. Both Party A and Party B's signatures are dated "June 25, 2014," which constitutes the agreement date.

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

**Prediction:** present=True, span='such fee shall in no event exceed RUB 50 000 000 (fifty million roubles)', confidence=0.92
  - token Jaccard vs gold: 0.1477

**Reasoning:** Clause 4.1 contains an explicit monetary cap on liability, stating that a termination fee "shall in no event exceed RUB 50 000 000 (fifty million roubles)," which directly limits the maximum financial exposure of QIWI in the event it terminates its settlement obligation.

### 5. `cuad-00103` — Audit Rights

**Contract:** DovaPharmaceuticalsInc_20181108_10-Q_EX-10.2_11414857_EX-10.2_Promotion Agreement

**Excerpt:**
```
CEUTICALS INC., 10-Q, 11/8/2018





primary or a secondary specialty designation of Gastroenterology, Colorectal Surgery or Proctology and that do not have either a primary or a secondary specialty designation of Hepatology shall be deemed to be in the Specialty.

6.5.4 The process described in this Section 6.5 shall be repeated for each Calendar Quarter of the Term; provided, however, that, pursuant to the process described above, if Dova's Third Party Data Source has confirmed that a Target Professional's primary specialty designation should be or should remain Gastroenterology, Colorect...
```

**Gold:** present=True
  - spans: ['Dova shall have the right, at its own expense, during normal business hours and upon reasonable prior notice, through a certified public accounting firm or other auditor selected by Dova and reasonably acceptable to Valeant and upon execution of a confidentiality agreement reasonably satisfactory to Valeant in form and substance, to inspect and audit the applicable records and books maintained by Valeant relating to the Valeant Activities for purposes of verifying Valeant\'s compliance with the terms of this Agreement, provided that (i) such examination shall not take place more often than once per every twelve (12) months during the Term and once during the one (1) year period following the end of the Term, and (ii) such examination shall not cover a period of time that has previously been audited; provided that Dova shall have the right to conduct additional "for cause" audits to the extent necessary to address significant compliance problems relating to Valeant\'s obligations hereunder or in response to any inquiry, inspection, investigation or other requirements of a Government Authority in the Territory relating to the Valeant Activities.', 'Valeant shall bear the out-of-pocket costs and expenses incurred by the Parties in connection with any such inspection or audit, unless the audit shows an undisputed under-reporting or underpayment for that audited period in excess of [***] of the amounts properly determined, in which case, Dova shall reimburse Valeant for its audit fees and reasonable out-of-pocket expenses in connection with said audit, which reimbursement shall be due and payable within [***] of receiving appropriate invoices and other support for such audit-related costs.', 'Valeant shall have the right, at its own expense, during normal business hours and upon reasonable prior notice, through certified public accounting firm or other auditor selected by Valeant and reasonably acceptable to Dova and upon execution of a confidentiality agreement reasonably satisfactory to Dova in form and substance, to inspect and audit the applicable records and books maintained by Dova for purposes of verifying Dova\'s payment obligations within this Agreement, including the applicable records and books of account maintained by Dova, or any Affiliate, as applicable, with respect to Net Sales in order to confirm the accuracy and completeness of such records and books of account and all payments hereunder; provided, however, that (i) such examination shall not take place more often than once per every twelve (12) months during the Term and once during the one (1) year period following the end of the Term, and (ii) such examination shall not cover a period of time that has previously been audited; provided that Valeant shall have the right to conduct additional "for cause" audits to the extent necessary to address significant problems relating to Dova\'s payment obligations hereunder.', "Where necessary, on reasonable request, Dova's audit rights shall include interviewing Sales Representatives and other employees of Valeant.", 'Dova shall bear the out-of-pocket costs and expenses incurred by the Parties in connection with any such inspection or audit, unless the audit shows an undisputed over- payment for that audited period in excess of [***] of the amounts properly determined, in which case, Valeant shall reimburse Dova for its audit fees and reasonable out-of-pocket expenses in connection with said audit, which reimbursement shall be due and payable within [***] of receiving appropriate invoices and other support for such audit-related costs.']

**Prediction:** present=True, span="ARTICLE 7  AUDIT RIGHTS\n\n7.1 Recordkeeping. Each Party shall maintain complete and accurate books and records in sufficient detail, in accordance with GAAP (to the extent applicable and in accordance with the Agreement) and all Applicable Law, to enable verification of the performance of such Party's obligations under this Agreement and any payments due to a Party under this Agreement.", confidence=1.0
  - token Jaccard vs gold: 0.1667

**Reasoning:** The excerpt contains an entire article (ARTICLE 7) explicitly titled "AUDIT RIGHTS" with detailed provisions covering recordkeeping obligations, Valeant's audit rights over Dova's books and records, and Dova's audit rights over Valeant's activities, including frequency limitations, cost allocation, and adjustment procedures.

### 6. `cuad-00051` — Agreement Date

**Contract:** PAXMEDICA,INC_07_02_2020-EX-10.12-Master Service Agreement

**Excerpt:**
```
Exhibit 10.12 Certain identified information has been excluded because it is both not material and would likely cause competitive harm if publicly disclosed.

Master Service Agreement This Master Service Agreement ("Agreement"), entered into on May 25th, 2018 by and between CRO Consulting (Pty) Limited, whose Registered Office is at OnQ House 250 Market Street Fairland Johannesburg 2170 South Africa (hereinafter referred to as "CRO") and Purinix Pharmaceuticals LLC whose Registered Office is at 1266 East Main Street, Suite 700R, Stamford, CT 06902, USA (hereinafter referred to as "Client")....
```

**Gold:** present=True
  - spans: ['May 25th, 2018']

**Prediction:** present=True, span='This Master Service Agreement ("Agreement"), entered into on May 25th, 2018 by and between CRO Consulting (Pty) Limited', confidence=1.0
  - token Jaccard vs gold: 0.1765

**Reasoning:** The excerpt explicitly states the date on which the agreement was entered into, identifying it as May 25th, 2018.

### 7. `cuad-00057` — Agreement Date

**Contract:** MusclepharmCorp_20170208_10-KA_EX-10.38_9893581_EX-10.38_Co-Branding Agreement

**Excerpt:**
```
ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT   This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date") by and between Marine MP, LLC ("Lender"), for services of Arnold Schwarzenegger ("Endorser"), and Fitness Publications, Inc. ("Fitness") (collectively, Lender, Endorser, and Fitness are referred to as the "AS Parties") and MusclePharm Corporation with its principal place of business in Denver, Colorado and its subsidiaries, (collectively, "MusclePharm" or the "Company").   RECITALS   WHEREAS, the AS Parties have the rights necessary t...
```

**Gold:** present=True
  - spans: ['July 26, 2013']

**Prediction:** present=True, span='This ENDORSEMENT LICENSING AND CO-BRANDING AGREEMENT is entered into on July 26, 2013 (the "Effective Date")', confidence=1.0
  - token Jaccard vs gold: 0.1765

**Reasoning:** The excerpt explicitly states the date on which the agreement was entered into, identified as the "Effective Date," in the opening paragraph of the agreement.

### 8. `cuad-00050` — Agreement Date

**Contract:** GopageCorp_20140221_10-K_EX-10.1_8432966_EX-10.1_Content License Agreement

**Excerpt:**
```
CONFIDENTIAL

  PSiTECHCORPORATION   WEBSITE CONTENT LICENSE AGREEMENT     This Content License Agreement ("Agreement"), dated as of Feb 10, 2014 (the "Effective Date"), is by and between PSiTech Corporation, a BVI Corporation, with offices located at 303, 3rdFl, St. Georges Bldg, 2 Ice House St, Central, Hong Kong("Licensor"), and Empirical Ventures, Inc., a Nevada corporation with offices located at 100, 40 Lake Bellevue Dr, Bellevue, WA("Licensee").     WHEREAS, Licensee owns, operates and controls the Licensee Site (as defined below);     WHEREAS, Licensor owns or otherwise has the righ...
```

**Gold:** present=True
  - spans: ['Feb 10, 2014']

**Prediction:** present=True, span='This Content License Agreement ("Agreement"), dated as of Feb 10, 2014 (the "Effective Date")', confidence=1.0
  - token Jaccard vs gold: 0.2308

**Reasoning:** The excerpt explicitly states the agreement date as "Feb 10, 2014" and designates it as the "Effective Date" in the opening paragraph of the agreement.

### 9. `cuad-00052` — Agreement Date

**Contract:** EhaveInc_20190515_20-F_EX-4.44_11678816_EX-4.44_License Agreement_ Reseller Agreement

**Excerpt:**
```
Exhibit 4.44 THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018 is made BETWEEN: EHAVE, INC., a company incorporated under the laws of the Province of Ontario, Canada ("Ehave"); - and - COMPANION HEALTHCARE TECHNOLOGIES CORP, a company incorporated under the laws of the Province of Ontario ("CHT") RECITALS: A. Ehave has developed a software platform that provides an end-to-end patient management solution to healthcare professionals and provides that platform to users as a service. B. CHT has developed a business model to bring a similar service that Ehave provides using th...
```

**Gold:** present=True
  - spans: ['October 30, 2018']

**Prediction:** present=True, span='THIS LICENSE AND RESELLER AGREEMENT dated as of the October 30, 2018', confidence=1.0
  - token Jaccard vs gold: 0.2500

**Reasoning:** The excerpt explicitly states the agreement date in the opening line as "October 30, 2018." This is further reinforced by the definition of "Effective Date" which refers back to "the date first written above," confirming the agreement date.

### 10. `cuad-00035` — Affiliate License-Licensor

**Contract:** ArconicRolledProductsCorp_20191217_10-12B_EX-2.7_11923804_EX-2.7_Trademark License Agreement

**Excerpt:**
```
Exhibit 2.7 FORM OF TRADEMARK LICENSE AGREEMENT THIS TRADEMARK LICENSE AGREEMENT (this "Agreement"), made and entered into as of the [ ] day of [ ], 2020 (the "Effective Date"), by and between ARCONIC INC., a corporation organized under the laws of Delaware ("Licensee") and ARCONIC ROLLED PRODUCTS CORP., a corporation organized under the laws of Delaware ("Licensor"). WHEREAS, Licensor and Licensee entered into a Separation and Distribution Agreement having an effective date of the [ ] day of [ ], 2020 ("Separation and Distribution Agreement"); unless specifically defined in this Agreement,...
```

**Gold:** present=True
  - spans: ['Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark: (i) for the Licensed Products as set forth on Schedule 2; and (ii) as set forth on Schedule 1, concerning agreements entered into by Licensee prior to the Effective Date ("Existing Agreements"). For the avoidance of doubt, Licensor also grants to Licensee and its subsidiaries and affiliates a non-exclusive, worldwide royalty-free license for continued use of the Licensed Mark for the production and sale of inventory containing the Licensed Mark applied to such products during the Transition Period as set forth in section 8.2 of the Separation and Distribution Agreement and in Schedule 2 of this Agreement.']

**Prediction:** present=True, span='Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark', confidence=0.92
  - token Jaccard vs gold: 0.2941

**Reasoning:** The excerpt explicitly states that the Licensor grants the license "on behalf of itself and its Affiliates," indicating that the license extends from the Licensor and its affiliates to the Licensee. This directly addresses the Affiliate License-Licensor category, where the licensor's affiliates are included in the grant of rights.

## hallucinated_span (9 total)

### Worst 9 examples

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

**Prediction:** present=True, span='Upon reasonable prior written notice to Operator, Owner shall have the right during normal business hours to audit or examine all books and records of Operator to the extent they relate to Operator\'s performance hereunder as well as the relevant books of account of Operator\'s contractors, relating to the performance of Operator\'s obligations under this Agreement. Operator shall cooperate with Owner\'s auditors by (i) making the applicable books and records available for inspection by Owner\'s auditors, and (ii) making such copies of books and records as may be reasonably requested by such auditors. In no event shall Owner\'s audits unreasonably interfere with Operator\'s operations. Owner will be responsible for all costs of any such audit; provided that if, in any audit, Owner discovers overpayments by Owner of at least $250,000 in the aggregate ("Material Overpayment"), Operator will reimburse Owner for such Material Overpayment and all reasonable costs incurred by Owner in connection with such audit ("Audit Costs"). Owner shall have up until two years after the close of a Calendar Year in which to make an audit of Operator\'s records for such Calendar Year.', confidence=1.0

**Reasoning:** Section 6.5 "Independent Audits" explicitly grants Owner the right to audit Operator's books and records, specifies notice requirements, cost allocation, a two-year audit period, and defines an "Adjustment Claim." Additional audit-related language also appears in Section 6.4.1 regarding bank statement copies provided for "accounting and audit purposes."

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

**Prediction:** present=True, span='Pretzel Time or its designee shall have the right at any time during business hours and without prior notice to Franchisee, to inspect, audit and copy or the right to cause to be inspected, audited and copied, the business records, bookkeeping and accounting records, sales and income tax records and returns and other records of the Franchised Business', confidence=1.0

**Reasoning:** Section 16.A explicitly grants Pretzel Time the right to inspect, audit, and copy business records at any time during business hours without prior notice. It also details consequences of understatements found during audits, cost allocation for audits, and cooperation requirements for the Franchisee.

### 3. `cuad-00075` — Anti-Assignment

**Contract:** LOYALTYPOINTINC_11_16_2004-EX-10.2-RESELLER AGREEMENT

**Excerpt:**
```
No right or interest in this Agreement shall be assigned by                   Schoolpop without prior written permission of AEIS, which                   shall not be unreasonably withheld.

c.       This Agreement shall be deemed to have been made and executed                   in the State of Missouri and any dispute arising thereunder                   shall be resolved in accordance with the laws of the State of                   Missouri, without reference to its rules governing conflicts                   of law.

d.       Either party may terminate this Agreement with written notice ...
```

**Gold:** present=True
  - spans: ['No right or interest in this Agreement shall be assigned by                   Schoolpop without prior written permission of AEIS, which                   shall not be unreasonably withheld.', 'This Agreement (a) may not be assigned by Seller without the written          consent of AEIS, except to an entity controlling, controlled by or          under common control with Seller, provided, however, Schoolpop shall          remain liable for the obligations contained herein including the          attachments and Exhibits thereto, and (b) may be modified only by an          agreement in writing signed on behalf of AEIS by an executive officer.']

**Prediction:** present=True, span='No right or interest in this Agreement shall be assigned by Schoolpop without prior written permission of AEIS, which shall not be unreasonably withheld.', confidence=0.99

**Reasoning:** The excerpt contains two explicit anti-assignment provisions. The first restricts Schoolpop from assigning any right or interest in the Agreement without prior written permission of AEIS. The second, in the Trust Agreement (Section 3), prohibits Seller from assigning the Agreement without AEIS's written consent, with a limited exception for affiliated entities.

### 4. `cuad-00078` — Anti-Assignment

**Contract:** TEARDROPGOLFCO_10_23_1996-EX-10.12-ENDORSEMENT AGREEMENT

**Excerpt:**
```
he effective date of termination.

    18. PRODUCTS FOR OGLE'S USE. During the Contract Period, TPC shall supply Consolidated Artists, at no charge, with such quantities of the Endorsed Product as Consolidated Artists may reasonably request for Ogle's use and the personal use of Ogle's immediate family. In addition, TPC shall supply Consolidated Artists at normal wholesale price with such quantities of the Endorsed Product as Ogle may reasonably request for gifts to others.

    19. PROTECTING THE OGLE ENDORSEMENT. TPC and Consolidated Artists agree that they will take all necessary steps d...
```

**Gold:** present=True
  - spans: ['Neither TPC nor Consolidated Artists shall have any right to grant sublicenses hereunder or to otherwise', 'assign, transfer, alienate, encumber or hypothecate any of its rights or obligations hereunder without the express prior written consent of the other party, except that Consolidated Artists shall have the right to assign the financial benefits hereof and TPC hereby consents to such assignment.']

**Prediction:** present=True, span='Neither TPC nor Consolidated Artists shall have any right to grant sublicenses hereunder or to otherwise assign, transfer, alienate, encumber or hypothecate any of its rights or obligations hereunder without the express prior written consent of the other party, except that Consolidated Artists shall have the right to assign the financial benefits hereof and TPC hereby consents to such assignment.', confidence=0.99

**Reasoning:** Paragraph 25 explicitly addresses assignment, prohibiting either party from assigning, transferring, or otherwise encumbering their rights or obligations without the express prior written consent of the other party. This is a classic anti-assignment clause, with a limited carve-out allowing Consolidated Artists to assign financial benefits.

### 5. `cuad-00080` — Anti-Assignment

**Contract:** DataCallTechnologies_20060918_SB-2A_EX-10.9_944510_EX-10.9_Content License Agreement

**Excerpt:**
```
  all damages awarded in a trial to a third Party.

6    CONFIDENTIALITY

     6.1  Each Party  shall  keep  in  confidence  all material and information,           including  without  limitation  Content, received from the other Party           and  marked  as  confidential  or  which  should  be  understood to be           confidential,  and  may  not  use such material or information for any           other  purposes  than  those  set  forth  in  this  Agreement.  The           confidentiality  obligation shall, however, not be applied to material           and  information,  which  as  ...
```

**Gold:** present=True
  - spans: ['Neither  Party  shall  assign  or  transfer  to  any  third  party,           without  the  prior written consent of the other Party, this Agreement           or  any  rights  granted  herein.']

**Prediction:** present=True, span='Neither Party shall assign or transfer to any third party, without the prior written consent of the other Party, this Agreement or any rights granted herein.', confidence=0.99

**Reasoning:** Section 8.2 explicitly prohibits either party from assigning or transferring the agreement or any rights granted therein to a third party without the prior written consent of the other party, which is a classic anti-assignment clause.

### 6. `cuad-00131` — Cap On Liability

**Contract:** STAMPSCOMINC_06_24_1999-EX-10.18-SPONSORSHIP AGREEMENT

**Excerpt:**
```
 conflict with, or result in a      material default under any other contract or agreement to which Intuit is a      party, or by which it is bound; and (iii) it has the right to make      available on the Intuit Sites the Banner Advertisements, Sponsor Client      Graphics, Links and other advertisements placed hereunder.

16.3 By Client.  Client will defend and/or settle any third party claim brought      ---------      against Intuit, its affiliates, officers, directors, employees, consultants      and agents arising from:  (1) a breach of Client's representations or      warranties unde...
```

**Gold:** present=True
  - spans: ['THE LIABILITY OF EITHER PARTY FOR DAMAGES OR ALLEGED DAMAGES      HEREUNDER (EXCEPT UNDER SECTIONS 15 AND 16), WHETHER IN CONTRACT, TORT OR      ANY OTHER LEGAL THEORY, IS LIMITED TO, AND WILL NOT EXCEED, THE AMOUNTS TO      BE PAID BY CLIENT TO INTUIT HEREUNDER.', 'BASED ON BREACH OF CONTRACT, TORT (INCLUDING NEGLIGENCE) OR OTHERWISE,      WHETHER OR NOT THAT PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH      DAMAGE.', 'EXCEPT UNDER SECTIONS 15 AND 16, IN NO EVENT WILL EITHER PARTY BE LIABLE TO      THE OTHER FOR ANY SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES, WHETHER']

**Prediction:** present=True, span='THE LIABILITY OF EITHER PARTY FOR DAMAGES OR ALLEGED DAMAGES HEREUNDER (EXCEPT UNDER SECTIONS 15 AND 16), WHETHER IN CONTRACT, TORT OR ANY OTHER LEGAL THEORY, IS LIMITED TO, AND WILL NOT EXCEED, THE AMOUNTS TO BE PAID BY CLIENT TO INTUIT HEREUNDER.', confidence=0.97

**Reasoning:** Section 17 (LIMITATION OF LIABILITY) explicitly caps each party's liability at the amounts to be paid by Client to Intuit under the agreement, and also excludes special, incidental, and consequential damages. This is a classic cap on liability clause.

### 7. `cuad-00030` — Affiliate License-Licensor

**Contract:** GSITECHNOLOGYINC_11_16_2009-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT between SONY ELECTRONICS INC. and GSI TECHNOLOGY, INC.

**Excerpt:**
```
ined herein, including the following terms, which shall have the meanings set forth below:     1





     1.1 IP Agreement     The term "IP Agreement" means this Intellectual Property Agreement, including all attached Exhibits hereto, and any  amendments or supplements agreed to in writing and signed by SONY and PURCHASER.     1.2 Asset Purchase Agreement     The term "Asset Purchase Agreement" means the Asset Purchase Agreement dated August 28, 2009 between SONY and  PURCHASER to which this IP Agreement is attached as Exhibit F.     1.3 Effective Date     The term "Effective Date" means t...
```

**Gold:** present=True
  - spans: ['SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free  license (a) under the Licensed Patents to make, have made, use, offer to sell, sell, otherwise dispose of, and import any Competing Products  (including, without limitation, the SRAM Products); and (b) to use, reproduce, modify, prepare derivative works of, perform, display, and otherwise  practice and exploit in any manner any and all of the SRAM Intellectual Property in connection with the use and exploitation of the', 'Transferred Assets, and to make, have made, use, offer to sell, sell, otherwise dispose of, and import Competing Products (including, without  limitation, SRAM Products).']

**Prediction:** present=True, span='SONY, on behalf of itself and its Affiliates, hereby grants to PURCHASER a worldwide, non-exclusive, fully paid-up, royalty-free license (a) under the Licensed Patents to make, have made, use, offer to sell, sell, otherwise dispose of, and import any Competing Products (including, without limitation, the SRAM Products)', confidence=0.92

**Reasoning:** Section 3.1 explicitly states that SONY grants the license "on behalf of itself and its Affiliates," meaning the licensor (SONY) is extending the license grant to cover its affiliates as well. This is the hallmark of an Affiliate License-Licensor clause, where the licensor grants rights that encompass its affiliates' intellectual property.

### 8. `cuad-00100` — Audit Rights

**Contract:** IVILLAGEINC_03_17_1999-EX-10.16-SPONSORSHIP AGREEMENT

**Excerpt:**
```
 work together in good faith to amend or terminate this Agreement.

2.       Promotion.

         A. During the Production Period, iVillage will design, develop, construct and host a Ford bridge site (the "Bridge Site") which shall include approximately [*] pages of content and other interactive material such as a travel planner or a car design feature. During the Promotion Period, iVillage will continue to host, maintain and update the Bridge Site. Upon receipt from iVillage of the proposed Bridge Site design and content, FMM shall have no more than five (5) business days in which to provi...
```

**Gold:** present=True
  - spans: ['All traffic reports shall be audited by the third party traffic auditor selected pursuant to Section 2.C.(ii).', 'During the Promotion Period, iVillage traffic shall be          audited by a third party traffic auditor listed on Exhibit A and          iVillage shall provide FMM with relevant reports on a biweekly basis.']

**Prediction:** present=True, span='During the Promotion Period, iVillage traffic shall be audited by a third party traffic auditor listed on Exhibit A and iVillage shall provide FMM with relevant reports on a biweekly basis.', confidence=0.85

**Reasoning:** The excerpt references third-party traffic auditing of iVillage's traffic and reports, which constitutes audit rights language. Specifically, Section 2.C.(ii) states that iVillage traffic shall be audited by a third party traffic auditor, and Section 3 reaffirms that all traffic reports shall be audited by the third party traffic auditor. While these are limited to traffic/impression audits rather than full financial audits, they substantively address audit rights in the context of the agreement's performance obligations.

### 9. `cuad-00005` — Affiliate License-Licensee

**Contract:** ConformisInc_20191101_10-Q_EX-10.6_11861402_EX-10.6_Development Agreement

**Excerpt:**
```
riteria, then Stryker will provide Conformis with a written notice of rejection within the Acceptance Notification Period   describing the defect in view of the relevant Acceptance Criteria and including sufficient detail with respect to such Stryker testing   and testing results as Conformis reasonably requests ("Failure Notice"). Conformis shall have [**] (or such longer period of time   as may be agreed between the parties in good faith should the scope and complexity of the applicable Deliverable warrant some   longer period of time) ("Redelivery Period") following the date it receives ...
```

**Gold:** present=True
  - spans: ['Except as specifically provided in the Distribution Agreement, Conformis shall be prohibited from   developing or assisting another in developing, or causing another to develop, Patient-Specific Instrumentation for Off-The-Shelf   Knee Implants for any Third Party in the field of orthopedics until January 1, 2032 (or earlier, to the extent set forth in Section   2.3.3.4 or Section 2.3.5 of the Distribution Agreement), with the exception that Conformis (including any entity involved in a   Change of Control of Conformis, any such entity an "Acquirer"), may develop Patient-Specific Instrumentation for any Off-The-   Shelf Implants of Conformis, an Acquirer or any of their Affiliates.']

**Prediction:** present=True, span='the Joint IP may be used freely by either Party or its Affiliates and licensed to Third Parties by Conformis and its Affiliates, on the one hand, outside of the Buyer Field or by Stryker and its Affiliates, on the other hand, within the Buyer Field, in each case, without the consent of, or duty to account to or notify, the other Party', confidence=0.72

**Reasoning:** The excerpt contains language permitting Affiliates to use Joint IP freely and to license it to Third Parties, specifically stating "the Joint IP may be used freely by either Party or its Affiliates and licensed to Third Parties by Conformis and its Affiliates, on the one hand, outside of the Buyer Field or by Stryker and its Affiliates, on the other hand, within the Buyer Field." This addresses licensing rights granted to Affiliates as licensees of the Joint IP, which is substantively relevant to the Affiliate License-Licensee category.

## parse_fail (0 total)

_No errors in this bucket._
