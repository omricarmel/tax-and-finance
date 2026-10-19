# Changelog

## 1.4.1 - 2026-10-19

### Fixed

- Example 1's US-side bullet said there is no foreign tax credit because Israel taxed nothing. Israeli tax paid on Israeli-source salary above the Hok Iddud cap does generate a credit; only the portions Israel exempts produce none.
- The interactive prompt now repeats that Year 1 counts only income from the residency date.

## 1.4.0 - 2026-10-19

### Fixed

- Step 3 and Step 5 described the 2026 Hok Iddud exemption as covering salary only. Section 1 of the law defines qualifying income as personal-exertion income under Sections 2(1) AND 2(2) of the Ordinance, so Israeli business and self-employment income is covered too. The listed exclusions (interest, dividends, rent, capital gains) were correct.
- Step 5 said the window is for returnees "arriving" between 5.11.2025 and 31.12.2026. The statute and Circular 07/2026 test when the person became an Israeli resident, by the actual center-of-life move, not the landing or certificate date.
- `scripts/cashflow-projection.py` labelled Israeli labour IL-LABOUR ("may be exempt") on every track and for every residency date, so a regular toshav chozer or a 2024 returnee was told Hok Iddud might apply when it cannot. It now marks IL-LABOUR only on the vatik track with a residency date inside the window and only for tax years 2026 to 2030, prints that year's cap (2026 pro-rated by days, as Circular 07/2026 computes it), and marks Israeli labour TAXABLE otherwise.
- The Nefesh B'Nefesh taxation link now points at the page it redirects to.
- Self-employment and employment income are sourced where the work is performed (Section 4A), not where the client or payer is. The skill listed only "business income from Israeli customers" as taxable, so a freelancer serving foreign clients from Israel would have read that income as Section 14 exempt. It is Israeli-source and protected only by the Hok Iddud caps.
- Green-card holders were treated as citizens. A green card keeps US worldwide taxation only until it is abandoned or a treaty-residence position is taken, and a holder with 8 of the last 15 years is a long-term resident whose exit is an IRC 877A expatriation. Step 6 and the script now separate the two.
- Three references still said the Misrad HaKlitah certificate was optional or conferred no tax benefit, contradicting Gotcha 13 and Hok Iddud Section 1. Two references still described the acclimation election as a deferral, and one said it made residency after 1.1.2026 "more attractive", which is backwards for Amendment 272.
- SKILL_HE.md Step 7 still carried the 14-day Form 2409 bank deadline that 1.3.0 removed from the English file as unsourced.
- Gotcha 2's "one day later" example used 30.12.2025.
- The 2026 relative cap (140,000 NIS) is pro-rated like the general cap; "relative" includes a company held 25% or more unless wholly owned.

### Added

- ITA Income Tax Circular 07/2026: in-year relief on Form 116ע with 300,000 / 500,000 NIS caps, the day-count pre-screen for the person and spouse, relative income only through the annual return, and the transparent-entity rules. New `references/hok-iddud-2026.md` holds the full mechanics.
- Section 3 of Hok Iddud, which exempts a foreign employer's Israeli-produced profit arising solely from the returnee's work, unless the returnee is a substantial shareholder.
- The Ordinance's day-count residency presumptions (183 days, or 30 plus 425) in Step 1, previously only in the Form 1348 reference.
- No US-Israel totalization agreement: a US-citizen freelancer can owe both Bituach Leumi and US self-employment tax.
- Example 4, a self-employed returnee from May 2026 with Israeli and foreign clients, and a route to `israeli-freelancer-ops` for Tax Authority, VAT and Bituach Leumi setup.
- The Form 116ע declarations and attachments (including no Bituach Leumi allowances in 2016-2025 and the spouse's entry/exit printout).

### Changed

- `scripts/cashflow-projection.py` now prints one row per TAX YEAR (Year 1 = the residency year, up to Year 11 where the window ends, marked PART-EX), so Hok Iddud caps sit on the right calendar year. The previous anniversary-year rows put every cap one year late for a late-year resident and could show the law in force in 2031. `years_active` indices are now tax years 1-11. A 1 January 2026 resident gets the full 2026 cap.
- The script now marks a post-window capital gain LINEAR-EX instead of TAXABLE, because Section 97(b)(3) keeps the pre-window slice exempt; adds an `acquired_by_gift` field (GIFT-TAX for a s.97(a)(5) gifted asset on the vatik track, and a warning when the field is missing); tells the user to enter only post-residency income in Year 1; and ends a 29 February window on 1 March.
- The frontmatter descriptions now OPEN with the legal clause, and the legal notice's non-recommendation clause extends to foreign-law decisions such as keeping or giving up US citizenship or a green card.
- Company edge cases (CFC, managing a foreign company from Israel) and the Section 14 waiver detail moved to references to keep both files under the word cap.
- The olim credit-point schedule moved from Step 5.5 to `references/section-14-mechanics.md` to keep both skill files under the 5,000-word cap.

## 1.3.0 - 2026-08-27

### Fixed

- Corrected the year-of-acclimation guidance, which said the election defers the start of the 10-year clock. Section 14(b)(2) says the opposite: the acclimation year is counted inside the Section 14(a) exemption period and the Section 97(b)(1) period, so the election buys a year of non-residency, not a year of exemption. It also does not move the Hok Iddud window, because Section 2(e) of that law disapplies Section 14(b)(1) for its own start date, so the previously stated trade-off of sacrificing the 2026 cap was built on a false premise.
- Removed a Hok Iddud offer made to a regular toshav chozer in Example 2. The statute grants those caps only to an oleh or a veteran returning resident.
- Qualified the Misrad HaKlitah certificate note. It still does not establish Section 14 status, but Hok Iddud makes the certificate a precondition to the Israeli-source caps, so a returnee told to skip it can lose that benefit.
- Corrected the Section 35 credit-point taper, which was described as front-loaded when year 1 accrues at the lowest rate; the statutory citation 135(b) to 135(1)(b); and the CFC discussion, which quoted an unsourced 25% test in place of the Section 75B control tests.
- Removed figures no source supported: a "3 years if you left before 1.1.2009" track rule, a 14-day bank deadline for Form 2409, and the framing of 3.1M NIS as tax saved when it is the total of exempt-income caps.

### Added

- Section 97(b)(3): there is no capital-gains cliff at year 10. An asset sold after the window keeps the exemption on the time-apportioned slice of the gain accrued up to the end of the window, so a rushed sale in year 9 or 10 is usually the wrong advice.
- The relief that stops a foreign company being treated as Israeli-resident merely because a veteran returning resident manages it from Israel during the same ten-year window.
- That the Section 14 exemption is waivable, which is the only lever that generates a US foreign tax credit for a US-person returnee.
- An exit-tax pointer on the clawback scenario, noting that deferral under Section 100A(b) is deemed rather than elected and that interest runs only from realization.
- A note that Section 14 is an income-tax exemption and does not cover National Insurance or health-levy contributions.
- The gift and Israeli-linked-asset carve-outs on the capital-gains rows.

### Changed

- `scripts/cashflow-projection.py` now refuses to run on an unrecognised track, an invalid residency date, out-of-range years, or a regular-track stream that does not state whether the asset was acquired abroad. An unrecognised track previously fell through to classifying every stream as taxable, producing a confident wrong projection. Israeli personal-exertion income is now reported as IL-LABOUR with the Hok Iddud caps explained, instead of a flat TAXABLE that contradicted Step 5.

## 1.2.2 - 2026-08-19

### Fixed

- Translated section headings that had been left in English in SKILL_HE.md, where they rendered as-is on the Hebrew page. Hebrew is the site's default locale, and the skill validator never checked the Hebrew file, so these went unnoticed.

## 1.2.1 - 2026-08-13

Corrected the capital-gains section number: the 10-year foreign capital-gains exemption for a toshav chozer vatik is Section 97(b)(1) of the Income Tax Ordinance, not 97(b3) (97(b3) is the non-resident exemption on Israeli securities). Replaced the nevo.co.il/law/84255 short-form links, which resolve to a login wall, with the law_html document of the Ordinance.

All notable changes to this skill are documented here.

## [1.2.0] - 2026-08-09

### Added

- נוסף פרק "הבהרה משפטית" בראש SKILL.md ו-SKILL_HE.md, המפרט מה הכלי עושה, מה הוא אינו, ולאיזה בעל מקצוע מוסמך יש לפנות.

### Changed

- התיאור נפתח כעת בהבהרה קצרה, כך שהיא נראית גם בכרטיס ובתוצאות החיפוש.
