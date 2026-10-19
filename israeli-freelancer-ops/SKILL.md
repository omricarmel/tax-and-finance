---
name: israeli-freelancer-ops
description: Manage daily operations for Israeli freelancers (osek murshe, osek patur) - invoice aging with collection reminders, utility bill collection via browser automation, tax deadline alerts (VAT, Bituach Leumi, mkdamot, annual report), osek patur threshold monitoring, and organized accountant packages (havila). Use when a freelancer needs help tracking invoices, preparing documents for their accountant, monitoring their osek patur revenue ceiling, or staying on top of Israeli tax filing deadlines. Prevents missed VAT filings (which trigger automatic penalties), forgotten invoice follow-ups, and disorganized handoffs to accountants. Do NOT use for VAT return preparation (use israeli-vat-reporting), e-invoice generation (use israeli-e-invoice), or payroll/employee management.
license: MIT
---

# Israeli Freelancer Operations

## Legal notice

This is a free information tool operated by an AI model. It explains the rules and calculates from the figures you enter, but it does not examine your full circumstances and does not constitute tax advice. All of its outputs are produced automatically, with no involvement, review, or approval by a tax adviser or accountant, and an AI model may err, omit data, or present a wrong conclusion. The binding computation is the Tax Authority's and responsibility for reporting is yours. This tool is not a substitute for advice that takes account of the particular circumstances and needs of each person, and all use of its output is the user's sole responsibility.


## Instructions

### Step 1: Assess Freelancer Profile
Determine the user's business type and tax obligations:

- **Osek Murshe (עוסק מורשה):** Authorized dealer, registered for VAT. Must file VAT returns, issue tax invoices (hashbonit mas), and can deduct input VAT (mas tsumos).
- **Osek Patur (עוסק פטור):** Exempt dealer, under revenue threshold (122,833 NIS for 2026; was 120,000 NIS in both 2024 and 2025). By statute the ceiling is CPI-indexed every 1 January (VAT Law s.126(א)) unless the Finance Minister set it by order in the preceding six months (s.126(ג)), so re-check it each January. Bills with a payment demand (חשבון עסקה) and issues a receipt (kabala) when paid; does not charge or report VAT.
  - **Occupations that can never be osek patur, whatever the turnover** (VAT Registration Regulations, reg. 13): agronomist, architect, practical engineer (הנדסאי), private investigator, rabbinical pleader, technician, dental technician, organisation or management consultant, scientific consultant, tax adviser, economist, engineer, surveyor, bookkeeper, interpreter (מתורגמן), lawyer, accountant, appraiser, chemical or medical lab owner, doctor, psychologist, physiotherapist, veterinarian, dentist, driving-school owner, school or kindergarten owner (not a non-profit), **anyone running professional, art or sport instruction for groups of at least 5 students** (unless incidental, up to 30 instruction days a year), real-estate broker, car dealer or broker. Ask the user's occupation before treating them as osek patur.
  - **The opposite exception:** someone whose main income is salary, pension or an allowance, who freelances for a business, non-profit or financial institution in lecturing, teaching or training, translation, writing or editing, artistic performance, exam preparation or invigilation, mediation, statutory committees, or as an insurance agent, does not have to register at all; the client pays the VAT from the first shekel.
  - **Clients abroad:** services to a foreign resident are generally zero-rated (VAT Law s.30(א)(5), not when the service is also given to an Israeli resident in Israel), so an osek patur serving mainly overseas clients gains little from the exemption and loses input-VAT refunds; Kol Zchut notes registering as osek murshe may be worthwhile below the ceiling. Raise it for the accountant to decide.
  - A low-income osek patur may qualify for the work grant (מענק עבודה). Registration with Bituach Leumi applies even at low income and to employees with a side business.
- **Esek Za'ir (עסק זעיר):** An **income-tax** status, not a VAT status (Income Tax Ordinance sections 87ב to 87ז, in force from tax year 2024). Both an osek patur and an osek murshe can be esek za'ir if annual turnover stays within the same ceiling (122,833 NIS for 2026). It replaces actual expenses with an automatic 30% normative deduction, so a freelancer whose real expenses exceed 30% of turnover pays more tax under it. In most cases there are no mkdamot and no full annual report; instead the user files an online tax coordination (תיאום מס) by 25 December each year and a shortened annual report (tax year 2025: by 31 August 2026; later years: by 31 March of the following year). Missing the shortened report turns the business into a regular one with a full annual report. A new osek patur file is registered as esek za'ir automatically unless the applicant opts out; anyone else applies online. Not available if the business employs workers, if it does not keep admissible books, if any income came from the person's own employer in that tax year, if more than 25% came from a relative or from someone who employed them in the previous three tax years, if there was income not from personal exertion, or if the person controls a closely held company. Re-check the ceiling each year.

Key profile details to collect:
- Business type (osek murshe / osek patur / esek za'ir)
- VAT filing frequency: bi-monthly when turnover in the determining year is up to 1,775,000 NIS (figure from September 2025; re-indexed every 1 September under VAT Law s.126(ד), so confirm it after each 1 September), monthly above it, and monthly for anyone required to file the detailed 874 report (Step 4)
- Industry and occupation (screen against the reg. 13 list above), and whether clients are in Israel or abroad
- Whether business clients withhold income tax at source (ניכוי במקור) from payments
- Accountant details: name, preferred package format, submission schedule
- Current revenue tracking: year-to-date income, number of active clients

Store the freelancer profile in persistent memory for ongoing tracking across sessions. If persistent memory is unavailable, export the profile as `freelancer-profile.json` in the working directory and reload it at the start of each session.

### Step 2: Set Up Invoice Aging Tracker
Track all issued invoices by payment status using aging buckets:

| Bucket | Age | Action |
|--------|-----|--------|
| Current | 0-29 days | Monitor, no action needed |
| 30-day | 30-59 days | Friendly WhatsApp reminder |
| 60-day | 60-89 days | Formal email follow-up |
| 90+ day | 90+ days | Alert for escalation |

Configure graduated reminder schedule:
- **Day 30:** Friendly WhatsApp message: "היי, רציתי לבדוק לגבי חשבונית מספר [X] מתאריך [DATE]. אשמח לעדכון על מועד התשלום."
- **Day 60:** Formal email follow-up with invoice copy attached, payment details (bank transfer info), and a clear due date.
- **Day 90+:** Alert the freelancer for escalation consideration. Suggest using the israeli-client-payment-chaser skill for structured collection (if available).

**Israel Invoice allocation numbers (חשבוניות ישראל).** For osek murshe, a tax invoice (hashbonit mas) above the threshold must carry an allocation number (mispar haktza'a) from the Tax Authority system, or the recipient cannot deduct the input VAT. **The threshold is staged, and the one that applies is the one in force on the invoice ISSUE date, not today's:**

| In force from | Threshold (pre-VAT) |
|---|---|
| 2024 (pilot year) | above NIS 25,000 |
| 1 Jan 2025 | above NIS 20,000 |
| 1 Jan 2026 | above NIS 10,000 |
| 1 Jun 2026 | above NIS 5,000 (current) |

An invoice issued in March 2026 is tested against 10,000, not 5,000, so do not flag a NIS 7,000 invoice from that month as missing a number. There is no announced step below 5,000; do not invent one. When tracking invoices, flag any issued invoice above the threshold for its own issue date that has no allocation number.

Keep the two statutory rules apart: the **buyer's** deduction is barred without a number (VAT Law s.38(א1)); the **seller's** duty to request one when the buyer demands it is s.47(א2)(1). The full number is long and invoices may print only its rightmost 9 digits; accept either form. Details: references/deadline-calendar.md.

**What you are aging matters for an osek murshe.** VAT on an issued tax invoice is owed on the next VAT report even if the client never pays, until the invoice is cancelled or corrected (VAT Law s.49). Many service freelancers therefore bill with a payment demand (חשבון עסקה) and issue the tax invoice when paid; check with the accountant that this fits the business. For a 90+ debt that will not be collected, raise a credit note or bad-debt treatment with the accountant rather than leaving VAT paid on income never received. Whatever the status, a receipt is issued immediately when each payment arrives.

Additional tracking:
- Record partial payments and update outstanding balances accordingly
- Record income tax withheld at source by a client as **settled by withholding**, not as an unpaid balance, and never chase the client for it: it is a credit against the user's own annual tax. Keep each client's annual withholding statement for the accountant, and send clients the user's current withholding certificate (אישור ניכוי במקור) each year so they withhold at the right rate
- Link to israeli-e-invoice for generating new invoices or credit notes
- Maintain running totals: total outstanding, total overdue, by client

### Step 3: Configure Utility Bill Collection
Use browser automation (CDP) to collect monthly bills (electricity from iec.co.il, Bezeq, Partner, HOT, the city's water corporation, arnona from the municipality portal; URLs and paths in references/utility-portals.md). For each provider: open the bill section with stored credentials, download the latest PDF, extract billing period, amount, due date and payment status, and file it by month and category in the accountant package folder.

**Household bills are mixed-use.** Input VAT is deductible only for business use (VAT Law s.41), so do not total the VAT on home electricity, internet, phone or water bills into the package's input VAT: label them "mixed use, deductible share for the accountant". A deduction also needs a tax invoice in the dealer's own name and must be taken within six months of the invoice date (s.38(א)), so flag expense invoices approaching that window.

Handle 2FA/OTP: If a portal requires SMS verification, pause browser automation and prompt the user for the OTP code. See references/utility-portals.md for portal-specific notes.

### Step 4: Set Deadline Calendar
Configure proactive alerts for Israeli tax deadlines:

| Deadline | Frequency | Date | Details |
|----------|-----------|------|---------|
| VAT filing (osek murshe) | Bi-monthly | 15th of the month after the period | Deadlines: Mar 15, May 15, Jul 15, Sep 15, Nov 15, Jan 15. Online filers may pay by the 19th. A zero report is due on the same dates. |
| VAT filing (monthly filers) | Monthly | 15th of each month | Turnover above 1,775,000 NIS (see Step 1). Detailed-report (874) filers: the 23rd. |
| Bituach Leumi (self-employed) | Monthly | Per the user's BL payment sheet (דף תשלומים) | National Insurance advances. A bank standing order is debited on the 22nd for the previous month. |
| Annual tax report (doch shnati) | Yearly | Tax year 2025: 29 May 2026 (non-online filers), 30 June 2026 (online filers) | The Tax Authority sets the dates each year; the dates for tax year 2026 are not published yet, so do not assume them. Online filing is mandatory for most filers. Accountant-represented filers often have a later schedule; confirm with the accountant. Do not confuse with the osek patur annual turnover declaration (Jan 31). |
| Advance tax payments (mkdamot) | Monthly or bi-monthly | 15th of the month after the period (19th if paid online via the Tax Authority website, by 18:30) | Frequency set by Tax Authority assessment letter; bi-monthly requires prior approval |
| Osek patur annual declaration | Yearly | January 31 | Report previous year's turnover to VAT office. The 2025 declaration was deferred once, to 30 April 2026. |
| Esek za'ir tax coordination | Yearly | December 25 | Online tax coordination for the year. Shortened annual report by 31 March of the following year (tax year 2025: 31 August 2026). |
| Self-employed pension tax benefit (Sections 45א + 47) | Yearly | **December 31** | Deposits made during the tax year earn the benefit for that year. Up to 16.5 percent of income: a **deduction** for deposits up to 11 percent of income (max 25,608 NIS for 2026) and a **35 percent credit** for deposits up to 5 percent of income (11,640 NIS for a preferred member, עמית מוטב, or 16,440 NIS otherwise), plus a further 0.5 percent slice for someone who took no deduction for disability insurance (Ordinance s.45א(ו)). Figures and the deposit that captures them: references/deadline-calendar.md. |
| Mandatory self-employed pension contribution | Yearly | Deposits during the calendar year | Legal floor under the self-employed pension law, separate from the tax benefit. 2026: 4.45 percent up to half the average wage and 12.55 percent from half up to the full average wage (13,769 NIS/month), **14,044 NIS a year in total** at most. Applies from 21 to under 60; exempt if already 55 on 1 January 2017, and for the first six months after first VAT registration. |
| Keren hishtalmut (self-employed) | Yearly | December 31 | Deductible up to 4.5 percent of taxable business income and of 293,397 NIS (13,203 NIS for 2026); tax-exempt gains on deposits up to 20,566 NIS. Details in references/deadline-calendar.md. |

**Detailed VAT reporting (report 874):** For an osek murshe who is an individual with annual turnover above 500,000 NIS, the detailed periodic report (doch meforat, each invoice listed) applies from reporting period 1/2026 (companies already from 9/2025). It forces monthly reporting, due the **23rd** of the following month. An individual may report invoices of up to 5,000 NIS pre-VAT as a single total, and one whose 2025 input invoices were at least 90 percent invoices of up to 5,000 NIS (by value or by count) may ask the regional VAT office to defer the duty to 1 January 2027. Ask the user's annual turnover to determine if this applies.

Reminder schedule for each deadline:
- **7 days before:** First alert via WhatsApp/Telegram with what to prepare
- **3 days before:** Second alert with checklist of required documents
- **Deadline day:** Final reminder with filing links and instructions

If a deadline falls on Shabbat (Saturday), it moves to Sunday. For VAT, if at least three rest days (holidays and chol hamoed count) fall in the five days before the deadline, it moves to the fourth weekday after them (VAT Law s.67(ב1)); this bites around Sukkot and Pesach. The Tax Authority also announces ad-hoc deferrals; check before each alert. See references/deadline-calendar.md.

Include per-deadline preparation notes:
- VAT filing: have all sales and purchase invoices ready, calculate net VAT (output minus input)
- Bituach Leumi: verify monthly advance amount from latest assessment. A bank standing order is debited on the 22nd for the previous month. 2026 self-employed figures: income floor 3,442 NIS per month, 7.7 percent up to 7,703 NIS and 18 percent up to 51,910 NIS, so the monthly advance runs from 265 NIS to 8,550 NIS. A request to correct the advances can be filed once a quarter, when income changed by at least 10 percent.
- Annual report: coordinate with accountant, ensure all monthly packages delivered. For tax year 2025: 29 May 2026 for non-online filers, 30 June 2026 for online filers. Online filing is mandatory for most filers. The tax year 2026 dates are set by the Tax Authority and are not published yet.
- Mkdamot: check assessment letter for payment coupon amounts. Payments are due by the 15th of the month after the period; paying online via the Tax Authority website extends the deadline to the 19th (until 18:30). Bi-monthly payment requires prior approval in the mkdamot book.
- Pension deposit (Dec 31): alert by **December 15** with the year's business income to date. The benefit ceilings are not the deposit target: the deposit that captures the full 45א + 47 benefit depends on income and on preferred-member status, so have the pension fund or accountant compute it rather than quoting a ceiling as "the amount to deposit". The mandatory minimum and the tax benefit are measured on the same pension deposits, so do not present them as two sums to add. Missing Dec 31 forfeits the tax benefits for the whole year; an insufficient mandatory deposit is a separate exposure.

### Step 5: Monitor Osek Patur Threshold
Track cumulative annual revenue against the osek patur threshold:

- **Current threshold (2026):** 122,833 NIS annually (CPI-indexed each 1 January; was 120,000 NIS in 2024-2025)
- **Alert levels:**
  - **70% (~86,000 NIS):** Informational. "You've reached 70% of the annual threshold. Consider planning for potential transition."
  - **85% (~104,400 NIS):** Warning. "Approaching threshold. Review implications of converting to osek murshe."
  - **95% (~116,700 NIS):** Urgent. "Very close to threshold. Conversion may be required soon."

**The projection governs, not the year-to-date percentage.** Compute the projection for the CALENDAR year first: year-to-date revenue, plus, for each remaining month, the LARGER of the unbilled contracted amount for that month and the run rate (recurring year-to-date income, leaving out past one-off projects, divided by months active: since opening if the business opened this year, otherwise since January). A small retainer does not make a month "covered". A one-off project on top of the usual flow is added to the run rate, not compared with it, and when unsure whether a contract is extra, add it (the duty is triggered by expectation); the user's stated facts about a month override the run rate. Whether the ceiling is prorated for a mid-year opening is not settled here; check with the accountant. Ask about seasonality (a December-heavy business, a summer-only one) and use last year's monthly shape when there is one. If the projection exceeds the ceiling, the notification duty is live NOW even when the year-to-date percentage still looks comfortable. A freelancer at 95,000 in July is only in the informational band above, yet their projection is well past the ceiling and they must act this week. Conversely someone at 110,000 in late December with nothing in the pipeline needs no action. Use the bands only as secondary context.

When the threshold is reached or projected to be exceeded, explain the implications:
- Must register as osek murshe with the Tax Authority
- Must start charging VAT (18%) on all invoices
- Must issue hashbonit mas (tax invoice), in addition to the receipt on each payment
- Can now deduct input VAT (mas tsumos) on business expenses
- Must file periodic VAT returns (bi-monthly at this turnover), including zero reports in quiet periods
- **Bituach Leumi and mkdamot must be re-estimated, and this is not caused by the VAT change.** Bituach Leumi is driven by income, not by VAT status, so converting does not itself raise it. What raises it is the higher income: advances were set from an assessment on a lower prior year, so a jump creates a year-end debt with linkage unless the user files a revised income declaration with Bituach Leumi now. The same applies to income-tax mkdamot, which are set from the prior year assessment: request an adjustment (בקשה לשינוי מקדמות) rather than underpaying all year.

**The two traps when crossing mid-year, state both explicitly:**
1. **Notify BEFORE the invoice that crosses the line.** The duty is triggered by the projection, not by the arrival of the money: `ברגע שצופים שההכנסות עד סוף השנה יעברו אות התקרה השנתית של העוסק הפטור, יש להודיע על כך לרשות המסים ולבקש לשנות את סיווג העסק מעוסק פטור לעוסק מורשה`. Once reclassified, the business charges VAT and issues tax invoices going forward. The mechanism is a change of classification at the **regional VAT office** (משרד מע"מ האזורי) for the existing file, and Kol Zchut advises doing it before receiving the payment that crosses the ceiling.
2. **Input VAT from the exempt part of the year is lost.** It cannot be reclaimed retroactively: `אי אפשר לדרוש רטרואקטיבית קיזוז מע"מ על הוצאות שהיו לעסק מתחילת השנה כאשר היה מוגדר כעוסק פטור, אלא רק על הוצאות שייווצרו מרגע הפיכתו לעוסק מורשה`. So a freelancer who buys equipment while still an osek patur and converts a month later never recovers that VAT. If a large purchase is planned and the crossing is foreseeable, the timing of the conversion is worth real money.

Do NOT state a specific statutory deadline in days for the notification, or a penalty figure: those are asserted by practitioner sites but are not in the regulations, which only impose the annual January 31 turnover declaration.

**Esek za'ir is not an alternative to converting.** It is an income-tax status with the same ceiling (122,833 NIS for 2026), so it ends when the ceiling is crossed and never defers the VAT conversion. Because a new osek patur file is esek za'ir by default, ask instead whether the user already is one (no mkdamot, 25 December tax coordination, shortened report): crossing the ceiling changes their income-tax reporting too, and the accountant should plan for it.

**Turnover above the ceiling before reclassification:** whether VAT is owed on it is not settled by the sources this skill has checked. Do not tell the user there is no exposure; flag it for the accountant.

Generate a transition checklist:
1. Ask the regional VAT office to change the classification from osek patur to osek murshe, before the payment that crosses the ceiling
2. Update invoicing system to issue tax invoices with VAT
3. Register for the Israel Invoice allocation number system (currently required for invoices above NIS 5,000 pre-VAT; see the staged table above for earlier issue dates)
4. Notify clients of new invoicing format
5. Set up VAT filing schedule (see Step 4)
6. Begin tracking input VAT on business expenses for deductions
7. Consult accountant on transition timing and implications

### Step 6: Generate Accountant Package (Havila L'Roe Cheshbon)
Compile an organized monthly or quarterly package for the accountant:

**Package contents:**
1. **Issued invoices:** All invoices/receipts issued during the period, sorted by date
2. **Received invoices/receipts:** All expense documents (business purchases, subscriptions, equipment)
3. **Bank statement summary:** Transaction list matched to invoices where possible
4. **Utility bills:** Bills collected in Step 3, organized by provider
5. **Revenue summary:** Running annual total with monthly breakdown
6. **Cover sheet:** Summary page with key numbers

**Cover sheet fields:** period covered; total revenue (bruto); total expenses; net income (neto); for osek murshe, VAT collected, input VAT on clearly business expenses (mixed-use household bills listed separately for the accountant) and net VAT payable or refundable; tax withheld at source by clients; running annual revenue total; number of invoices issued and received.

**Export format:** folders `YYYY-MM/invoices-issued/`, `YYYY-MM/invoices-received/`, `YYYY-MM/utility-bills/`, `YYYY-MM/bank-statements/` (or one ZIP with the same structure), with the cover sheet as PDF or CSV at the root.

Cross-reference with related skills:
- Use israeli-e-invoice for generating any missing invoices (if available)
- Use israeli-vat-reporting for VAT return preparation (if available)
- Use israeli-bank-connector for pulling bank transaction data (if available)

## Examples

### Example 1: Freelancer Tracking Invoices Across Aging Buckets
User says: "I have 5 outstanding invoices for my web dev consulting, some are getting old"
Actions: request the invoice list (amounts, issue dates, clients, and any tax withheld), bucket each invoice by age, queue reminders for 30+ days, and produce an aging report by bucket and by client.
Result: Organized aging dashboard with 2 invoices current, 1 at 30-day (WhatsApp reminder queued), 1 at 60-day (email follow-up sent), and 1 at 90+ (escalation alert flagged). Automated follow-up reminders configured for all overdue invoices.

### Example 2: Developer Approaching Osek Patur Threshold
User says: "I'm osek patur and I think I'm getting close to the limit this year"
Actions:
1. Request current year's revenue total and number of remaining months
2. Calculate the projection with the Step 5 formula
3. Compare against current threshold (122,833 NIS for 2026)
4. Result: at 85% of threshold (104,400 NIS earned) with 3 months remaining
5. Average monthly income of ~11,600 NIS projects annual total of ~139,200 NIS, exceeding threshold by ~16,400 NIS
6. Prepare transition checklist: VAT registration, invoice type changes, expense VAT deductions
Result: Threshold status report saying the notification duty is already live: the projection crossed the ceiling months ago and the ceiling itself will be crossed within weeks, so the classification change should be filed with the regional VAT office before the next payment. Clear breakdown of what changes when converting to osek murshe, with the step-by-step transition checklist, and the open question of VAT on turnover above the ceiling flagged for the accountant.

### Example 3: Preparing Year-End Package for Accountant
User says: "My accountant needs everything organized for the annual report"
Actions: compile the year's issued invoices in date order, match expense receipts to bank entries, run utility collection (Step 3) for missed bills, add clients' withholding statements, build the monthly revenue and expense summary, and package it with the cover sheet.
Result: Complete accountant package (havila l'roe cheshbon) with 12 monthly folders, each containing issued invoices, expense receipts, and utility bills. Cover sheet shows annual revenue of 185,000 NIS, expenses of 42,000 NIS, net of 143,000 NIS, with VAT summary. Ready for handoff as ZIP file.

## Bundled Resources

### References
- `references/deadline-calendar.md`: Complete Israeli tax deadline calendar for freelancers: VAT filing dates, Bituach Leumi monthly payments, annual report deadlines, and advance tax payment (mkdamot) schedule. Includes both osek murshe and osek patur timelines, plus holiday adjustments. Consult when setting up deadline alerts in Step 4.
- `references/utility-portals.md`: Login URLs, bill download paths, and automation notes for Israeli utility providers (IEC, Bezeq, HOT, Partner, water corporations, Arnona portals). Includes 2FA/OTP handling guidance per portal. Consult when configuring browser-based bill collection in Step 3.

## Gotchas
- Agents may confuse Osek Murshe (licensed dealer, charges VAT) with Osek Patur (exempt dealer, no VAT). The threshold for Osek Patur is 122,833 NIS for 2026 (was 120,000 NIS in 2024-2025). Exceeding it mid-year requires immediate registration upgrade.
- An osek murshe must file every periodic VAT report on time even with no activity, as a zero report (the Tax Authority's new-dealer guide); an osek patur files only the annual turnover declaration. Agents may skip a period with no income, but a late or missing report draws late-filing fines.
- Bituach Leumi advance payments (mikdamot) for self-employed are based on projected annual income, not actual monthly revenue. Agents may calculate contributions based on current month earnings.
- Invoice numbering in Israel must be sequential with no gaps. Agents may suggest starting from an arbitrary number or allowing gaps, which violates Tax Authority requirements.
- Since 1 June 2026 an osek murshe's tax invoice above 5,000 NIS pre-VAT needs an allocation number (mispar haktza'a) when the buyer is an osek murshe who asks for one; for earlier issue dates use the staged table in Step 2. Agents may generate invoices without this number, and the buyer then loses the input VAT deduction.
- Agents may not distinguish between esek za'ir (micro business) and standard osek patur. Esek za'ir is an income-tax status (an osek murshe can hold it too) with a 30% normative expense deduction and simplified reporting, and it shares the same turnover ceiling. Recommending esek za'ir benefits to a standard osek patur (or vice versa) causes confusion.
- Agents may quote the wrong annual-report deadline. The osek patur turnover declaration is due **31 January** (the 2025 declaration alone was deferred to 30 April 2026). The income-tax annual report (Form 1301) for tax year 2025 was due 29 May 2026 for non-online filers and 30 June 2026 online. April 30 is not a general deadline for either.
- Agents may treat the 35 percent Section 45א credit and the mandatory self-employed pension contribution as the same obligation. It is one stream of pension deposits with two separate tests: a legal floor under the Self-Employed Pension Law, and the 45א/47 benefit ceilings. Do not present them as two sums to add.

## Reference Links

Use these official sources to verify time-sensitive figures before quoting them to the user. Israeli tax and Bituach Leumi tables update at least annually; allocation-number thresholds change mid-year.

| Source | URL | What to Check |
|--------|-----|---------------|
| Tax Authority - Form 1301 / annual income-tax report | https://www.gov.il/he/service/reporting-and-payment-2025-annual-tax-report-for-individuals | Current-year deadlines for paper and online filing |
| Tax Authority - VAT guide for the new dealer | https://www.gov.il/he/pages/vat-to-the-new-dealer?chapterIndex=9 | Monthly vs bi-monthly threshold, zero reports, 19th online payment |
| Tax Authority - PCN 874 / detailed VAT reporting | https://www.gov.il/he/pages/pa280825-1 | 500,000 NIS threshold for individuals from 1/2026, deferral to 2027 |
| Tax Authority - Allocation numbers (mispar haktza'a) | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice | Current allocation-number threshold: 5,000 NIS before VAT since 1.6.2026 |
| Kol Zchut - Osek Patur | https://www.kolzchut.org.il/he/עוסק_פטור | Current threshold, conversion rules |
| Kol Zchut - Esek Za'ir | https://www.kolzchut.org.il/he/עסק_זעיר | 30 percent normative deduction, eligibility caveats |
| Kol Zchut - Self-employed pension tax benefits (Sections 45א, 47) | https://www.kolzchut.org.il/he/הטבות_במס_הכנסה_בגין_הפקדות_עצמאיות_לביטוח_פנסיוני | Current-year deduction and credit ceilings, preferred-member rule |
| Bituach Leumi - Self-employed rates | https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx | Current advance bracket min/max and floor |

## Troubleshooting

### Error: "Utility portal login failed"
Cause: Israeli utility portals frequently change their login flows or require SMS 2FA.
Solution: Pause automation for the OTP, check the credentials and the portal URL, and see references/utility-portals.md.

### Error: "VAT filing deadline incorrect"
Cause: Using wrong filing frequency (bi-monthly vs monthly) for the business type.
Solution: Verify filing frequency in the freelancer profile (Step 1). Osek murshe with determining-year turnover up to 1,775,000 NIS (see Step 1) files bi-monthly on the 15th of odd months. Above it, or when required to file the detailed 874 report, the business files monthly. See references/deadline-calendar.md for the complete schedule.

### Error: "Osek patur threshold outdated"
Cause: The threshold is CPI-indexed each 1 January (or set by order).
Solution: Check the Kol Zchut osek patur page (Reference Links) each January; 122,833 NIS for 2026. Update the profile when a new amount is published.

### Error: "Annual report due April 30"
Cause: Confusing the income-tax annual report (Form 1301) with the osek patur turnover declaration.
Solution: See the annual-report Gotcha above; confirm the current year's dates on the Form 1301 service page.

### Error: "Accountant package missing documents"
Cause: Not all expense receipts were tracked during the period, or utility bills were not collected.
Solution: Re-run utility collection (Step 3), cross-check the bank statement against tracked expenses, and look for recurring expenses (subscriptions, rent, insurance) with no receipt.
