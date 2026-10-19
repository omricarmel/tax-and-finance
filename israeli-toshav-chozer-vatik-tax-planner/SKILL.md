---
name: israeli-toshav-chozer-vatik-tax-planner
description: Not tax advice and not a filed return. Plans Section 14 tax exemption for an Israeli toshav chozer vatik (10+ years abroad). Distinguishes vatik (full 10-year foreign-income exemption) from regular toshav chozer (5-year passive + 10-year capital gains only), pins the 10-year clock to the tax-residency date (not arrival), surfaces the 2026 reporting change (Amendment 272 cancels 134b + 135(1)(b); tax stays exempt, reporting required for residents from 1.1.2026), flags the US-citizen dual-tax trap, and outputs a 10-year cash-flow projection. Triggers on "תושב חוזר ותיק", "סעיף 14", "פטור 10 שנים", "תיקון 272". Do NOT use for the returning-resident process (use israeli-returning-resident-navigator), vehicle/customs (use israeli-returning-resident-customs-vehicle), olim chadashim (use israeli-aliyah-navigator), or people leaving Israel (use israeli-relocation-abroad). Planning aid only.
license: MIT
---

# Israeli Toshav Chozer Vatik Tax Planner

## Legal notice

This is a free information tool operated by an AI model. It explains the tax rules and helps you organise your own figures. All of its outputs are produced automatically by an AI model, with no involvement, review, or approval by a tax adviser or accountant. The output is not a tax opinion, not a return prepared by a licensed representative, and not professional advice, but a general calculation and explanation only: it does not examine the full extent of your income or your complete documents. An AI model may err, omit data, or present a wrong conclusion.

Any form or text this tool produces is an automatic draft for your personal preparation only, and is not a filed return. Responsibility for reporting and for paying the tax is yours, the binding computation is the Tax Authority's, and representation before the Tax Authority is reserved to those permitted by law. This tool is not a substitute for advice that takes account of the particular circumstances and needs of each person. Consult a tax adviser or accountant before filing or paying. This tool is also not a recommendation to sell, to hold, or to time the sale of any asset, and not a recommendation to claim or to waive any exemption, benefit, or election under the Income Tax Ordinance or under foreign law, including keeping or giving up US citizenship or a green card; decisions of that kind are irreversible and must be reviewed with a tax adviser or accountant, or a US tax professional, before they are made. All use of its output is the user's sole responsibility.


## Problem

Returning Israelis with 10+ years abroad get the Section 14 exemption, but four points keep tripping people up. First, vatik (10+ years, full exemption) and regular toshav chozer (6-10 years, only passive income for 5 years) are often confused. Second, the 10-year clock starts on the date the user becomes an Israeli tax resident again, NOT on the date they land at Ben Gurion, and these dates can be months apart. Third, Amendment 272 took effect on 1.1.2026: the TAX exemption stays, but the REPORTING exemption was canceled. Vatikim who settled on or after 1.1.2026 must now disclose foreign income and assets to Mas Hachnasa even though no tax is owed. Fourth, US citizens (the largest single returnee cohort, from CA and NY) still owe US tax on the same income Israel exempts; the US-Israel treaty saving clause blocks treaty relief and there is no foreign tax credit because no Israeli tax was paid.

Planning aid, not binding tax advice; final filings go through a CPA.

## Instructions

### Step 1: Identify the track

Ask the user, in this order:

1. **How many consecutive years were you a foreign tax resident immediately before returning?** Foreign tax resident means center-of-life outside Israel under the Ordinance (not just "I lived abroad").
   - **10 or more, continuous**: **vatik** track.
   - **6 to 9**: **regular toshav chozer** track. (Older transitional rules that granted vatik status on fewer years applied only to people who became resident in tax years 2007-2009 and are spent for any current returnee. Do not apply them.)
   - **Fewer than 6**: no track. Section 14 does not apply. Stop here and recommend a CPA.

2. **Was the foreign residency continuous?** A multi-month return to Israel during the 10-year window (family moved, kids enrolled in Israeli schools, primary home shifted) can break the chain. Short visits do not. Borderline cases need CPA review.

3. **When did you become an Israeli tax resident again?** Pin a calendar date for center-of-life shifting back to Israel. This is the start of the 10-year clock.
   - Common signals: family moved, kids enrolled in school, primary home shifted, foreign work contract terminated.
   - Physical arrival date can differ by months. Document both.
   - The Ordinance also presumes residency on day counts (183+ days in the tax year, or 30+ days in the year and 425+ across that year and the two before it). The presumption is rebuttable, but it is how the Tax Authority will first read the dates; see `references/form-1348-fields.md`.

4. **Do you hold US citizenship, a US green card, or citizenship of any country that taxes worldwide income?** Ask citizenship and green card separately, because they diverge (Step 6). If either, flag the dual-tax trap and route the user to a US-Israel cross-border CPA.

### Step 2: Apply the right exemption matrix (Israeli tax only)

| Income kind | Source | Vatik | Regular toshav chozer | No track |
|---|---|---|---|---|
| Active (employment, business) | Foreign | Exempt 10 years (Section 14) | Taxable from day 1 | Taxable |
| Passive (dividend, interest, rent, royalty) | Foreign | Exempt 10 years (Section 14) | Exempt 5 years (only if asset acquired during the period abroad) | Taxable |
| Capital gain | Foreign | Exempt 10 years (Section 97(b)(1)) | Exempt 10 years (only if asset acquired during the period abroad and not Israeli-property-linked) | Taxable |
| Any | Israeli | Taxable | Taxable | Taxable |

**Source is where the work is done.** Under Section 4A, business income is sourced where the income-producing activity takes place, professional income where the service is performed, and employment income where the work is performed, whatever the client's or payer's location. A self-employed returnee serving foreign clients from Tel Aviv has ISRAELI-source income: Section 14 never covers it, only the Step 5 caps do.

This matrix is ISRAELI INCOME TAX only. Section 14 does not exempt National Insurance and health-levy contributions, assessed on a resident under the National Insurance Law independently of it, so a projection full of EXEMPT rows is not a projection of zero cost (see `israeli-returning-resident-navigator`). US citizens see Step 6.

**There is no capital-gains cliff at year 10.** Under Section 97(b)(3), if the foreign asset is sold AFTER the ten years the exemption is not lost: the real gain splits on a straight time basis, the part accrued from acquisition to the end of the window stays EXEMPT, and only the remainder is taxed under Section 91(b). The exempt share is (acquisition to end of the 10 years) divided by (acquisition to sale). So do NOT push a user in year 9 or 10 into a rushed sale: that can crystallise US tax (Step 6) and, on a losing position, destroy the loss under Gotcha 12.

**Two carve-outs on the capital-gains rows.** For the vatik row, an asset received under the Section 97(a)(5) tax-exempt gift route (from 1.1.2007) is excluded. For the regular-track row, the asset must not be, directly or indirectly, a right to property located in Israel, so a foreign company holding Israeli real estate does not qualify.

Edge cases to flag (always defer to a CPA):
- **CFC dividends**: dividends from a foreign company the returnee controls can lose the exemption. Do not quote a percentage test; Section 75B has control, passive-income and foreign-tax-rate limbs. CPA review. See `references/section-14-mechanics.md`.
- **A foreign company you manage from Israel does NOT automatically become Israeli-resident.** The "Israeli resident" definition excludes a company controlled and managed in Israel by a vatik within the ten years, unless it asks otherwise. But its profit from your work in Israel is still Israeli-source (Section 4A), Hok Iddud Section 3 is denied to a substantial shareholder, and the relief ends at year 10. Detail in `references/section-14-mechanics.md`.
- **Trust distributions** where the returnee is settlor or beneficiary.
- **Mixed-source income** where part of the work was performed in Israel: the exemption is pro-rated.
- **Equity compensation (RSU, options)**: sourced by where the work was performed during the VESTING period, NOT by grant date. See `references/equity-compensation-sourcing.md`.

### Step 3: Israeli-source income is always taxable

The vatik exemption is FOREIGN-source income only. Throughout the 10-year window the returnee pays normal Israeli tax on:

- Israeli salary (subject to the 2026 labor caps in Step 5)
- Israeli rental real estate
- Israeli TASE securities trading and Israeli mutual funds
- Israeli dividends and Israeli interest
- Business or professional income from work performed in Israel, for Israeli or foreign clients alike (Section 4A); it may fall under the Step 5 caps

A returnee planning to trade TASE from day one needs to know this.

### Step 4: Apply the 2026 reporting rule

Compare the user's Israeli tax-residency start date (from Step 1) to **1 January 2026**:

- **Residency started before 1.1.2026**: legacy regime. Foreign income remains both EXEMPT and NOT reportable for the rest of the 10-year window. They keep the old "no Form 1301 for foreign income" treatment.
- **Residency started on or after 1.1.2026**: Amendment 272 applies. Foreign income remains EXEMPT but must be REPORTED annually:
  - Form 1301 (annual return).
  - Nispach D-1 (Schedule D-1) listing foreign income.
  - Hatzharat Hon (capital declaration) when the Tax Authority requests one.
  - Trust + CFC disclosures if applicable.

**Trustee-level reporting (new, separate from beneficiary reporting).** Amendment 272 also imposes a NEW reporting obligation on **Israeli-resident trustees** of foreign trusts whose beneficiaries are vatik or oleh, even when the trust stays exempt. A returnee who is also a trustee of a family trust must check this separately (Shibolet writeup in Reference Links).

For background, read `references/2026-reporting-change.md`.

### Step 5: Apply the 2026 Hok Iddud Israeli-source personal-exertion cap

Separately from section 14, the 2026 חוק עידוד עלייה לישראל וחזרה אליה (הוראת שעה), התשפ"ו-2026 exempts an oleh or a toshav chozer vatik who **became an Israeli resident** in the window 5.11.2025 to 31.12.2026 on ISRAELI-source personal-exertion income (Sections 2(1) and 2(2): employment AND business or profession income, so self-employed income from work performed in Israel counts too, for Israeli or foreign clients alike), up to annual caps:

- 2026: 600,000 NIS (pro-rated to the part of 2026 the person was resident)
- 2027: 1,000,000 NIS
- 2028: 1,000,000 NIS
- 2029: 350,000 NIS
- 2030: 150,000 NIS

The window is tested by when the center of life actually moved, not by the landing date or the certificate date, and an acclimation-year election does not move it (Section 2(e), confirmed in ITA Circular 07/2026). A regular toshav chozer does not qualify. For a 2026 returnee with high Israeli earnings this is the biggest lever.

What to tell the user, in short (full mechanics, examples and sources in `references/hok-iddud-2026.md`):

- **Not covered**: interest, dividends, rent, capital gains (all "other income" under Section 62A(d)), and income attributed from a transparent entity in which the person is a substantial shareholder. A returnee who pays themselves a dividend expecting the 600K shield gets none of it.
- **Income from a relative** is capped at 140,000 NIS a year for 2026-2029 (pro-rated in 2026 like the general cap) and can be claimed only in the annual return. "Relative" follows Section 88, which includes a company the person holds 25% or more of, so salary from your own partly-owned Israeli company is relative income; only a wholly-owned company is carved out.
- **During the year** the exemption comes through tax coordination or reduced advances on Form 116ע, capped at 300,000 NIS (not registered as an annual filer) or 500,000 NIS (registered as an annual filer when applying, which a self-employed person with an open file normally is), pro-rated in 2026; the balance is claimed in the annual return. In-year relief also requires a day-count pre-screen for the person AND the spouse over 2016-2025 (a 90-day rule with limited exceptions, plus a three-year 425-day test). Failing it, or any other Form 116ע declaration (for example, that no Bituach Leumi allowance was received in 2016-2025), blocks only the in-year relief, not the annual claim.
- **Working from Israel for a foreign employer**: Section 3 exempts the foreign company's Israeli-produced profit that arises solely from the returnee's work, unless the returnee is a substantial shareholder in it.
- **Clawback (Section 4)**: the whole law stops applying, from its start, to a person who BOTH ceases to be an Israeli resident in 2028 or 2029 AND stays in Israel fewer than 75 days in one of those years. That voids the 2026-2027 exemptions already taken. Ceasing residency also triggers the Section 100A exit tax, a deemed sale on the last day of residency (the deferral is deemed requested by a non-payer under Section 100A(b), and no interest or linkage accrues until realization); see `israeli-relocation-abroad` and `israeli-digital-nomad-navigator`. 2026 and 2027 carry no presence test.
- The caps total 3.1M NIS of EXEMPT INCOME across 2026-2030, not 3.1M NIS of tax. The exemption is waivable in whole or in part. It is an income-tax exemption only: the law says nothing about National Insurance or health levy, so self-employed setup (opening files with the Tax Authority, VAT and Bituach Leumi) goes to `israeli-freelancer-ops`.

### Step 5.5: Olim credit points (only if the returnee is also an oleh)

**Scope trap first:** the additional immigrant **tax credit points** (nekudot zikui) are an **olim chadashim** benefit under Section 35 of the Income Tax Ordinance. A **toshav chozer vatik who is a returning Israeli citizen (not an oleh) does NOT automatically receive them.** Do not promise a pure returning-citizen vatik these points. A person who holds oleh status AND meets the vatik years-abroad test gets both section 14 and the olim credit points; a returning citizen gets only section 14.

For an oleh, the points accrue over 54 months under a schedule that is NOT front-loaded (year 1 is the lowest), each point is worth 2,904 NIS/year in 2026, and they apply against Israeli-source tax left after the Step 5 exemption, for example on salary above the cap. The schedule and a worked example are in `references/section-14-mechanics.md`.

### Step 6: Special case, US citizens (and other global-taxation citizenships)

If the user holds US citizenship or a US green card, the section 14 exemption does NOT relieve them from US tax. The US taxes citizens on worldwide income. The US-Israel income tax convention (signed 1975, amended by the 1980 and 1993 protocols, generally effective from 1 January 1995) contains a saving clause at Article 6(3) that lets the US tax its citizens "as if this Convention had not come into effect." Because no Israeli tax was paid on the section 14 exempt income, there is also NO foreign tax credit (FTC) available on the US side.

So a US-citizen vatik owes full US tax on foreign dividends, interest and gains that Israel exempts; the net Section 14 benefit there is close to zero.

The same applies to any country that taxes citizens regardless of residence (Eritrea, edge cases). Canada, the UK and the EU tax on residence and stop once Israeli residency is established.

**The exemption is waivable.** Section 14(a) grants it "unless they requested otherwise", and Hok Iddud Section 2(a) uses the same words. Paying Israeli tax generates a US foreign tax credit, which the exemption never does, so waiving all or part can beat claiming it. That is a CPA calculation, not a default, but never present the exemption as unavoidable. Detail in `references/us-citizen-dual-tax.md`.

**Green-card holders are not citizens.** A green card keeps US worldwide taxation only until it is formally abandoned (Form I-407) or the holder takes an Israeli treaty-residence position and notifies the IRS. But a holder with permanent residence in at least 8 of the last 15 tax years is a long-term resident, and ending that status is an expatriation under IRC 877A (Form 8854, possible covered-expatriate exit tax). A 12-years-in-the-US returnee is usually in that group, so neither keeping nor dropping the card is a default (and the I-407 itself is a question for US immigration counsel).

**Self-employed US persons.** The US has no totalization agreement with Israel, so a US-citizen freelancer living in Israel can owe Bituach Leumi AND US self-employment tax on the same profit.

If the user is a US person: STOP recommending section 14 as an automatic planning win and route them to a US-Israel cross-border CPA before any major event (RSU vest, sale of US assets, retirement-account distribution). Continued US compliance (Form 1040, Schedule B, Form 8938, FBAR, Form 5471 if controlled-foreign-corporation, Form 3520 for foreign trusts) remains mandatory throughout the 10-year window.

Read `references/us-citizen-dual-tax.md` for the full mechanics.

### Step 7: Clarify the form question

"Do I file Form 1348?" No: it is for people LEAVING Israel (Gotcha 5). Returnees file Form 1301 + Nispach D-1, and an Israeli bank may ask for Form 2409 on an incoming foreign-currency deposit; ask the bank for its own deadline, it is not statutory. See `references/form-1348-fields.md`.

### Step 8: Build the cash-flow projection

Run `scripts/cashflow-projection.py` either interactively or with a JSON input that lists each income stream:

```bash
python3 scripts/cashflow-projection.py
# or
python3 scripts/cashflow-projection.py --json my-plan.json
```

The script prints one row per TAX YEAR from the residency year (Year 1, usually partial: enter only income earned from the residency date) through the year the window ends (PART-EX), then the reporting reminder for the residency date and a US warning that differs for citizens and green-card holders. EXEMPT and TAXABLE classify FOREIGN income. For active income, `source` is where the work is done (Section 4A), so work in Israel for a foreign client is `israeli`. Israeli personal-exertion income is IL-LABOUR (Section 14 never exempts it, the Step 5 caps may) only on the vatik track, with a residency date inside the Hok Iddud window, in tax years 2026 to 2030, with that year's cap printed; otherwise TAXABLE. A capital gain on a qualifying asset sold after the window is LINEAR-EX (Section 97(b)(3)), and a gifted asset on the vatik track is GIFT-TAX. The script refuses an unrecognised track, a bad residency date, or a regular-track stream that does not say whether the asset was acquired abroad. It does NOT compute tax owed and does NOT compute US tax.

### Step 9: Hand off to a CPA

Always close by recommending a CPA before any filing. What to bring: years-abroad documentation; the residency start date with evidence; the Population Authority entry/exit printout for you and your spouse; an income-stream inventory (where the work was done, kind, amount, currency, asset acquisition dates, equity vesting calendars); trust and CFC documents; and US status with US filing history.

## Examples

### Example 1: Software engineer returning Q1 2026 from 11 years in the US

User: returned to Israel on 15 March 2026. Has been in California for 11 years, working at a US company. Holds US citizenship (born in the US). Wants to know what changes for him vs. someone who returned in 2025.

Reasoning:
- 11 years foreign-resident, continuous: **vatik** track on the Israeli side.
- If center-of-life shifted to Israel on 15.3.2026, that is the start of the 10-year clock. Clock runs 15.3.2026 to 14.3.2036.
- Residency started AFTER 1.1.2026: Amendment 272 applies, foreign income is exempt but must be reported.
- **US citizen**: Step 6 applies. Israeli exemption on foreign income does not relieve US tax.

Output (Israeli side, then US-side note):

- **US W-2 salary** (if he keeps working remotely for the US company, work performed in Israel after the move): mixed-source. The portion performed in Israel is **Israeli-source, taxable** (subject to the 2026 Israeli-source labor cap from Step 5: 600,000 NIS exempt in 2026, proportional). The portion performed in the US before the move is **foreign-source active income, exempt 10 years** on the Israeli side.
- **US 401(k) distribution received in 2027**: foreign passive, **exempt 10 years** on the Israeli side.
- **US RSU vest 2028, granted in 2024 before the move, 4-year vest schedule**: do NOT treat this as a clean foreign capital gain. The Israeli sourcing depends on where the work was performed during the vesting period (see `references/equity-compensation-sourcing.md`). The portion of the vest that vested on work performed in Israel (after 15.3.2026) is **Israeli-source ordinary income, taxable**. The portion that vested on work performed in the US (before 15.3.2026) is **foreign-source ordinary income, exempt 10 years** under section 14. Engage a CPA with a calendar of the vesting period and a workdays-by-location log.
- **All three exempt streams above must still be reported** annually on Form 1301 + Schedule D-1 (Amendment 272).
- **Form 1348? No.**
- **US side**: all of the above stay taxable on Form 1040 under the saving clause, with no FTC since Israel taxed nothing. Engage a US-Israel cross-border CPA before the 2028 RSU vest.

### Example 2: Doctor returning from Germany after 8 years

User: returned after 8 years in Germany. Has German investment account with stocks bought 5 years ago, and works at an Israeli hospital after the return. German (not US) citizen.

Reasoning:
- 8 years foreign-resident: **regular toshav chozer** track (not vatik).
- No vatik benefits. Only passive-on-foreign-assets-acquired-abroad (5 years) + capital gains on those assets (10 years).
- Germany taxes based on residence; once Israeli tax residency is established the German tax stops. No saving-clause issue.

Output:
- Israeli hospital salary: **taxable from day 1** on the Israeli side. The Hok Iddud Israeli-source labour cap (Step 5) is **NOT available to her**: the statute grants it only to an oleh or a toshav chozer vatik, and she is on the regular track. Do not raise the 600K cap with a regular toshav chozer.
- Dividends from German stocks (acquired during the 8 years abroad): **exempt for 5 years**, then taxable.
- Capital gain when she eventually sells the German stocks: **exempt for 10 years**.

### Example 3: Pre-2026 returnee asking what to file for tax year 2027

User: became Israeli tax resident on 1 June 2024, vatik track. Israeli citizen only.

Output:
- Residency began before 1.1.2026, so the legacy regime runs for the whole window: foreign income is exempt AND not reportable through 1 June 2034, including for tax year 2027.
- Not eligible for the Step 5 caps: residency began before the 5.11.2025 window.
- After 1 June 2034 foreign INCOME becomes taxable and reportable. But a foreign ASSET sold after that date is not fully taxable: Section 97(b)(3) still exempts the slice of the gain accrued up to 1 June 2034 (see Step 2). Do not advise a rushed pre-2034 sale.

### Example 4: Self-employed returnee from May 2026, Israeli and foreign clients

User: became Israeli tax resident on 10 May 2026 after 12 years in the US, Israeli citizen only, freelances from Tel Aviv for Israeli and US clients.

Output:
- Vatik track. Inside the Hok Iddud window, so the Misrad HaKlitah certificate matters (Gotcha 13).
- ALL the freelance income is Israeli-source, including the US clients, because the work is performed in Israel (Section 4A). Section 14 exempts none of it. Hok Iddud can exempt it, if she meets its conditions, up to 600,000 NIS pro-rated for 2026, then 1M, 1M, 350K, 150K; fully taxable from 2031.
- In-year relief: she asks for reduced advances on Form 116ע (the 500,000 NIS tier once her file is registered as an annual filer, pro-rated for 2026) and claims the rest in her annual return.
- Foreign passive income and gains: exempt to May 2036, reportable under Amendment 272.
- Bituach Leumi and VAT setup: `israeli-freelancer-ops`.

## Bundled Resources

### References

- `references/domain-checklist.md`: what is in/out of scope, with source URLs.
- `references/section-14-mechanics.md`: eligibility, what is exempt, the clock, the year-of-acclimation election, capital-loss matching, 2026 labor cap.
- `references/equity-compensation-sourcing.md`: vesting-period sourcing for RSUs and options, ITA principle.
- `references/us-citizen-dual-tax.md`: the US worldwide-tax trap, treaty saving clause, FTC limitations.
- `references/form-1348-fields.md`: why Form 1348 is NOT the form for returnees, and what they actually file.
- `references/2026-reporting-change.md`: Amendment 272 details (sections 134b + 135(1)(b), effective date, threshold).
- `references/hok-iddud-2026.md`: the 2026 Israeli-source exemption, caps, Circular 07/2026 in-year relief and day-count pre-screen, the foreign-company limb, the clawback.

### Scripts

- `scripts/cashflow-projection.py`: tax-year-by-tax-year exempt-vs-taxable classifier with Hok Iddud caps, the reporting note and citizen / green-card warnings.

## Recommended MCP Servers

None. This skill is text-based planning. No live API integration with Mas Hachnasa exists for individual returning-resident filings.

## Gotchas

1. **Clock start date is NOT arrival date.** The 10-year exemption clock starts when center-of-life shifts to Israel, which can lag (or precede) the physical landing by months. Pin the date with documentation.
2. **Residency-date rule for the reporting change.** A returnee whose Israeli tax-residency commenced on 31.12.2025 keeps the legacy "no reporting" treatment for the full window. One day later (1.1.2026) and Amendment 272 kicks in.
3. **Vatik vs. regular is widely confused.** 6-9 years gets a much narrower benefit (5 years on passive only, capital gains on acquired-abroad assets only, never active income). Many online guides treat them as the same. They are not.
4. **CFC and trust traps.** Foreign companies the returnee controls, and foreign trusts where they are settlor or beneficiary, can pierce the exemption. The Section 75B tests are not a simple ownership percentage (Step 2), so flag the structure for CPA review rather than applying a threshold yourself.
5. **Form 1348 is not your friend.** It belongs to Israelis LEAVING Israel. Returnees file Form 1301 + Schedule D-1. Do not file 1348 unless arguing non-residency for a pre-return part-year.
6. **US citizens still owe US tax on Israeli-exempt income.** The saving clause (Article 6(3)) lets the US tax citizens as if the treaty did not exist, and there is no FTC because no Israeli tax was paid. Note the Section 14(a) opt-out (Step 6) is the one lever that changes this. Route every US-person returnee to a cross-border CPA.
7. **RSUs and stock options are sourced by VESTING period, not grant date.** The part vesting on work done in Israel is Israeli-source and outside Section 14.
8. **Shnat Histaglut does NOT buy an extra exempt year.** File within 90 days of arrival via Form 1130; irrevocable. The 90 days run from arrival, so a returnee who arrived earlier in the year may already be past it. It treats year 1 as non-resident, useful for a try-before-commit returnee. But Section 14(b)(2) says the acclimation year **is counted** toward the periods it lists, expressly including the Section 14(a) exemption and the Section 97(b)(1) period, so the clock is not pushed to year 11. And Hok Iddud Section 2(e) disapplies Section 14(b)(1) for its own start date, so electing acclimation neither postpones the Israeli-source caps nor forfeits the 2026 one. The real trade-off is residency optionality, not clock extension.
9. **Israeli-source income is fully taxable throughout the 10-year window.** Section 14 exempts FOREIGN income only. TASE trading, Israeli rentals, Israeli salary above the 2026 labor caps, Israeli dividends: all taxed at normal Israeli rates.
10. **Spouse not eligible for vatik.** Marrying a returnee does not make an Israeli who never left a vatik. Joint filing (תיק מאוחד) can drag exempt income into the household calculation in non-trivial ways. The interaction with the spouse's Israeli filing is complex; consult a CPA.
11. **Center-of-life break during the 10-year abroad window can disqualify vatik.** The 10 years of foreign residency must be CONTINUOUS. A 13-month sabbatical back in Israel (family there, kids in Israeli schools) can reset the clock, dropping the returnee to regular track or none. Short visits do not break continuity; multi-month center-of-life shifts can.
12. **Capital losses during the exempt window are NOT carry-forwardable.** Foreign capital losses incurred during the 10-year window cannot be offset against later (post-window) gains. Section 92 matching: a loss is offsettable only if the matching gain would have been Israeli-taxable, and inside the window it would have been exempt. ITA Circular 10/2025 confirms this. Big trap for crypto and stock-heavy years.
13. **The Misrad HaKlitah certificate does not establish Section 14 status, but DO get it.** It is not proof of Section 14 eligibility, which the Tax Authority determines independently. But Hok Iddud defines a toshav chozer vatik for ITS purposes as one meeting Section 14(a) **and holding a returning-resident certificate from the Ministry of Aliyah and Integration**, so it is a precondition to the Step 5 caps and skipping it can forfeit them entirely.

## Reference Links

| Topic | URL |
|---|---|
| Income Tax Ordinance (Nevo) | https://www.nevo.co.il/law_html/law01/255_001.htm |
| Hok Iddud Aliyah 2026 (Nevo) | https://www.nevo.co.il/law_html/law00/241397.htm |
| ITA Income Tax Circular 07/2026 (Hok Iddud implementation) | https://www.gov.il/BlobFolder/service/tax-relief-new-immigrants/he/IncomeTax_hozer-7-2026-acc.pdf |
| Kol-Zchut, vatik (10+) | https://www.kolzchut.org.il/he/הטבות_במס_לתושבים_חוזרים_ששהו_בחו%22ל_מעל_10_שנים |
| Kol-Zchut, regular (6-10) | https://www.kolzchut.org.il/he/הטבות_במס_לתושבים_חוזרים_ששהו_בחו%22ל_בין_6_ל-10_שנים |
| BSH CPA, vatik 2026 | https://www.bshcpa.co.il/תושב-חוזר-ותיק/ |
| BSH CPA, 2026 labor cap | https://www.bshcpa.co.il/tax-exemption-returning-residents-olim-2026/ |
| BSH CPA, year-of-acclimation 90-day rule | https://www.bshcpa.co.il/שנת-הסתגלות-תושב-חוזר/ |
| Amendment 272 (Arnon TL) | https://arnontl.com/he/news/ביטול-הפטור-מדיווח-על-הכנסות-פטורות-לע/ |
| Amendment 272 (Shibolet EN) | https://www.shibolet.com/en/cancellation-of-reporting-exemption-for-new-immigrants-and-long-term-returning-residents-regarding-foreign-income-and-new-reporting-obligation-for-israeli-resident-trustees-regarding-trusts-not-requir/ |
| Knesset Research Center analysis | https://fs.knesset.gov.il/globaldocs/MMM/2ef1a063-cd62-f011-a85f-005056aa9911/2_2ef1a063-cd62-f011-a85f-005056aa9911_11_20997.pdf |
| ITA Circular 1/2011 (year of acclimation) | https://www.gov.il/BlobFolder/policy/income-tax-professional-inst-01-2011/he/Policy_IncomeTaxInst_hoz1-2011.pdf |
| ITA Circular 10/2025 (capital loss matching) | https://www.gov.il/BlobFolder/policy/professional-directives-271125-1/he/IncomeTax_professional-directives-271125-1.pdf |
| Y-Tax on capital loss offsetting (Circular 10/2025) | https://y-tax.co.il/capital-loss-offsetting/ |
| S. Horowitz on equity-comp sourcing | https://s-horowitz.com/taxation-of-stock-options-for-employees-who-became-israeli-residents/ |
| Philip Stein, US-Israel treaty | https://www.pstein.com/our-firm/us-israel-tax-treaty/ |
| IRS, US-Israel treaty PDF | https://www.irs.gov/pub/irs-trty/israel.pdf |
| Nefesh B'Nefesh, Benefits for Toshavim Chozrim (Returning Residents) | https://www.nbn.org.il/life-in-israel/government-services/rights-and-benefits/benefits-for-toshavim-chozrim-returning-residents/ |
| Nefesh B'Nefesh, US-Israel tax update 2026 (rules for olim and returning Israelis from 1.1.2026) | https://www.nbn.org.il/life-in-israel/finances/taxes/us-tax-compliance/ |

## Troubleshooting

**"I do not know my exact Israeli tax-residency start date."**
Walk through the center-of-life factors: where is your family, primary home, work, social ties, schools. Pick the date when the majority of factors shifted. Document with photos, lease, school enrollment, etc. A CPA can finalize.

**"My foreign company sent me a 1099/W-2 for work done after I moved to Israel, is it foreign-source?"**
No. Source follows where the work was performed, not where the payer sits. Work performed in Israel is Israeli-source regardless of who pays.

**"I returned on 15 December 2025, do I get the legacy regime?"**
Probably yes, if your Israeli tax-residency commenced on that date (not 2.1.2026). But the cutover is so close to the 1.1.2026 line that a CPA must confirm the residency-start date and document it carefully.

---

**This skill is a planning aid, not binding tax advice. Engage a CPA before any filing.**
