# Israeli Budget Planner: Domain Checklist

Scope: household / personal budgeting and mortgage (mashkanta) planning for Israeli
residents. Reviewed against this checklist on each update. Figures must be the
current (2026) authoritative values, each traceable to a source below.

## Must cover (a wrong/absent item here is a CRITICAL family-facing error)

1. **Bank of Israel interest rate + prime rate.** Current BOI rate and prime =
   BOI + 1.5%. As of 3 Sep 2026 (decision of 1 Sep 2026): BOI 3.25%, prime 4.75%.
   Source: https://www.boi.org.il (rate series via the BOI SDMX API)
2. **Mortgage mix rule (correct direction).** At least 1/3 of the total mortgage must be
   in a FIXED-interest track; up to 2/3 may be variable/prime. The fixed third need NOT
   be unlinked, a CPI-linked fixed track satisfies it. Maximum term 30 years. (Inverting the direction leads a family to an
   over-variable, rate-shock-exposed loan; over-stating it as "unlinked" wrongly removes
   the cheaper CPI-linked fixed option from their choice set.)
   Source: https://www.kolzchut.org.il/he/מגבלות_על_לקיחת_משכנתא
3. **PTI (payment-to-income) cap.** BOI regulatory ceiling: monthly repayment may not
   exceed 50% of disposable income, counting earlier loans secured on the same property
   with more than 18 months left. Above 40% PTI the loan carries a 100% risk weight,
   which is the authoritative anchor for the skill's 40% planning line.
   Source: https://www.kolzchut.org.il/he/מגבלות_על_לקיחת_משכנתא ;
   https://boi.org.il/media/ez4npagt/329.pdf (directive 329, version 06/26)
4. **LTV limits.** 75% first/only home, 70% home replacement, 50% investment.
   Source: https://www.kolzchut.org.il/he/מגבלות_על_לקיחת_משכנתא
5. **Net-pay deductions used in affordability math must be the CURRENT employee rates,**
   because PTI and budget headroom are computed off net income:
   - Income tax: marginal 10%-50% brackets (2026 widened Jan 2026; 10% bracket to
     ~7,010/mo, top 50% above ~60,130/mo).
     Source: https://www.kolzchut.org.il/he/מדרגות_מס_הכנסה
   - **Bituach Leumi + health-tax (employee): the FULL category table, not one row.**
     The rate varies by age and pension status. Must cover, as its own row each:
     resident 18-to-retirement (4.27% / 12.17% combined), under 18 (0% / 0%),
     old-age-pension recipient (0% / 0%), disability-pension recipient with annual
     approval (health only, 3.23% / 5.17%), aged 67-70 not receiving old-age pension
     (3.93% / 10.03%), woman between retirement age and male retirement age not
     receiving a pension (3.95% / 10.24%), controlling shareholder (4.25% / 11.96%),
     first resident after 62 (3.6% / 7.45%). Split at 7,703 NIS/mo, ceiling 51,910.
     Encoding only the default row charges the full deduction to a working pensioner or
     an under-18 employee, who in fact owe nothing.
     Source: https://www.btl.gov.il/Insurance/Rates/Pages/%D7%9C%D7%A2%D7%95%D7%91%D7%93%D7%99%D7%9D%20%D7%A9%D7%9B%D7%99%D7%A8%D7%99%D7%9D.aspx
   - **Health-tax (dmei bituach briut), employee 2026: 3.23% reduced / 5.17% full**,
     split at 7,703 NIS/mo.
     Source: https://www.btl.gov.il/Insurance/Health_Insurance/Pages/%D7%A9%D7%99%D7%A2%D7%95%D7%A8%D7%99%20%D7%93%D7%9E%D7%99%20%D7%91%D7%99%D7%98%D7%95%D7%97%20%D7%91%D7%A8%D7%99%D7%90%D7%95%D7%AA.aspx
   - Tax credit point (nekudat zikui): 242 NIS/mo in 2026; resident base 2.25, women
     +0.5, new immigrant extra for 42 months (arrived before 2022) or 54 months (2022 on).
     Source: https://www.kolzchut.org.il/he/נקודות_זיכוי_ממס_הכנסה
6. **Minimum wage / average wage.** Min wage 6,443.85 NIS/mo (35.40/hr) from 1 Apr 2026;
   average wage 13,566 NIS/mo (section 1, Jan 2026).
   Source: https://www.kolzchut.org.il/he/שכר_מינימום ;
   https://www.btl.gov.il/Mediniyut/GeneralData/Pages/%D7%A9%D7%9B%D7%A8%20%D7%9E%D7%9E%D7%95%D7%A6%D7%A2.aspx
7. **VAT (ma'am): 18%** (since 1 Jan 2025).
   Source: https://www.gov.il/he/pages/vat-history
8. **Hidden fixed housing costs.** Rent is quoted excluding arnona + va'ad bayit; these
   add ~500-2,000 NIS/mo and must be in the budget.
9. **Arnona = municipality-set, annual.** Do not ship static per-city tables; fetch the
   current-year tzav arnona from the relevant municipality.
10. **Child credit points by child's age (mother / father table)** and the zero-tax floor,
    because for a family this is the largest net-pay correction.
    Source: https://www.kolzchut.org.il/he/נקודות_זיכוי_ממס_הכנסה_להורה_לילד_עד_גיל_5
11. **Child allowance and savings-for-every-child amounts (2026)** on the income side.
    Source: btl.gov.il children rates page and HisahoLayeled page.
12. **A payment-to-loan path** (`--max-loan`), since "how much can we borrow" is the
    question most users actually ask.

## Should cover (absence = MAJOR)

- Mortgage track types and indicative ranges (prime-linked, fixed-unlinked,
  CPI-linked fixed, CPI-linked variable) with the caveat that ranges drift.
- Mandatory mortgage life + structural insurance (bituach chaim / bituach mavne) as a
  budget line and a bank requirement.
- Pension contribution as a salary deduction (employee 6%; 6.5% is the employer tagmulim leg) - affects net pay.
- Israeli savings vehicles (keren pensia, keren hishtalmut, kupat gemel) with their tax
  treatment and lock-in.
- Emergency-fund target (3-6 months expenses).
- Credit points for children, the pension-contribution tax credit, and the keren
  hishtalmut employee deduction, as named corrections to the net-pay estimate.
- Multi-employer households: the reduced band and credit points cannot both be claimed
  twice; a tiaum dmei bituach and tiaum mas are required.
- Acquisition costs outside the loan (mas rechisha, lawyer, broker, appraiser,
  registration) alongside the LTV equity requirement, with the 2026 only-apartment
  purchase-tax brackets (0% to 1,978,745 NIS).
- A prime rate-shock stress line (prime plus 2 points) for the variable share.
- Surtax (mas yesef): the 50% top row is the 47% bracket plus a 3% surtax, and since 2025 a further 2% applies to high non-employment/non-business income (52% top).
- A worked affordability example tying net income to PTI to max loan to monthly payment.
- Calculator script consistency: the script's hardcoded constants (BL rate/threshold,
  health-tax rate, default mortgage rate, tax brackets) must match the SKILL.md prose;
  divergence between the documented rule and the code that computes the answer is a
  family-facing error.

## Out of scope

- **Self-employed households (osek patur / osek murshe), reviewed 2026-08-27, re-litigated
  2026-10-12:** still out of scope. Users would ask, and the answer they get is an explicit
  routing to a self-employed skill rather than silence; adding a second rate regime to this
  calculator would double its surface for a minority of its users.
  Original rationale: An ordinary
  user WOULD plausibly ask, so this is now an EXPLICIT exclusion stated in SKILL.md,
  SKILL_HE.md and the script docstring rather than a silent gap: the self-employed pay
  different Bituach Leumi and health rates and have deductible expenses and mikdamot, so
  `--salary` must not be used for them. Route them to a self-employed skill. Revisit next
  cycle whether to add the self-employed rate rows outright.
- Per-bank rate shopping / live quote scraping (point to boi-exchange MCP instead).
  Re-litigated 2026-10-12: users ask, but no authoritative per-bank rate is published;
  the skill names indicative ranges and routes to the bank.
- Investment-portfolio / stock advice beyond the named Israeli savings vehicles.
  Re-litigated 2026-10-12: regulated activity (investment advice), stays out.
- Business/corporate budgeting and the state takciv (this is a household tool).
  Re-litigated 2026-10-12: different audience, stays out.
- Legal tax-planning advice (defer to an accountant / rashut hamisim).
  Re-litigated 2026-10-12: stays out; the skill names credit points and brackets but
  does not plan.

## Authoritative sources

- Bank of Israel - interest/prime, mortgage regs: https://www.boi.org.il
- Bituach Leumi - BL + health-tax rates, average wage: https://www.btl.gov.il
- Central Bureau of Statistics - CPI, housing indices: https://www.cbs.gov.il
- Kol Zchut - mortgage rules, min wage, credit points, tax brackets: https://www.kolzchut.org.il
- Israel Tax Authority - brackets, VAT: https://www.gov.il/he/departments/israel_tax_authority
- Municipality tzav arnona (per city) - e.g. https://www.tel-aviv.gov.il
