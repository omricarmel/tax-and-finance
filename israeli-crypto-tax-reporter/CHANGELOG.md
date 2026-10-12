# Changelog

## 1.7.1 - 2026-10-12

- Hebrew site description now says "שיעור של עד 25%", matching the 25% ceiling in the body and the English description.
- Calculator: the same-day-acquisitions warning also covers lots bought in earlier years (a newest-first export from a prior December could still reverse FIFO silently); the Hebrew gershayim spelling ש״ח is accepted as shekels.

## 1.7.0 - 2026-10-12

Correctness and currency cycle. The surtax correction changes figures the skill, its calculator and its published checker all printed.

### Corrected
- **Surtax 2% limb**: s.121B(a1) charges 2% only on the part of capital-source income that ITSELF exceeds 721,560, per the ITA's execution instruction (הוראת ביצוע) 05/2025 and its worked examples. The skill, the calculator and the capital-gains checker applied 5% to capital income stacked above a salary, which overstated the surtax for every salaried user (salary 400,000 plus a 700,000 gain: 18,922 printed, 11,353 correct). Business income is not capital-source and bears only the 3%.
- **Pre-2025 surtax**: the 3% limb already reached capital gains before 2025. The calculator used to print no surtax at all for those years; it now applies 3% with the Ordinance's per-year thresholds (2019-2027).
- **Staking and airdrop income**: there is no general 25% "passive" rate. Unless characterised as interest (s.125C), the income is taxed under s.121, from 31% for an individual under 60. The calculator no longer prints a "25% floor" income-tax figure.
- **Advance payments**: s.91(d)(1) requires a 1399י notice on every sale, a loss sale included, and the 1399י loss line counts the current year's losses. The schedule now lists loss sales and nets same-year losses before computing each advance (one disposal per notice, not one row per FIFO lot).
- **Loss offset**: a same-year business loss offsets capital gains (s.28(a)), the opposite of what Scenario 6 said; foreign-asset losses go first against foreign gains (s.92(a)(3)); the unsourced spousal-offset line was removed.
- **Retracted leftovers removed**: the crashing `--currency ILS` command and the "convert to NIS using Bank of Israel rates" step (the calculator converts nothing); the Hebrew examples still routing to 1325/1322; `--form-1325` as the primary command; s.97(a)(5) as a basis rule in Troubleshooting and the checklist; FIFO attributed to Circular 05/2018; "collection from 2026" for CARF, which no Israeli legislation supports.
- **TY2025 paper deadline**: 31 May 2026 after the ITA's extension, not 29 May. Filing guidance now points at the TY2026 return (filed in 2027).

### Updated
- **Voluntary Disclosure**: closed on 31 August 2026 with no extension or successor announced; the open-window branch was retired to the reference file.
- **Form 909**: extended to 31.12.2027, and tax paid under it is not refunded even where losses or credits would have produced a refund.
- **CARF**: OECD list of 14 September 2026 still places Israel in the 2028 group; no domestic implementing legislation.

### Added
- Withholding at source by an Israeli platform (Bits of Gold's 2022 ITA arrangement, current status unverified), so a user does not pay a second advance on a withheld sale.
- The 1399י monthly-aggregation route for many trades, and the 1301 fields 054 and 056.
- Derivatives named as uncovered; the pending digital-asset bill and the Kopel docket in the reference file.

### Calculator
- New surtax engine with both limbs and `--other-capital-income`; `--tax-rate` (which was parsed and silently ignored) removed; JSON gains `advance_notices` and the two surtax limbs; `income_tax_estimate_nis` replaced by `income_events_tax_included: false`.

## 1.6.0 - 2026-08-27

Correctness cycle. Several entries below are retractions of statements earlier versions published as settled.

### Corrected
- **Section 100A exit tax**: deferral is a DEEMING rule, not an election. s.100A(b) deems a non-payer to have requested it, the chargeable portion is the real gain measured at REALIZATION and apportioned by elapsed time (s.100A(d)), and **no interest or linkage differentials accrue during the deferral**.
- **The 30% rate**: s.91(b)(2) charges it on a "נייר ערך בחבר-בני-אדם", a security in a body corporate. A fungible token is not one. The skill no longer applies 30% to an ordinary crypto disposal, and the calculator no longer carries it as a selectable rate.
- **VAT**: Circular 05/2018 s.3.2.3.2.3 registers a business-level crypto trader as a **מוסד כספי** under Section 4 of the VAT Law, NOT as an osek charging 18%. Only the miner is an osek (s.3.2.3.2.4). Earlier versions collapsed three regimes into one wrong one.
- **Mining** is business income categorically per s.3.1.4, with no scale test. The worked scenario's "capital treatment" branch was removed.
- **Reporting forms**: 1322 is scoped by the ITA's own title to securities **הנסחרים בבורסה**, 1325 aggregates securities sales **by tax rate**, and neither carries a נספח label (נספח א belongs to 1320). Crypto disposals go on **1399י**, the notice of an ASSET sale. The "Nispach Gimel" routing is withdrawn.
- **Inflationary amount**: re-cited from 91(b)(3) (which is the non-index-linked bond rate) to Sections 88 and 91(c). 91(c) taxes the chargeable inflationary amount at **10%**, not 0%; it comes out nil for crypto only via s.88's 31.12.1993 cut-off.
- **Section 97(a)(5)** is a gift EXEMPTION, not a basis-carryover rule. The carryover runs through s.88.
- **CARF**: Israel is in the OECD Global Forum's "first exchanges by **2028**" group, not 2027. The earlier "2027-2028" hedge resolved against the primary source.
- **Voluntary Disclosure**: the Green Track digital-asset limb is NIS 500,000 for the ENTIRE disclosure period, not per year. The section is now date-aware, with a post-closure branch, because the window ends 31 August 2026. Its citation moved from a two-paragraph clarification page that supported none of the figures to the ITA announcement that does.
- **ITA Instruction 06/2024** was published 03.04.2024 (updated 22.10.2025), not 31.12.2023.

### Removed
- Three fabricated attributions to Circular 05/2018: the enumerated badge-of-trade factor list (s.3.1.4 delegates to the case law), the Bank of Israel representative-rate requirement (the word יציג does not appear in the circular), and the 7-year retention period (s.3.1.3 fixes none).
- The `--manual-rate` flag and the automatic Bank of Israel rate lookup, both of which the troubleshooting section described and neither of which ever existed.
- An unsourced AML shekel threshold.

### Added
- Section 121B structure: the 3% base limb (a), the 2% capital-source limb (a1), the exclusion of the inflationary amount from the base (e), and that s.121B(b) keeps the surtax **out** of the 30-day advance.
- Section 92 loss mechanics: the 3.5:1 offset against the chargeable inflationary amount, and the s.92(b) condition that a return must have been filed for the loss year.
- Sections 91(d)(2a) and 91(d)(2e): the officer may increase the advance, or extend and reduce it.
- The circular's barter rule (same shekel figure both sides) and its stated-price (מחיר נקוב) override.
- How the gain actually reaches the 1301, since the ITA publishes no crypto appendix.

### Calculator
- A disposal with no matching purchase lot is now **UNPRICED**: no invented zero basis, no invented acquisition date, excluded from every total, surfaced in the JSON, exit code 3. Previously it produced a fabricated zero-basis gain that was invisible on the JSON path.
- Totals are **suppressed entirely** when any disposal is unpriced or any row unrecognised, rather than printing a plausible partial that would get filed.
- Unrecognised transaction types (including Hebrew labels from an Israeli exchange export) are reported and set the report incomplete, instead of being silently dropped into a clean zero-tax report.
- Refuses to compute on negative or zero quantities, on dates before the Bitcoin genesis block, and on future dates.
- Enforces the circular's same-value rule across the two legs of a swap.
- The 2% capital-source surtax limb is no longer applied to pre-2025 tax years, which is exactly the Voluntary Disclosure computation.
- `--form-1325` renamed to `--schedule` (the alias is kept) because the output is not an ITA form 1325; `--schedule` and `--advance-payments` now compose instead of one silently shadowing the other.
- `price_nis` is documented in `--help`, in the skill and at the top of the scenarios file as the TOTAL row consideration, never the per-unit price.

## 1.5.1 - 2026-08-11

Corrected the attribution of the FIFO cost-basis rule and the capital-gains rates. ITA Circular 05/2018, read in full, contains no cost-basis method, no 25% or 30% rate and no retention period; the rates come from Section 91(b) of the Income Tax Ordinance. FIFO is now described as the customary default rather than an ITA mandate, since no source prescribes it.

All notable changes to this skill are documented here.

## [1.5.0] - 2026-08-09

### Added

- נוסף פרק "הבהרה משפטית" בראש SKILL.md ו-SKILL_HE.md, המפרט מה הכלי עושה, מה הוא אינו, ולאיזה בעל מקצוע מוסמך יש לפנות.

### Changed

- התיאור נפתח כעת בהבהרה קצרה, כך שהיא נראית גם בכרטיס ובתוצאות החיפוש.
