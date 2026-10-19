# Changelog

## 1.7.1 - 2026-10-20

- Step 5 projection: when it is unclear whether a contract is part of the usual flow or extra to it, add it, since the notification duty is triggered by expectation. Reworded the 95,000-in-July sentence (wording only).

## 1.7.0 - 2026-10-19

Two dates and one figure were wrong, several facts a freelancer acts on were missing, and a projection rule double counted.

- **Annual report dates corrected.** Tax year 2025: 29 May 2026 for non-online filers and 30 June 2026 online (the gov.il Form 1301 page), not 31 May. The tax year 2026 dates are not published and are not assumed.
- **The "April 30" Gotcha attributed that date to the osek patur declaration.** The declaration is due 31 January; only the 2025 declaration was deferred, once, to 30 April 2026.
- **Mandatory self-employed pension: 14,044 NIS is the 2026 annual TOTAL**, not the upper-bracket figure. Applies from 21 to under 60.
- **Osek patur ceiling indexation reinstated.** VAT Law s.126(א) indexes it to CPI every 1 January unless set by order in the preceding six months (s.126(ג)). The 1.4.0 cycle removed this as unsourced; it was right.
- **Occupations barred from osek patur (reg. 13)** listed in full, including group instruction for 5 or more students, plus the opposite exception for salaried people who lecture, translate or write for a business (the client pays the VAT).
- **Esek za'ir** reframed as an income-tax status (an osek murshe can hold it too), with the correct disqualifiers, the 25 December tax coordination, the shortened report (tax year 2025 by 31 August 2026, later years by 31 March) and the 30% downside when real expenses are higher. The unsupported "Amendment 277" attribution was removed.
- **Allocation numbers:** buyer rule (s.38(א1)) and seller duty (s.47(א2)(1)) kept separate; the full confirmation number is long (A30 field, 26-digit examples) and the printed short form is its rightmost 9 digits. The 2024 row is "2024 (pilot year), above 25,000"; no primary source was found for a 5 May 2024 start date.
- **VAT reporting:** bi-monthly up to 1,775,000 NIS (re-indexed each 1 September), zero reports, 19th online payment, the s.67(ב1) rest-day rule, and the 874 detailed report for individuals above 500,000 NIS from 1/2026 with the 2027 deferral route.
- **Collections:** VAT on an issued tax invoice is owed even if unpaid (s.49), so the payment-demand-first flow and credit notes are explained; tax withheld at source is recorded as settled, not chased.
- **Household utility bills** are mixed-use (s.41): their VAT is not totalled into input VAT; the six-month deduction window (s.38(א)) is flagged.
- **Year-end savings:** keren hishtalmut for the self-employed added (13,203 deductible, 20,566 exempt-gains cap for 2026); pension benefit restated from Kol Zchut (11% deduction up to 25,608; 35% credit up to 11,640 preferred member or 16,440 otherwise, plus the s.45א(ו) 0.5% slice).
- **Bituach Leumi:** no longer asserts an unsourced 15th-of-month due date or "circular 1502"; the bank standing order debits on the 22nd, and advances can be corrected once a quarter on a 10% change.
- **Osek patur projection** no longer double counts contracted work: per remaining month, the larger of the contracted amount and the run rate.
- Dead water-corporation domains in references/utility-portals.md fixed.

## 1.6.0 - 2026-08-27

The allocation-number rule was stated three different ways in one skill, and the version a reader hit depended on which section they opened.

- **The main allocation-number paragraph contradicted itself.** It opened "For osek murshe, tax invoices exceeding **5,000 NIS** must include an allocation number" and then closed "From June 2026 this threshold drops to 5,000 NIS", so the threshold was 5,000 both before and after the step. The Jan 2026 row (10,000) was missing entirely, which meant a NIS 7,000 invoice issued in March 2026 was flagged as missing a number it never needed. Replaced with the full staged table (25,000 from 5 May 2024, 20,000 from 1 Jan 2025, 10,000 from 1 Jan 2026, 5,000 from 1 Jun 2026) and an explicit statement that the threshold in force on the invoice **issue date** governs, not today's.
- The Hebrew Gotcha carried the same self-contradiction in its own words ("מ-1.6.2026 ... מעל 5,000 ש\"ח (יורד ל-5,000 ש\"ח מיוני 2026)"), and the Hebrew main paragraph had the Jan-May 2026 step but not the 2024 or 2025 rows. Both now carry the full ladder.
- The English Gotcha at the bottom of the file was already correct, which is why this survived: a reader who opened Gotchas got the right answer and a reader who opened the Invoicing section did not. Same skill, same day, two different rules.
- **Evidence file schema normalised.** 21 of 32 entries had no `claim_id`, and the allocation entry described only the last three steps of the ladder. Both fixed, and the 25,000 opening row now has its own entry recording that it is corroborated across four sibling skills rather than re-fetched.

Verified unchanged and correct: the osek patur / esek za'ir ceiling of 122,833 NIS for 2026 (120,000 in 2024 and 2025), which is quoted verbatim from Kol Zchut in the evidence file and matches the figure carried by three other skills in this repo; the 18% VAT rate; and the projection-governs-not-percentage rule for the threshold crossing.
