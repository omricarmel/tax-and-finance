# Domain Checklist: israeli-crypto-tax-reporter

Scope: Israeli cryptocurrency capital-gains tax calculation and reporting.
Category: tax-and-finance.
Audience: Israeli-resident individual crypto investors (and the borderline business-classification case).

## Must cover (core)

- **Crypto = "asset" (neches), not currency.** Capital-gains regime under Chapter E, anchored in Section 88 of the Income Tax Ordinance and ITA Circular 05/2018.
- **25% individual capital-gains rate on the real gain, Section 91(b)(1).** The 30% rate in 91(b)(2) is for a **security in a body corporate** held by a material shareholder and must NOT be defaulted onto a fungible token. 25% is a ceiling (s.121 top layer); from age 60 the s.121(b)(1) brackets can lower it, and s.91(e)(1) allows spreading. Section 91(b1) DOES reach crypto bought 2009-2011: the real gain to 31.12.2011 is taxed at no more than 20%. Section 91(c) taxes the **chargeable** inflationary amount at 10%, which is nil for any crypto lot because Section 88 confines it to gain that would have arisen by 31.12.1993.
- **FIFO cost basis as the customary Israeli default.** NOT prescribed by Circular 05/2018, which sets no cost-basis method; other methods are usable if consistently applied and documented.
- **Crypto-to-crypto swap is a taxable disposal.** Each swap = disposal of leg A + acquisition of leg B, both valued in NIS at swap time.
- **Stablecoin disposals are taxable.** USDT/USDC/DAI are "asset" under Section 88, not foreign currency.
- **NIS conversion.** Circular 05/2018 does NOT require the Bank of Israel representative rate; section 3.1.5.1 sets the value at **fair value in shekels**, overridden by the **stated price (מחיר נקוב)** of the asset or goods bought where one exists, and requires the SAME figure to serve as the seller's proceeds and the buyer's original cost. The representative rate is a defensible documented choice, not a legal requirement. Earlier versions of this file asserted the circular required it; it does not, and the word יציג does not appear in it.
- **Inflation indexation split, Sections 88 and 91(c).** The gain splits into a real gain, taxed under 91(b), and an inflationary amount. **91(c) taxes the CHARGEABLE inflationary amount at 10%, not 0%**; the practical result for crypto is nil only because Section 88 confines the chargeable part to gain that would have arisen by 31.12.1993. Do NOT cite 91(b)(3) for this: that subsection is the 15% (20% for a material shareholder) rate on non-index-linked bonds, commercial paper and loans, and has nothing to do with the split. The calculator flags long-held lots but does not compute it; The split is made on the 1399י itself; Form 1326א is a helper for controlling shares only.
- **Loss offset and carryforward, Sections 92 and 28.** Same-year offset (including against land betterment, s.92(a)(1)), foreign-asset losses first against foreign gains (s.92(a)(3)), carryforward against capital gains only and only if the loss-year return was filed (s.92(b)); a same-year business loss offsets capital gains too (s.28(a)).
- **Cost-basis special cases (Section 88 "מחיר מקורי"):** inheritance carries the deceased's basis and acquisition day; a gift carries the donor's basis ONLY if exempt under s.97(a)(4) or (5), and a non-exempt gift from a non-relative takes its value on the day of the gift; hard-fork zero basis as a stated choice; airdrop/staking basis = FMV at receipt.
- **DeFi/income-vs-capital classification.** Staking, liquidity-mining/farming, airdrops, mining, lending interest, income at receipt vs capital on later sale. No 25% "passive" rate for staking: s.121 marginal from 31% under age 60 unless characterised as interest (s.125C: 15% / 25% / marginal). The calculator reports income amounts and deliberately computes no tax on them.
- **Business vs investment determination (badge of trade).** Circular 05/2018 section 3.1.4 does NOT enumerate a test; it delegates to "מבחני עסק כפי שנקבעו **בפסיקה**". Cite the factors as case law. Business classification moves gains to ordinary income (marginal up to 47% plus surtax) and triggers Bituach Leumi and Mas Briut.
- **Mining is business income categorically**, per Circular 05/2018 section 3.1.4, with no scale test.
- **The VAT consequence has three regimes, not one.** Section 3.2.3.2.3 registers a business-level trader as a **מוסד כספי** under Section 4 of the VAT Law; 3.2.3.2.4 registers the **miner** as an **עוסק**; 3.2.3.1 leaves a non-business investor outside VAT. Never state "18% VAT plus osek registration" as the business rule.
- **Surtax (mas yesafim), two limbs with two tests.** 3% on TOTAL taxable income above NIS 721,560; plus 2% only on the part of capital-source income that ITSELF exceeds 721,560 (ITA execution instruction (הוראת ביצוע) 05/2025, examples 2 and 3). A gain stacked on a salary does not get the 2% unless capital income alone crosses the threshold. Threshold fixed 2024-2027. Before 2025 only the 3% limb, which already reached capital gains. The calculator takes --other-income and --other-capital-income.
- **Advance payment (mikdama), Form 1399י, within 30 days of EVERY sale, loss sales included (s.91(d)(1)).** Advance after losses brought forward and earlier same-year losses, less platform withholding. Codes 77 / 71; monthly aggregation with a weighted-average acquisition date per the form's instructions; Form 1399ח for companies.
- **Withholding at source by an Israeli platform.** Ask whether the platform withheld (Bits of Gold 2022 arrangement, status unverified); credit the withholding, and do not pay a second advance on a withheld sale. The December 2024 draft withholding regulations are not in force.
- **Annual return mechanics.** Form 1301 plus the appendices the ITA requires. The 1399י notice within 30 days is the Section 91(d)(1) obligation for an **asset** sale. 1322, 1325 and 1326 are all titled as **ניירות ערך** forms and 1322 is scoped to securities **הנסחרים בבורסה**, so do not assert that crypto belongs on them; the 1301's נספח ג is the traded-securities appendix (field 256), not a crypto one. Form 1344 carries losses brought forward. The salaried-filer exemption for digital assets was a January 2025 **draft** under Section 134A (full withholding by a supervised body, the EXISTING תוספת ו' securities-sale ceiling, and a reported NIS 400,000 holdings cap) and was NOT enacted.
- **Record retention.** Circular 05/2018 section 3.1.3 fixes NO period; it requires documents "ככול שיידרש להנחת דעתו של פקיד השומה". The 7-year figure comes from the bookkeeping directives. Do not attribute it to the circular.

## Should cover (advanced)

- **Exit tax / deemed sale on ceasing Israeli residency, Section 100A.** Must state that **deferral is a deeming rule, not an election** (100A(b) deems a non-payer to have requested it), that the chargeable portion is the **real** gain **measured at realization** apportioned by elapsed time (100A(d)), and that **no interest or linkage accrues during the deferral**, only from realization. The calculator does not model it; relocation scenarios go to a CPA and the aliyah skills.
- **Form 909 bank-refusal payment pathway (Hora'at Sha'a, ITA Instruction 06/2024).** Individual-only NIS payment direct to the ITA's BOI account when a bank refuses crypto-derived funds.
- **Voluntary Disclosure Procedure: CLOSED 31 Aug 2026**, no extension or successor as of 12 Oct 2026. The skill must not imply immunity; the route is a Section 131 correction after advice from a tax-specialist lawyer. Former Green Track figures kept in the regulations reference for applications already lodged.
- **Form 909** extended to 31.12.2027; tax paid under it is not refunded.
- **CARF / automatic exchange.** First exchange **2028** per the OECD Global Forum commitments list (updated 14 Sep 2026). No Israeli implementing legislation, so no domestic collection start date. Re-verify against the current list.
- **Mining / NFT-creator business treatment and deductible costs** (electricity, depreciation), Circular 05/2018; Section 17 deductions.
- **The surtax is not part of the 30-day advance.** Section 121B(b) disapplies Section 91(d) for surtax-chargeable income, and Section 121B(e) excludes the inflationary amount from the surtax base.
- **Section 92 loss mechanics.** Indefinite carry-forward against future capital gains, and within a year each shekel of remaining loss offsets **3.5 shekels** of chargeable inflationary amount. The calculator performs neither offset nor carry-forward.
- **AML provider-side reporting**, distinct from the taxpayer's own duty; the casual-customer shekel ceiling is unverified, so quote none.
- **Pending digital-asset bill** (tabled 19.1.2026, not law): mention only as pending.

## Out of scope (explicit)

Re-litigated 2026-10-12: each row below was checked against "would an ordinary user ask?" and "is it now capturable?".

- Non-Israeli jurisdictions' domestic rules (US 8949, EU, etc.). Mostly asked by olim with US filing; a different skill's job.
- **Foreign-tax credit and treaty relief, Sections 199-210, as a worked computation.** Carried unresolved for five cycles; closed here. An ordinary user rarely has foreign tax paid on crypto gains, the mechanics depend on the treaty and the source rule, and a generic worked example would mislead more than help. The skill names it as a "get professional help" trigger.
- **Derivatives** (futures, perpetuals, options, margin on Binance/Bybit). Common among Binance users, so the skill names them explicitly as uncovered; FIFO spot logic cannot capture them.
- General (non-crypto) income tax computation and payroll. The skill does give the s.121 bracket floor (31% under 60) for crypto income receipts, but computes no marginal tax.
- Full VAT return preparation for crypto businesses (warn + refer, do not compute).
- Corporate-structure / company crypto holdings beyond the 23% rate and Form 1399ח.
- Legal adjudication of whether a specific pattern is a "business" (recommend pre-ruling / CPA; the skill applies the test, it does not decide).
- Securities-law / token-offering regulatory compliance (ISA), as distinct from tax.

## Authoritative sources

- Income Tax Ordinance [New Version] 5721-1961, Sections 2(1), 2(4), 14(a), 28, 88, 91(b)(1), 91(b)(2), 91(c), 91(d), 92, 97(a)(5), 97(b)(1), 100A, 121, 121B, 125C, 131, 134A, 159A, 199-210.
- ITA Circular 05/2018 (virtual-currency classification, mining as business income, VAT regimes, and the s.3.1.5.1 barter and fair-value rule; it prescribes NO cost-basis method and no tax rates); Circular 07/2018 (token issuance).
- ITA execution instruction (הוראת ביצוע) 05/2025 (the 2% capital-source surtax limb, with worked examples).
- ITA Instruction (Hora'at Sha'a) 06/2024 (Form 909 bank-refusal procedure), extended to 31.12.2027 by the notice of 31.8.2026.
- ITA Voluntary Disclosure Procedure, declared 25 Aug 2025, closed 31 Aug 2026.
- Forms 1301, 1320, 1322, 1325, 1326, 1326א, 1344, 1399י, 1399ח, 909, with the ITA's own published titles (see references/crypto-tax-regulations.md).
- Bank of Israel representative rates; Bituach Leumi self-employed rate schedule (btl.gov.il).
- OECD Crypto-Asset Reporting Framework (CARF), first exchange 2028 (per the Global Forum commitments list).
