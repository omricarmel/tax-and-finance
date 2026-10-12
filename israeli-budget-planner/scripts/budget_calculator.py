#!/usr/bin/env python3
"""Calculate Israeli household budget and mortgage estimates.

Provides tools for monthly budget planning, mortgage calculations,
and tax estimation for Israeli households.

SCOPE AND LIMITS. This models a SALARIED employee with ONE employer. It is not a
payslip and will not match one exactly. In particular it does NOT model:
  * credit points beyond the number you pass in --credit-points. Parents are
    entitled to additional credit points for their children, which for a family
    is usually the single largest correction to this figure. Look up the current
    entitlement and pass the real total.
  * the tax credit granted on the employee's own pension contribution, so the
    income-tax line here is conservative (too high).
  * a keren hishtalmut deduction, if the employee has one.
  * a second employer. With two jobs the reduced band and the credit points
    cannot both be claimed twice: the secondary employer withholds at the full
    band and top tax rate until a tiaum (dmei bituach and mas) is filed. Running
    each job through this tool separately will overstate combined net pay.
  * taxable benefits added to salary, such as a company car.
  * the SELF-EMPLOYED. Osek patur and osek murshe pay different Bituach Leumi and
    health rates and have deductible expenses and mikdamot; do not use --salary
    for them, the answer will be wrong.

Usage:
    python budget_calculator.py --salary 15000
    python budget_calculator.py --mortgage --amount 1500000 --years 25
    python budget_calculator.py --max-loan --payment 7000 --rate 0.05 --years 30
    python budget_calculator.py --help
"""

import argparse
import math
from decimal import Decimal, ROUND_HALF_UP

# 2026 annual income-tax brackets (section 121; some brackets were widened in 2026:
# the 20% step now runs to 228,000 and the 31% step to 301,200 NIS/year). The 50%
# row is the 47% bracket plus the 3% surtax of section 121B. Source: kolzchut
# מדרגות מס הכנסה.
TAX_BRACKETS = [
    (84120, Decimal("0.10")), (120720, Decimal("0.14")),
    (228000, Decimal("0.20")), (301200, Decimal("0.31")),
    (560280, Decimal("0.35")), (721560, Decimal("0.47")),
    (999999999, Decimal("0.50")),
]

# Employee (salaried) Bituach Leumi + health-tax rates.
# The rate is NOT one number: it varies by age and pension status. The BTL table
# "לעובדים שכירים" publishes a row per category; the default row below applies only
# to a resident aged 18 to retirement age. Percentages carry 2025 effective dates
# and did not change for 2026; only the two thresholds did.
# Each entry: (bituach_leumi_low, bituach_leumi_high, health_low, health_high).
# Rows where the combined employee rate is health-tax only carry BL 0.
CATEGORIES = {
    "default": (Decimal("0.0104"), Decimal("0.07"), Decimal("0.0323"), Decimal("0.0517")),
    "under18": (Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")),
    "old-age-pension": (Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")),
    "disability-pension": (Decimal("0"), Decimal("0"), Decimal("0.0323"), Decimal("0.0517")),
    "age67-70": (Decimal("0.007"), Decimal("0.0486"), Decimal("0.0323"), Decimal("0.0517")),
    "controlling-shareholder": (Decimal("0.0102"), Decimal("0.0679"), Decimal("0.0323"), Decimal("0.0517")),
    "woman-between-retirement-ages": (Decimal("0.0072"), Decimal("0.0507"), Decimal("0.0323"), Decimal("0.0517")),
    "new-resident-over-62": (Decimal("0.0037"), Decimal("0.0228"), Decimal("0.0323"), Decimal("0.0517")),
}
# Published COMBINED employee rates per category (reduced band, full band). These are
# the authoritative figures from the BTL table; the split above is derived by
# subtracting the health-tax leg, so report combined totals when they are what matters.
CATEGORY_COMBINED = {
    "default": (Decimal("0.0427"), Decimal("0.1217")),
    "under18": (Decimal("0"), Decimal("0")),
    "old-age-pension": (Decimal("0"), Decimal("0")),
    "disability-pension": (Decimal("0.0323"), Decimal("0.0517")),
    "age67-70": (Decimal("0.0393"), Decimal("0.1003")),
    "controlling-shareholder": (Decimal("0.0425"), Decimal("0.1196")),
    "woman-between-retirement-ages": (Decimal("0.0395"), Decimal("0.1024")),
    "new-resident-over-62": (Decimal("0.036"), Decimal("0.0745")),
}
# Reduced-collection step from 1 Jan 2026. Published as an absolute amount; do not
# restate it as a fraction of the average wage, it matches neither section 1 nor 2.
BL_THRESHOLD = Decimal("7703")
# Maximum monthly income subject to Bituach Leumi + health insurance (from 1 Jan 2026).
# Salary above this ceiling is NOT charged BL/health, so the high band must be capped here.
BL_CEILING = Decimal("51910")
# Base credit points for a resident. Women get +0.5 (2.75); new immigrants get extra
# for 42 months (arrived before 2022) or 54 months (2022 on); parents get child points.
# Point value 242 NIS/month (2026); verify with the tax authority.
CREDIT_POINTS = Decimal("2.25")
CREDIT_VALUE = Decimal("242")

def calc_monthly_tax(monthly_salary, credit_points=CREDIT_POINTS):
    annual = Decimal(str(monthly_salary)) * 12
    tax = Decimal("0")
    prev = Decimal("0")
    for limit, rate in TAX_BRACKETS:
        if annual <= prev:
            break
        taxable = min(annual, Decimal(str(limit))) - prev
        tax += taxable * rate
        prev = Decimal(str(limit))
    credit = Decimal(str(credit_points)) * CREDIT_VALUE * 12
    annual_tax = max(Decimal("0"), tax - credit)
    return (annual_tax / 12).quantize(Decimal("0.01"), ROUND_HALF_UP)

def _banded(monthly_salary, low_rate, high_rate):
    """Apply a two-band rate, capped at the maximum insurable income."""
    sal = Decimal(str(monthly_salary))
    if sal <= BL_THRESHOLD:
        return (sal * low_rate).quantize(Decimal("0.01"))
    capped = min(sal, BL_CEILING)
    return (BL_THRESHOLD * low_rate + (capped - BL_THRESHOLD) * high_rate).quantize(Decimal("0.01"))

def calc_bituach_leumi(monthly_salary, category="default"):
    bl_low, bl_high, _, _ = CATEGORIES[category]
    return _banded(monthly_salary, bl_low, bl_high)

def calc_health_tax(monthly_salary, category="default"):
    _, _, h_low, h_high = CATEGORIES[category]
    return _banded(monthly_salary, h_low, h_high)

def show_salary_breakdown(salary, category="default", credit_points=CREDIT_POINTS, pension_rate=None):
    if not math.isfinite(salary) or salary < 0:
        raise SystemExit("error: --salary must be a finite number, zero or positive.")
    if category not in CATEGORIES:
        raise SystemExit("error: unknown --category. Choose one of: " + ", ".join(CATEGORIES))
    if not math.isfinite(credit_points) or credit_points < 0 or credit_points > 40:
        raise SystemExit("error: --credit-points must be between 0 and 40.")
    tax = calc_monthly_tax(salary, credit_points)
    bl = calc_bituach_leumi(salary, category)
    health = calc_health_tax(salary, category)
    # Employee pension contribution: the statutory employee share is 6%. The 6.5%
    # figure often quoted is the EMPLOYER's tagmulim leg, not an employee deduction.
    # Mandatory pension starts at 21 (men) / 20 (women), so under-18s default to 0.
    if pension_rate is None:
        pension_rate = 0.0 if category == "under18" else 0.06
    if not math.isfinite(pension_rate) or pension_rate < 0 or pension_rate > 0.2:
        raise SystemExit("error: --pension-rate must be a decimal fraction between 0 and 0.2.")
    pension = Decimal(str(salary)) * Decimal(str(pension_rate))
    net = Decimal(str(salary)) - tax - bl - health - pension

    print(f"\nSalary Breakdown: {salary:,.0f} NIS/month")
    print("=" * 40)
    lo, hi = CATEGORY_COMBINED[category]
    print(f"  BL/health category:  {category} "
          f"({lo * 100:.2f}% to {BL_THRESHOLD:,.0f}, {hi * 100:.2f}% above, ceiling {BL_CEILING:,.0f})")
    print(f"  Credit points:       {credit_points}")
    print(f"  Gross salary:        {salary:>10,.2f} NIS")
    print(f"  Income tax:          {tax:>10,.2f} NIS")
    print(f"  Bituach Leumi:       {bl:>10,.2f} NIS")
    print(f"  Health tax:          {health:>10,.2f} NIS")
    print(f"  Pension ({pension_rate * 100:.1f}%):     {pension:>10,.2f} NIS")
    print(f"  --------------------------------")
    print(f"  Net salary:          {net:>10,.2f} NIS")
    if category in ("old-age-pension", "age67-70", "woman-between-retirement-ages"):
        print("  Note: past retirement age, mandatory pension contributions follow")
        print("  different rules. If no pension is deducted, re-run with --pension-rate 0.")

# Default rate: prime as of 3 Sep 2026 (BOI 3.25% + 1.50%). Re-verify at boi.org.il.
DEFAULT_RATE = 0.0475

def _check_term_and_rate(years, rate):
    if years <= 0:
        raise SystemExit("error: --years must be a positive number of years.")
    if years > 30:
        raise SystemExit("error: --years may not exceed 30. A mortgage will not be "
                         "approved, on any track, for longer than 30 years.")
    if not math.isfinite(rate) or rate < 0:
        raise SystemExit("error: --rate must be a finite number, zero or positive.")
    if rate > 0.3:
        raise SystemExit("error: --rate is a decimal fraction, not a percentage. "
                         "Pass 0.0475 for 4.75%.")

def calc_mortgage(amount, years, rate=DEFAULT_RATE):
    if not math.isfinite(amount) or amount <= 0:
        raise SystemExit("error: --amount must be a positive number.")
    _check_term_and_rate(years, rate)
    if rate == 0:
        payment = Decimal(str(amount)) / (years * 12)
        total = Decimal(str(amount))
        _print_mortgage(amount, years, rate, payment, total)
        return
    monthly_rate = Decimal(str(rate)) / 12
    n_payments = years * 12
    amt = Decimal(str(amount))
    payment = amt * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    total = payment * n_payments
    _print_mortgage(amount, years, rate, payment, total)

def _print_mortgage(amount, years, rate, payment, total):
    amt = Decimal(str(amount))
    print(f"\nMortgage Calculator")
    print("=" * 40)
    print(f"  Loan amount:     {amt:>12,.0f} NIS")
    print(f"  Term:            {years:>12} years")
    print(f"  Interest rate:   {rate*100:>11.2f}%")
    print(f"  Monthly payment: {payment:>12,.2f} NIS")
    print(f"  Total paid:      {total:>12,.0f} NIS")
    print(f"  Total interest:  {total - amt:>12,.0f} NIS")
    _print_rate_note()

def _print_rate_note():
    print(f"  Note: one rate for the whole loan is illustrative. At least 1/3 of the")
    print(f"  loan must sit in a FIXED track (unlinked 4.5-6.5%, or CPI-linked fixed")
    print(f"  3.0-5.0% plus CPI), so a real blended payment differs. Re-run per track")
    print(f"  and sum. A CPI-linked rate entered here ignores indexation: the real")
    print(f"  payment and balance rise with CPI. Regulatory maximum term is 30 years.")

def calc_max_loan(payment, years, rate=DEFAULT_RATE):
    """Largest loan a fixed monthly payment repays over the term (inverse annuity)."""
    if not math.isfinite(payment) or payment <= 0:
        raise SystemExit("error: --payment must be a positive number.")
    _check_term_and_rate(years, rate)
    pay = Decimal(str(payment))
    n_payments = years * 12
    if rate == 0:
        loan = pay * n_payments
    else:
        r = Decimal(str(rate)) / 12
        loan = pay * (1 - (1 + r) ** -n_payments) / r
    print(f"\nMaximum Loan for a Monthly Payment")
    print("=" * 40)
    print(f"  Monthly payment: {pay:>12,.2f} NIS")
    print(f"  Term:            {years:>12} years")
    print(f"  Interest rate:   {rate*100:>11.2f}%")
    print(f"  Maximum loan:    {loan:>12,.0f} NIS")
    print(f"  This is the loan the payment repays, not what a bank will lend. The")
    print(f"  payment must stay under 50% of disposable income (counting earlier loans")
    print(f"  on the same property), and the loan under the LTV cap (75% only home).")
    _print_rate_note()

def main():
    parser = argparse.ArgumentParser(description="Israeli budget calculator")
    parser.add_argument("--salary", type=float, help="Monthly gross salary in NIS")
    parser.add_argument("--mortgage", action="store_true", help="Calculate mortgage")
    parser.add_argument("--amount", type=float, help="Mortgage amount in NIS")
    parser.add_argument("--max-loan", action="store_true",
                        help="Largest loan a monthly payment repays (needs --payment)")
    parser.add_argument("--payment", type=float, help="Affordable monthly payment in NIS")
    parser.add_argument("--years", type=int, default=25, help="Mortgage term in years")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE,
                        help="Annual interest rate as a decimal fraction (default 0.0475 = prime "
                             "as of Sep 2026, BOI 3.25%% + 1.5%%). Illustrative: at least 1/3 of the "
                             "loan must be in a fixed track, so pass a blended rate or run per track.")
    parser.add_argument("--category", default="default", choices=sorted(CATEGORIES),
                        help="Bituach Leumi / health-tax category. The default row covers a "
                             "resident aged 18 to retirement age. Under-18s and old-age-pension "
                             "recipients pay nothing; disability-pension recipients pay health-tax only.")
    parser.add_argument("--credit-points", type=float, default=float(CREDIT_POINTS),
                        help="Income-tax credit points (default 2.25 resident base; women 2.75; add "
                             "child points per the table in SKILL.md).")
    parser.add_argument("--pension-rate", type=float, default=None,
                        help="Employee pension rate as a decimal fraction (default 0.06; 0 for "
                             "--category under18). Pass 0 for anyone with no pension deduction.")
    args = parser.parse_args()

    ran = False
    if args.salary is not None:
        show_salary_breakdown(args.salary, args.category, args.credit_points, args.pension_rate)
        ran = True
    if args.mortgage:
        if args.amount is None:
            parser.error("--mortgage needs --amount")
        calc_mortgage(args.amount, args.years, args.rate)
        ran = True
    if args.max_loan:
        if args.payment is None:
            parser.error("--max-loan needs --payment")
        calc_max_loan(args.payment, args.years, args.rate)
        ran = True
    if not ran:
        parser.print_help()

if __name__ == "__main__":
    main()
