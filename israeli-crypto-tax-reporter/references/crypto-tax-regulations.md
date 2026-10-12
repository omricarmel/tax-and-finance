# Israeli Cryptocurrency Tax Regulations

## Primary Legal Sources

### Income Tax Ordinance (Pekudat Mas Hachnasa)

The Income Tax Ordinance is the foundational tax law in Israel. Key sections relevant to cryptocurrency:

**Section 88 - Definitions:**
- Defines "asset" (neches) broadly to include "any type of property, whether tangible or intangible"
- Cryptocurrency falls under this definition as an intangible asset
- This classification was affirmed in Circular 2018/05

**Section 91 - Capital Gains Tax:**
- Capital gains on the sale of assets are taxable
- The gain is calculated as the difference between the sale price (tmura) and the cost basis (mechir mekorri)
- The gain splits into a real gain and an inflationary amount (s.88). The chargeable inflationary amount (s.91(c), 10%) is nil for crypto, but the split itself still applies; the 1399י carries the lines

**Section 91(b)(1) - Tax Rate for Individuals:**
- Capital gains for an individual: **up to 25%** on the real gain, taxed under s.121 as the top layer of income and capped at 25%. From age 60 the s.121(b)(1) brackets (10%, 14%, 20%) can make it lower; s.91(e)(1) lets the taxpayer spread the real gain over up to four tax years, or the ownership period if shorter, ending in the year of the sale.
- **Lots acquired before 1.1.2012 (מועד השינוי)**: bitcoin was bought and mined from 2009, so s.91(b1) does reach crypto. The real gain is apportioned by days (s.88): the part from acquisition to 31.12.2011 is taxed under s.121 at no more than 20%, the rest at up to 25%. The calculator flags such lots but applies 25% throughout.
- The 30% rate in Section 91(b)(2) applies to the sale of a **נייר ערך בחבר-בני-אדם**, a security in a body corporate, by a material shareholder. A fungible token is not one, and Circular 05/2018 never invokes 91(b)(2), so do NOT apply 30% to an ordinary crypto disposal. Treat an equity-like token in an incorporated entity as a CPA / pre-ruling question.

**Section 2(1) - Business Income:**
- If crypto trading constitutes a "business" (esek), gains are taxed as ordinary income
- Marginal tax rates apply: 10% to 47% depending on the income bracket and on whether the income counts as personal exertion, plus the 3% surtax limb above the threshold
- Plus social insurance (bituach leumi) and health tax (mas briut)
- A business LOSS in the year offsets total taxable income from other sources, capital gains included (s.28(a)); the taxpayer may ask that it not be set against capital gains taxed at no more than 25% (s.28(c)). A business loss carried forward offsets only business income, or s.2(2) income on the s.28(b) conditions

**Section 2(4) - Passive Income:**
- Interest, dividends and similar passive returns from crypto lending. A staking reward is NOT interest unless it is characterised as such; otherwise it is income under s.121 at marginal rates, starting at **31%** for income not from personal exertion of an individual under 60 (s.121(a)(1)), with the lower s.121(b)(1) brackets only from age 60
- **Section 2(4) is a charging section and fixes no rate.** The rate on interest is in Section 125C, whose structure is three-tiered. **125C(b)** sets the general 25%. **125C(c)(1)** charges **15%** where the interest is paid on an asset that is not index-linked, or is only partly linked, or is unlinked to redemption; crypto lending is not CPI-linked, so 15% is arguable, but s.125C(a) defines "מדד" for an asset linked to or denominated in foreign currency as the exchange rate, so a USD-stablecoin loan may be argued to be linked and taxed at 25%; treat 15% as the aggressive position there. **125C(d)** overrides BOTH and charges the full marginal rate under Section 121 where the interest is income under s.2(1) or is recorded (or required to be recorded) in the recipient's books, where he claimed interest and linkage expenses on the asset, where he is a material shareholder in the payer, or where he is an employee, supplier or other special-relations party of the payer unless the rate is shown to have been set at arm's length. That last limb covers most yield-platform positions. Establish which limb applies rather than defaulting to 25%.

### Circular 2018/05 (Chozar 05/2018)

Published by the Israeli Tax Authority on January 17, 2018, this is the primary guidance document for cryptocurrency taxation.

**Key determinations:**

1. **Classification**: Virtual currencies (matbeot virtualiyim) are not considered "currency" (matbea) or "foreign currency" (matbea chutz) under Israeli law. They are classified as assets.

2. **Tax treatment**: Gains from the sale or exchange of virtual currencies are subject to capital gains tax under Chapter E of the Income Tax Ordinance.

3. **Business vs. investment**: the circular acknowledges that crypto activity may constitute a business, but **section 3.1.4 does NOT enumerate a test**. Its whole statement is that classification "ייקבע בהתאם למבחני עסק כפי שנקבעו **בפסיקה**", i.e. by the badge-of-trade tests established in the CASE LAW. Cite the factors (trade frequency and volume, holding period, time and attention, leverage, professional knowledge, financing, inventory-versus-investment intent) as case law, never as this circular. Earlier versions of this file listed them as the circular's own factors; that attribution was wrong and was removed on 2026-08-27.

4. **Mining is business income, categorically.** Section 3.1.4: crypto reaching a person through mining, "יש לראות את ההכנסות המתקבלות בידיו - **כהכנסה עסקית**". There is no hobby-versus-scale alternative in the circular, and earlier versions of this file offered one. For VAT the miner is separately registered as an **עוסק** under section 3.2.3.2.4, which is a different regime again from the מוסד כספי registration that applies to a business-level trader. Mining expenses (electricity, equipment depreciation) are deducted from the business income under the general deduction rule of s.17; they are not part of the coins' cost basis.

5. **ICOs and token offerings**: Tokens received in an ICO are treated as an asset acquisition. The cost basis is the amount paid for the tokens. For project founders, token distribution may be treated as income.

6. **Cost basis**: the circular prescribes **no** method. FIFO is the customary Israeli default and another method may be used if applied consistently and documented, but do not attribute FIFO to this circular; earlier versions of this file did.

7. **Currency conversion**: amounts are reported in shekels, but the circular does **not** require the Bank of Israel representative rate and the word יציג does not appear in it. Its actual rule, section 3.1.5.1, is the **fair value in shekels** of the crypto, with an override: where the asset or goods bought carry a **stated price (מחיר נקוב)**, that stated price fixes the crypto's disposal value. The same section requires the SAME figure to serve as the seller's proceeds and the buyer's original cost. The representative rate is a defensible documented choice, not a legal requirement; earlier versions of this file asserted the circular required it.

8. **Record retention**: section 3.1.3 requires documents to be kept "ככול שיידרש להנחת דעתו של פקיד השומה" and fixes **no** period.

9. **VAT**: section 3.2.3.2.3 registers a business-level trader as a **"מוסד כספי"** under **Section 4 of the VAT Law**, not as an osek charging 18% output VAT; 3.2.3.2.4 registers the miner as an **עוסק**; 3.2.3.1 leaves a non-business investor outside VAT entirely.

### Subsequent Guidance and Court Rulings

**ITA Circular 07/2018:**
- Addresses the issuance of utility tokens for services or products in development (relevant to issuers, not to an ordinary holder)

**District-court line of decisions, 2020-2024:**
- Multiple Israeli district-court rulings have classified frequent crypto trading (high transaction volume relative to portfolio size, sustained over multiple years, with active position management) as a business activity, taxing the gains at marginal income rates instead of 25% capital gains. Verify any further case name on `psakdin.co.il` or `nevo.co.il` before citing it.
- **Kopel**: ע"מ 11503-05-16 קופל נ' פקיד שומה רחובות (19.5.2019) held that bitcoin is not currency or foreign currency, so the s.9(13) exemption for exchange-rate differences is unavailable. The docket is cited in the explanatory notes of the government digital-asset bill below.

**Pending, NOT law: the government digital-asset bill.** הצעת חוק לתיקון פקודת מס הכנסה (מס' 285) (נכס דיגיטלי), התשפ"ו-2026, published in הצעות חוק הממשלה 1925 on 19.1.2026, would define "נכס דיגיטלי" in s.88, define "מטבע חוץ" in s.1, and add a source rule for digital-asset gains. Its last recorded Knesset status (1.2.2026) is "tabled for first reading". Do not present any of it as in force.
- The ITA's position that crypto is a taxable asset (not foreign currency) has been consistently upheld; agents should never cite specific case docket numbers without first verifying them on a legal database.

**Note on case citations:** never invent or fabricate ruling numbers. If a specific docket is needed, look it up on `nevo.co.il`, `psakdin.co.il`, or the Israeli Tax Authority's published rulings (`mas.gov.il/החלטות-מיסוי`); otherwise, describe the line of authority generically.

## Tax Rates Summary

### For Individuals (Yachid)

| Income Type | Rate | Notes |
|------------|------|-------|
| Capital gains (investment) | 25% | Standard rate for assets held as investment |
| Capital gains, material shareholder, Section 91(b)(2) | up to 30% | Applies to a **security in a body corporate**, not to a fungible token. Do not default crypto here |
| Business income | 10-47%, plus the 3% surtax limb | Marginal rates based on total income |
| Interest (s.125C) | 15%, 25% or marginal | 15% on a non-index-linked asset (125C(c)(1)), 25% generally (125C(b)), marginal where 125C(d) applies |
| Staking / airdrop income at receipt | Marginal (s.121) | From 31% for an individual under 60 (s.121(a)(1)); lower brackets from 60 (s.121(b)(1)) |
| Surtax (mas yesafim) - 2026 | 3% on total taxable income above the threshold + 2% on the part of capital-source income that ITSELF exceeds the threshold | Threshold NIS 721,560 / monthly NIS 60,130, **fixed for 2024 through 2027** in the Ordinance. ITA execution instruction (הוראת ביצוע) 05/2025: salary 400,000 + capital 700,000 gives 3% on 378,440 and no 2%; 1,500,000 total of which 1,100,000 capital gives 23,353 + 7,569 = 30,922. Before 2025 only the 3% limb existed, and it already reached capital gains (thresholds: 649,560 in 2019, 651,600 in 2020, 647,640 in 2021, 663,240 in 2022, 698,280 in 2023). Business income is s.2(1), not capital-source, so it bears only the 3% |

### For Companies (Chevra)

| Income Type | Rate | Notes |
|------------|------|-------|
| Capital gains | 23% | Corporate tax rate |
| Business income | 23% | Corporate tax rate |

### National Insurance and Health Tax (2026)

If crypto income is classified as business income (not investment):
- **Bituach Leumi (self-employed, 2026)**: **4.47% on income up to NIS 7,703/month; 12.83% on the portion above, up to the maximum insurable income of NIS 51,910/month** (per btl.gov.il). Verify the current bracket and ceiling at the start of each tax year.
- **Mas Briut (health tax, 2026)**: **3.23% on income up to the same threshold; 5.17% on the portion above**.
- Combined effective rate (BL + Mas Briut): roughly **7.7% / 18%** across the two bands.
- These rates do NOT apply to capital gains (investment classification) - only to income classified as a business under Section 2(1).

## Reporting Requirements

### Reporting forms: the ITA's own published titles

Taken from the Tax Authority's annual-return service page. The titles are narrower than this skill previously assumed, so read them before routing a crypto disposal onto a form.

| Form | ITA title | What it actually covers |
|---|---|---|
| 1399י | הודעה על מכירת נכס וחישוב המס המגיע | Sale of an **asset**. The Section 91(d)(1) 30-day notice, and the right vehicle for a crypto disposal. 1399ח is the company equivalent |
| 1322 | רווחי הון מניירות ערך סחירים **(הנסחרים בבורסה)** | Gains on **exchange-traded** securities |
| 1325 | טופס עזר לריכוז מכירות של ניירות ערך **על פי שיעורי המס** | Auxiliary aggregating securities sales **by tax rate**. Nothing in the title concerns withholding |
| 1326 | רווחי הון מניירות ערך סחירים | A further securities form |
| 1326א | טופס עזר לחישוב רווח או הפסד ריאלי ממניות שליטה | A real-gain helper for CONTROLLING SHARES. For crypto the split is made on the 1399י itself |
| 1320 | דוח רווח והפסד לבעלי עסק עצמאי **(נספח א)** | Business P&L appendix |
| 1301 נספח ג / ג1 / ג-2 | רווח הון מניירות ערך סחירים | The 1301's own appendix for TRADED SECURITIES gains (field 256). Not a crypto appendix |
| 1344 | דיווח על הפסדים מועברים משנת מס קודמת | Losses brought forward, which is where a Section 92 carry-forward lands |

**The "Nispach Gimel" routing earlier versions of this skill gave for crypto is wrong.** The 1301 does use a נספח ג label, but for traded-securities gains. Since 1322, 1325 and 1326 are all titled as securities forms and crypto is a נכס, confirm with the assessing officer or a CPA which appendix the ITA expects for a non-securities asset rather than asserting one.

### Retracted: the old Form 1322 + Form 1325 routing

Earlier versions of this file told the reader to itemise crypto disposals on Form 1325 and carry the totals to Form 1322 as "Nispach Gimel". **That routing is withdrawn.** Both forms are titled by the ITA as ניירות ערך forms, 1322 expressly as securities הנסחרים בבורסה, and neither carries a נספח label on the ITA's page. Use the table above.
- Lists acquisition date, disposal date, cost basis, proceeds, and gain/loss for each disposal.
- All amounts must be in NIS.

### Form 1301 (Annual Individual Tax Return)

The comprehensive annual return that includes:
- All income sources (salary, business, capital gains, passive income)
- **For a crypto gain there is no ITA "crypto appendix", so do not attach 1322 or 1325**, which the ITA titles as securities forms. On the TY2025 1301, field **054** is the number of capital-gain and betterment forms attached and field **056** the total sale proceeds outside traded securities; traded securities go to field 256 via נספח ג. The crypto gain is supported by: a copy of each Form 1399י already filed with the assessing officer (its tax paid is credited against the s.91(d) advance); a self-prepared disposal schedule in the 1399י columns, one line per FIFO-matched disposal (asset, יום הרכישה, יום המכירה, מחיר מקורי, תמורה, real gain); and **Form 1344** where a loss is brought forward, which s.92(b) allows only if a return was filed for the loss year. Where the same taxpayer also disposed of exchange-traded securities, 1322 and 1325 carry THOSE, and only those. Confirm the final packaging with the assessing officer or a CPA
- **Filing deadline for tax year 2025 (filed in 2026): 30 June 2026 online; 31 May 2026 on paper**, after the ITA extended the paper date from 29 May (notice of 23.04.2026). Representatives' extensions were published separately. Both dates have passed. The TY2026 return is filed in 2027 and its deadline was not yet published on 12.10.2026; verify on gov.il.

### Advance Tax Payments (Mikdamot)

**Form 1399י (1399-yod) - capital gains advance payment for individuals:**
- Within 30 days of **every sale**, including a sale at a loss (s.91(d)(1): the notice sets out "רווח ההון או הפסד ההון"), the taxpayer files Form 1399י with the assessing officer (pakid shuma) and pays 25% of the gain as an advance. The form's loss line counts capital losses brought forward, losses of the current year, and losses on traded securities, so a later gain is reduced by earlier same-year losses.
- Virtual-currency disposals: transaction code **77** ("כל שאר העסקאות (כולל מוניטין ומטבע וירטואלי)") with code **71** ("מימוש / המרה של מטבע וירטואלי").
- **Many trades in one month**: the 1399י instructions say each trade is computed separately, but all of a month's trades may be reported as ONE transaction with a weighted-average acquisition date; alternatively the real gain is entered as a forced transaction (code 51 with code 71). A working paper with the computations is attached either way.
- Form 1399ח is the equivalent form for companies.
- No statutory de minimis applies to the notice.
- **Withholding by an Israeli platform**: Bits of Gold announced in April 2022 an arrangement with the ITA for its "closed circle" clients: 25% of the profit withheld with same-year losses offset (instead of 30% of the consideration), no separate 30-day notice for a withheld sale, and no annual return where none is otherwise required. Whether it still runs, and on what terms, is unverified: ask the platform for its annual withholding confirmation and credit it. Draft regulations of December 2024 on withholding by supervised digital-asset businesses were not enacted.
- Failure to file: interest (ribit) and linkage differences (hafreshei hatzamda) accrue from the 30-day deadline.
- The advance is credited against the final annual tax liability.

### Form 909 (Paying Tax When a Bank Refuses Crypto Funds)

A distinct, very common Israeli problem: a commercial bank refuses (in writing) to accept crypto-derived deposits, so the taxpayer cannot fund the tax payment through a normal account. The ITA, jointly with the Bank of Israel and the Anti-Money-Laundering Authority, published a temporary procedure (Hora'at Sha'a, ITA Instruction 06/2024, "נוהל לקבלת כספי מסים בשל רווח ממימוש אמצעי תשלום מבוזר", Instruction 06/2024 dated 03.04.2024, implementing a procedure first published on 31.12.2023) for this case:

- **Who**: an individual (NOT a company) who realised a crypto gain and has no alternative funding source, after at least one Israeli commercial bank refused the funds (including refusing to open an account).
- **Form**: **Form 909** ("דיווח על פעילות במטבעות וירטואליים ובקשה לתשלום המס המגיע במימוש המטבעות").
- **Required attachments**: written bank-refusal letter; working paper computing the taxable income and tax; proof of the legal source of the funds used to buy the coins; a money-trail working paper for the coins over the holding period; deposit/account-management confirmations from the financial-service provider.
- **How**: filed to the assessing officer either online via the ITA CRM together with the annual return, or physically.
- **Outcome**: after a money-laundering-risk review and a tax assessment under Section 145, the tax is paid in NIS directly into the ITA's account at the Bank of Israel.
- **Validity**: temporary. Extended in January 2026 and again, by an ITA notice of 31.8.2026, to **31.12.2027**.
- **No refund**: per the same notice, tax paid under the procedure is not returned to the taxpayer even where refunds, losses, deductions or credits that the assessment agreement or self-assessment did not reflect stand to his credit. Put every loss and credit into the computation before paying.

### Reporting Thresholds

- **Any capital gain**: technically reportable regardless of amount.
- **Advance payment (mikdama)**: the 30-day notice is due on every sale; the advance is the tax on the gain after losses brought forward and earlier same-year losses.
- **Annual filing**: required for individuals with income from sources other than salary, or with annual income exceeding the filing threshold. A crypto disposal generally creates a filing obligation, but a TY2025 draft amendment to the exemption-from-filing regulations (טיוטת תקנות מס הכנסה (פטור מהגשת דין וחשבון), published for public comment January 2025) would exempt a salaried taxpayer from filing on crypto gains where the sales were made through a supervised Israeli body that withheld the full tax, the year's sales stayed under the EXISTING תוספת ו' ceiling of the exemption regulations (the securities-sale ceiling), AND the digital assets he held that year were worth no more than NIS 400,000 (per a practitioner summary of the draft). It was not enacted (see below). The enabling power is **Section 134A**; Section 131 is the filing duty being exempted FROM. **Do not quote the general Section 131 ceilings for this**, which earlier versions of this file did: they are a different mechanism. Incomplete withholding or trading through an unsupervised or foreign venue restores the full filing duty; paying an advance does not by itself remove it. Still a draft, so verify enactment and read the ceiling out of the regulation text.
- **Record retention**: Circular 05/2018 section 3.1.3 requires documents to be kept "ככול שיידרש להנחת דעתו של פקיד השומה" and fixes **no period**. The seven-year figure comes from the bookkeeping directives, not from this circular. Confirm the applicable period rather than citing the circular for it.

### Voluntary Disclosure Procedure 2025-2026 (Crypto Track)

**CLOSED on 31 August 2026.** As of 12.10.2026 no extension or successor had been announced. Kept here for users asking about an application already lodged. Published 25 August 2025 by the ITA, the procedure expressly covered digital assets and offered criminal immunity for regularising prior-year unreported income:

- **Two tracks**:
  - **Green Track** - for the digital-asset limb, income from digital assets **not exceeding NIS 500,000 for the entire disclosure period** (NOT per year, which earlier versions of this file said), where the fair value of ALL the applicant's digital assets at **31 December 2024** did not exceed **NIS 1,500,000**. The Tax Authority, not the applicant, decided the track. Anonymity removed.
  - **Regular Track** - for cases above those thresholds.
- **Deadline**: declared 25 August 2025, ended **31 August 2026**. There is no immunity to obtain now; the route is an ordinary Section 131 correction through the assessing officer, with the exposure that normally attaches to a late or amended return, after advice from a tax-specialist lawyer. Check gov.il for a successor rather than assuming one.
- **Anonymity**: not available; all applications included the taxpayer's identifying details.

### CARF (OECD Crypto-Asset Reporting Framework)

- Israel committed to CARF. **No Israeli implementing legislation has been enacted**, so no domestic data-collection start date can be asserted. In its July 2025 call for comments the ITA said exchanges were expected to begin in 2027 "subject to the required legislation".
- **First international exchange: 2028.** The OECD Global Forum's CARF commitments list places Israel in the group of "Jurisdictions undertaking first exchanges by **2028**", alongside Australia, Canada, Hong Kong, Singapore, Switzerland and the UAE; the 2027 group is a different list of jurisdictions. Earlier versions of this file hedged to "2027-2028"; the primary source resolves it to 2028. Re-verify against the current commitments list, since the Global Forum revises it.
- For taxpayers, this means: crypto held on a CARF-participating exchange becomes visible to the ITA once exchanges begin. Past-year non-compliance is increasingly likely to surface during routine matching.

## DeFi-Specific Guidance

The Israeli Tax Authority has not published comprehensive DeFi guidance. The following represents the conservative consensus among Israeli tax professionals:

### Staking
- **Conservative view**: Income at receipt (market value), taxed at marginal rates under s.121 (from 31% under age 60), or under s.125C only if the reward is characterised as interest
- **Alternative view**: Capital gain treatment (similar to stock splits), taxed at 25% upon sale
- **Filing position**: the conservative filing position is income at receipt; whether a capital-gain position can be argued in an assessment dispute is a question for a tax adviser

### Liquidity Provision
- Depositing into a pool for LP tokens: **contested**. Under Circular 05/2018 s.3.1.5.1 a swap of crypto for other consideration is a disposal, which supports treating the deposit as one; the ITA has not decided. Pick a treatment and carry it through (Scenario 9 shows both)
- Impermanent loss: not deductible until the position is closed
- Withdrawing from pool: may trigger a taxable event if the composition differs from the deposit
- Yield/fee rewards: income at receipt

### Airdrops
- Unsolicited airdrops: income at market value on receipt date
- Airdrops requiring action (claiming, staking): still income at receipt
- Airdrop tokens that are worthless at receipt: zero income, zero cost basis
- Cost basis for future sale: market value at receipt

### NFTs
- Creating and selling NFTs: business income for artists/creators
- Purchasing and reselling NFTs: capital gain (or business income if frequent)
- Receiving NFTs as rewards: income at market value
- NFT-to-NFT trades: taxable as crypto-to-crypto exchanges

### Wrapped Tokens
- Wrapping (e.g., ETH to WETH): generally not a taxable event (same economic exposure)
- Cross-chain bridges: may be taxable if involving a swap mechanism
- Synthetic assets: treated based on the underlying asset's tax treatment

## International Considerations

### Foreign Exchange Controls
- Israel does not have strict foreign exchange controls
- Crypto service providers in Israel operate under the Prohibition on Money Laundering Order for financial-asset-service providers, which sets a ceiling on "casual customer" activity before full identification and recording duties attach, and requires reports on suspicious or threshold activity. **The specific shekel ceiling is UNVERIFIED here**: the figure this file previously stated could not be confirmed against any reachable primary source, so read it out of the Order itself before relying on it. Note this is AML reporting by the PROVIDER, separate from the taxpayer's own tax-reporting duty
- Israeli banks may request documentation for large crypto-related deposits

### Tax Treaties
- Israel has a wide treaty network; check the treaty with the other country
- Capital gains from crypto are generally taxable in the country of residence (Israel, for Israeli residents)
- Foreign tax credits may be available if tax was paid in another jurisdiction

### OECD Crypto-Asset Reporting Framework (CARF) - see Reporting Requirements above
- See the dedicated CARF block under "Reporting Requirements": first international exchange **2028** per the OECD commitments list; no Israeli implementing legislation yet.

## Compliance Best Practices

1. **Maintain detailed records**: Every transaction, including dates, amounts, prices, fees, and exchange rates
2. **Convert to NIS**: Keep a running record of NIS values for all transactions
3. **File a 1399י within 30 days of EVERY sale**, loss sales included, with the advance on any gain
4. **Separate wallets**: Consider using separate wallets for different tax classifications (investment vs. business)
5. **Professional advice**: Consult with a tax advisor familiar with crypto for complex situations
6. **Unreported past years**: the voluntary disclosure procedure closed on 31.8.2026. Correct the returns under Section 131 after advice from a tax-specialist lawyer, and check gov.il for any successor procedure


## Section 100A: the exit tax on ceasing Israeli residency

Quoted from the Income Tax Ordinance. The section has five subsections, (a) to (e), and there is **no subsection (b1)**; the separate section **100A1** deals with distributions out of revaluation profits and is a different provision entirely.

- **(a)** An asset of an Israeli resident who ceases to be an Israeli resident **is deemed sold on the day before** residency ends.
- **(b)** A person who **did not pay** the tax at that point **"יראו אותו כאילו ביקש לדחות"**, is deemed to have requested deferral, to the date of realization. **Deferral is a deeming rule, not an election**: there is no form and no choice. He then pays the tax on the "chargeable portion of the gain". The provision closes: **"ואולם, הפרשי הצמדה וריבית, כהגדרתם בסעיף 159א ייווספו רק החל במועד המימוש ועד לתשלום המס בפועל"**, so **neither interest nor linkage differentials accrue during the deferral period**; they run only from realization to actual payment.
- **(c)** Where the sale is in any event chargeable to Israeli tax at realization, the ordinary capital-gains tax applies **instead of** (b).
- **(d)** **"חלק הרווח החייב"** is the **real** capital gain **at the date of realization**, multiplied by the holding period from acquisition to cessation of residency, divided by the whole period from acquisition to realization. Three consequences: it is apportioned by **elapsed time**, not by a valuation at exit; it is measured at **realization**, so post-emigration appreciation enlarges the Israeli base pro rata; and it is the **real** gain, net of the inflationary amount. **"מימוש"** is defined as the actual sale of the asset.
- **(e)** The Finance Minister may make implementing regulations, including on double-tax relief and reporting.

The FIFO calculator does not model any of this. Route relocation scenarios to a CPA.

## Form 909: paying when a bank refuses crypto-derived funds

Where a commercial bank refuses **in writing** to accept crypto-derived deposits, an **individual** (not a company) may file **Form 909**, "דיווח על פעילות במטבעות וירטואליים ובקשה לתשלום המס המגיע במימוש המטבעות", with the assessing officer and pay the tax in shekels directly into the Tax Authority's account at the Bank of Israel. The route is a temporary procedure (הוראת שעה) under ITA Instruction 06/2024, run with the Bank of Israel and the Anti-Money-Laundering Authority, extended to 31.12.2027. Tax paid under it is not refunded.

Required attachments: the written bank-refusal letter, a taxable-income working paper, a full money-trail of the coins, and proof of the legal source of the original funds. Filed online through the ITA CRM with the annual return, or physically at the assessing officer. The request goes through a money-laundering risk review before the payment is accepted.
