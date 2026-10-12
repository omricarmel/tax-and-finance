# Changelog

All notable changes to this skill are documented here.

## [1.3.0] - 2026-10-12

Second review. Every market input was re-checked and is unchanged: the July 2026 country-risk file is still the newest on the data-current index, Moody's still rates Israel Baa1, the corporate rate is 23% for 2026 with no enacted change, the domestic minimum top-up tax applies from fiscal years beginning 1 January 2026 with no income inclusion or undertaxed profits rule, and the surtax threshold is ILS 721,560 for 2026. The work this cycle went into the script and the deal guidance.

### Fixed

- scripts/valuation_model.py printed the whole-company enterprise value range as its headline, below a smaller equity figure, so a reader asking what a 30% stake is worth could quote a number for the wrong thing. The headline range is now the equity value of the stake after the bridge and the discounts, across WACC, terminal growth and the marketability discount. Enterprise value is shown for reference only.
- The script silently defaulted the tax rate to 23%, the exact error the skill exists to prevent for a preferred enterprise. `--tax-rate` is now required.
- Inputs typed as percentages (a discount of 25 instead of 0.25) produced confident absurd figures, including a negative equity value. All rate and discount inputs are now range-checked and rejected with a message saying to use decimals. `--years 0` no longer crashes.
- Negative EBIT printed a full negative valuation and range under a note saying it was meaningless. It now prints no DCF at all and routes to the asset or round-based methods.
- A discount applied to negative equity raised the value. Discounts are no longer applied to negative equity.
- The vintage line claimed the built-in dataset when some, but not all, premia were overridden. It now says the vintages are mixed.
- The equity bridge deducted any severance shortfall unconditionally. Under a full section 14 arrangement there is no company-level shortfall for the insured salary; deposits at 12% without the top-up replace only 72%, and pay above the insured salary keeps its severance right.
- The closely held company reference listed two escape routes from the 2% charge. Section 81ב(ב) has three: the loss-year exclusion (losses above 10% of accumulated profits) is the one summaries drop.
- The Gotchas called the overstatement from applying 23% to the lowest preferred rates "roughly threefold"; against 5% it is more than fourfold. Both files and the tax-regimes reference now say three to more than four times.
- The excess-profitability formula under section 62א(א1) started from gross income from personal-exertion-intensive activity. The statute starts from TAXABLE income and deducts 25% of that income less related-company payments; the old wording overstated the attribution for any company with real costs.
- The officer and management-services limb of section 62א(א)(1) dropped its condition that the individual or the company was an officer of the other body.
- Preferred Technology Enterprise eligibility was described as four cumulative conditions with the R&D test always required. Section 51כד has two routes, R&D test plus a secondary test OR Innovation Authority approval, and on the second route the R&D test does not apply.
- The Approved and Beneficiary Enterprise rows said "pre-2017" and tied the 15% dividend withholding to an election year before 2014. Those regimes closed with the 2005 and 2011 amendments, and the 15% applies to dividends from benefits-period profits distributed during that period or the following 12 years. The 2014 switch from 15% to 20% belongs to the Preferred Enterprise regime.
- The country-risk dataset was described as refreshing in January and July. It updates at least that often and sometimes in between (there was an April 2026 file). The script now measures staleness from the date a reviewer last confirmed the file is still the newest (90-day window), not from the file's vintage, and points to the data-current index.
- The company self-purchase passage said a distribution may be made only out of profits. Section 303 lets a court approve one that fails the profit test where the solvency test is met.
- The Companies Law personal-interest approval track was applied to any sale to an officer or controlling shareholder. It governs transactions of the company, such as a buyback, not a plain sale between shareholders.
- The legal notice was the tax template unchanged and never mentioned the valuation. It now says what the tool builds, names the accountant, valuer and lawyer it replaces none of, lists what it does not do, and says that reading a shareholders' agreement is for valuation inputs only. The script now prints the full two-paragraph scope limit before any figure as well as after.
- In the script, a country premium passed in the convention that ignores it was printed as if it had been used, and the vintage was labelled mixed. That combination is now rejected with a message naming the right flag. A capex-heavy company with positive EBIT but negative terminal free cash flow got a negative valuation presented as a range; it now gets no DCF. Stake values floor at zero. The capital structure no longer defaults silently to 30% debt.
- The scope limit called the output "not admissible" to the Tax Authority or a court. Nothing bars submitting it; the point is that it is not fit to submit. Reworded in both files and in the script.

### Added

- `--stake`, `--nol` (carried-forward losses shelter the explicit years only; the terminal value stays fully taxed), `--exit-multiple`, an implied exit EV/EBITDA on every run, and warnings for unsupplied risk premia, WACC debt with no net debt in the bridge, growth with no reinvestment, and a range whose high end is more than twice its low end.
- Step 3 now starts from operating profit rather than profit before tax, and replaces a departing partner's draw with a market replacement cost.
- Step 4 covers carried-forward business losses under section 28, and the change-of-control restriction that comes from case law on section 86 rather than from section 28 itself.
- A buyer-side section in the transaction reference (inherited tax history, warranties and indemnities, non-compete, guarantees, financing), the company self-purchase route, which the Companies Law treats as a distribution subject to the profit and solvency tests, and retained earnings in the price, including section 94ב for a corporate seller. Mirrored in the Hebrew reference.
- The factors that place a marketability discount (buyer pool, transfer restrictions, distribution history, holding period, block size) and the international study families behind it, a caution that listed sector multiples are an upper bound for a small owner-managed business, and a purchase price allocation note for a consolidating buyer, in references/valuation-methods.md and its Hebrew twin.
- The excess-profitability reference now carries the section 62א(א1)(2) carve-outs: a partnership share under 10%, and the exclusion for a company whose controllers control no other company and whose accumulated profits are at most ILS 750,000.
- The company-buyback route now explains the בית חוסן ruling (ע"א 9308/20): in a quasi-partnership a buyback is taxed as a dividend to the remaining shareholders and a purchase by them, so the partner who stays can owe tax. Company financing of a purchase is a distribution too.
- A full Hebrew twin of the methods reference, references/valuation-methods-he.md, which SKILL_HE.md now routes to; the English file is English-only.
- Transfer pricing now names section 85א and the 2006 market-conditions regulations, and the share-versus-asset fork covers VAT, the buyer's cost base, and real estate taxes in an asset sale.
- A documentation benchmark in references/valuation-methods.md, in both languages: regulation 8ב of the Securities Regulations, the closest statutory list of what a valuation discloses.
- Sourced the long-standing claim that Israel has no licensing statute for business valuers, and recorded in the domain checklist that valuing private-company shares falls outside the Investment Advice Law, whose definition of securities excludes unlisted ones.

### Changed

- The real estate association detail moved from Step 7 into the transaction reference, the Section 104 passage was shortened to what the reference does not already say, and the reorganization gotcha it duplicated was removed, to stay under the word cap.

## [1.2.0] - 2026-08-26

First review since publication.

### Fixed

- Refreshed the Israel country-risk inputs from the January 2026 vintage to the July 2026 one: adjusted default spread 1.36% to 1.27%, country risk premium 2.07% to 1.98%, total equity risk premium 6.30% to 6.18%. The Moody's rating is unchanged at Baa1, so the move is CDS repricing, not a downgrade. Figures read directly from the published dataset file.
- Vintage checks now point at the data-current index. The country-premium landing page kept advertising the January file after the July one was published, so a check made there confirms a stale vintage and looks like verification. Corrected in both languages, in the prose AND in both Reference Links tables.
- Corrected the Pillar Two passage. Israel enacted a domestic minimum top-up tax only, with no income inclusion rule and no undertaxed profits rule, so it tops up Israeli low-taxed profit rather than a group's foreign profit. The 15% is a floor, not a cap, and the earlier wording called it a ceiling.
- Corrected the closely held company rules to the statute: sections 81א-81ו for the 2% charge (base is accumulated profits less the highest of three shields, and Encouragement-Law-sourced profits are outside it), section 62א(א1) for excess profitability (25% is BOTH the entry trigger and the deducted normal return, subject to an ILS 30 million per-controlling-shareholder ceiling), and section 62א(א) for attribution. The 25% escape belongs to the officer and management-services limb, not to the 70% limb, and the 70% limb has its own four-employee exclusion in section 62א(א)(5) and a 22-of-36-months duration test.
- Corrected the newly added real estate association passage. A sale of shares in an איגוד מקרקעין changes the charging statute, adds purchase tax on the buyer, and removes ordinary capital-gains apportionment, but section 48א(ב) charges the individual at the SAME 25% and 30% ladder. An earlier draft of this update wrongly said those rates do not govern.
- Three bugs in scripts/valuation_model.py. Staleness suppression keyed off a parameter that does not drive the number, so passing a fresh country premium alone silenced the warning while the stale total premium still set the cost of equity. The vintage line kept asserting the built-in vintage after an override. Guard-rail ValueErrors printed a traceback instead of their own message.

### Added

- Preferred Technology Enterprise eligibility now carries the competitiveness test and the secondary tests (R&D headcount, venture funding, revenue growth, headcount growth, or Innovation Authority certification). A company clearing revenue and R&D alone does not qualify, and the earlier text implied it did.
- The pre-2017 Approved and Beneficiary Enterprise regimes, which still govern older companies at different rates and a 15% dividend withholding.
- A primary-versus-secondary distinction with pre-money and post-money arithmetic. Selling a stake to an investor usually means issuing new shares, in which case the money goes to the company and there is no capital gains event for the owner at all.
- Section 3(ט1) shareholder debit balances in the equity bridge, including the ILS 100,000 de minimis.
- The additional 2% surtax on capital-source income, taking a substantial shareholder's top slice to 35%.
- A Section 104 section in references/transaction-and-sale-he.md, which the Hebrew reference file was missing entirely while its English twin carried it.

### Changed

- The size premium is now presented as contested rather than as an omission that would be an error.
- Moved the discount-rate components, the levels-of-value ladder, the Section 104 detail and the share-sale mechanics into references/ to stay under the validator's word cap.

## 1.1.1 - 2026-08-13

Moved the Troubleshooting section to references/ to bring SKILL.md under the 5,000-word validator cap, which it had been exceeding. No content was removed.

## [1.1.0] - 2026-08-09

### Added

- נוסף פרק "הבהרה משפטית" בראש SKILL.md ו-SKILL_HE.md, המפרט מה הכלי עושה, מה הוא אינו, ולאיזה בעל מקצוע מוסמך יש לפנות.

### Changed

- התיאור נפתח כעת בהבהרה קצרה, כך שהיא נראית גם בכרטיס ובתוצאות החיפוש.
