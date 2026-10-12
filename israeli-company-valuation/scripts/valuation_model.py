#!/usr/bin/env python3
"""
Israeli private company valuation model.

Builds a WACC from components, runs a free-cash-flow-to-firm DCF, bridges
enterprise value to equity value, applies marketability and control discounts,
and prints a sensitivity grid.

Design rules baked in deliberately:

  * The risk-free rate is a REQUIRED argument. There is no default. The shekel
    yield curve moves continuously, so any built-in value would ship stale.
    Read it live from the Bank of Israel yield page, or from the Tel Aviv
    Stock Exchange government bond data.

  * The country risk premium carries a vintage date and is printed with every
    run, so a reader can see how old the parameter is.

  * The same effective tax rate is used in the cash flow tax line and in the
    debt tax shield. They cannot diverge.

  * The effective tax rate is also REQUIRED. Defaulting to the statutory 23%
    is exactly the error the skill exists to prevent for a preferred
    enterprise, so the operator has to state it.

  * Output is a range with a sensitivity grid, never a single point. The
    headline range is EQUITY value of the stake being valued, after the
    bridge and the discounts, across WACC, terminal growth and the
    marketability discount. Enterprise value is shown, but it is not the
    answer to "what is my stake worth".

  * Inputs are decimals. Out-of-range values (a discount of 25 instead of
    0.25, a tax rate of 23) are rejected rather than computed.

Usage:
    python3 valuation_model.py --example
    python3 valuation_model.py --risk-free 0.041 --ebit 5000000 --tax-rate 0.23 \\
        --growth 0.03 --terminal-growth 0.02 --beta 1.1 --net-debt 2000000 \\
        --stake 0.30 --dlom 0.20 --dloc 0.10

All monetary inputs are in whole shekels unless stated otherwise.
"""

import argparse
import datetime
import sys

# Country risk parameters. Vintage is printed on every run so the reader can
# judge staleness. Re-verify against the source in evidence.json at each update.
COUNTRY_DATA_VINTAGE = "July 2026"
COUNTRY_DATA_VINTAGE_ISO = "2026-07-09"
# The date a reviewer last confirmed, on the data-current index, that no newer
# file exists. Staleness runs from here, not from the vintage, so a file that is
# still the newest one does not trip the warning on every run. Bump it at each
# review that re-confirms the vintage.
COUNTRY_DATA_CONFIRMED_ISO = "2026-10-12"
# The dataset updates at least twice a year and sometimes in between (an April
# 2026 file sat between January and July). Past this many days we stop
# trusting it silently and tell the operator to refetch, mirroring the
# risk-free rule.
COUNTRY_DATA_STALE_AFTER_DAYS = 90
ISRAEL_COUNTRY_RISK_PREMIUM = 0.0198
ISRAEL_TOTAL_EQUITY_RISK_PREMIUM = 0.061783  # already includes the country premium
# Published mature-market ERP from the SAME vintage (US ERP less the US adjusted
# default spread). Held as its own constant on purpose: deriving it as
# total minus country premium lets a half-override invert the sign of country
# risk, because a fresh, larger country premium is then subtracted from a stale
# total. Keep all three in step whenever the vintage is refreshed.
MATURE_MARKET_ERP = 0.0420
ISRAEL_SOVEREIGN_RATING = "Baa1"

SCOPE_LIMIT = """
SCOPE LIMIT
This is an indicative valuation range produced from the inputs supplied. It is
not a signed valuation opinion, and it is not fit to submit to the Israel Tax
Authority, to a court, or into financial statements. Israel has no statutory
licence for a business valuer, so acceptance turns on the professional standing,
independence, and documentation of whoever signs it. For any transaction,
filing, or reorganization, engage a certified public accountant or a
credentialed valuer to prepare and sign the valuation.

This range is also pre-tax to the seller, it is not a negotiated price, and it
does not account for the terms of any shareholders' agreement. Do not sign a
share purchase agreement, set a negotiating anchor, or assume this is what you
net, on the strength of this output alone.
""".strip()


def cost_of_equity(risk_free, beta, size_premium, specific_premium,
                   use_total_erp=True):
    """
    Build the cost of equity.

    use_total_erp=True uses the Israel total equity risk premium, which already
    contains the country premium. Adding the country premium again on top would
    be a double count, so this function refuses to do it.
    """
    if use_total_erp:
        market_component = beta * ISRAEL_TOTAL_EQUITY_RISK_PREMIUM
        country_component = 0.0
        convention = ("beta x Israel total ERP (country premium already "
                      "included, not added again)")
    else:
        market_component = beta * MATURE_MARKET_ERP
        country_component = ISRAEL_COUNTRY_RISK_PREMIUM
        convention = "beta x mature-market ERP, plus country premium separately"

    total = (risk_free + market_component + country_component
             + size_premium + specific_premium)
    return total, convention


def wacc(ke, kd_pretax, tax_rate, equity_weight):
    """Weighted average cost of capital. Tax shield uses the SAME rate as FCFF."""
    if not 0.0 <= equity_weight <= 1.0:
        raise ValueError("equity_weight must be between 0 and 1")
    debt_weight = 1.0 - equity_weight
    kd_after_tax = kd_pretax * (1.0 - tax_rate)
    return ke * equity_weight + kd_after_tax * debt_weight


def project_fcff(ebit, tax_rate, dep, capex, delta_wc, growth, years,
                 nol=0.0):
    """
    Free cash flow to firm, grown at `growth` for `years`.

    FCFF = EBIT - tax on EBIT + D&A - capex - change in working capital

    `nol` is a balance of carried-forward business losses. It shelters EBIT
    from tax in the explicit years until it is used up. The terminal value
    must NOT inherit that shelter, so the fully taxed final-year FCFF is
    returned separately for it.
    """
    flows = []
    remaining = max(nol, 0.0)
    full_tax_last = None
    for year in range(1, years + 1):
        factor = (1.0 + growth) ** year
        f_ebit = ebit * factor
        f_dep = dep * factor
        f_capex = capex * factor
        f_wc = delta_wc * factor
        sheltered = min(remaining, max(f_ebit, 0.0))
        remaining -= sheltered
        taxable = f_ebit - sheltered
        tax = tax_rate * taxable if taxable > 0 else 0.0
        flows.append(f_ebit - tax + f_dep - f_capex - f_wc)
        full_tax_last = f_ebit * (1.0 - tax_rate) + f_dep - f_capex - f_wc
    return flows, full_tax_last, remaining


def discount(flows, rate):
    return sum(f / ((1.0 + rate) ** (i + 1)) for i, f in enumerate(flows))


def terminal_value(last_fcff, rate, terminal_growth, years):
    if terminal_growth >= rate:
        raise ValueError(
            "terminal growth (%.4f) must be below the discount rate (%.4f). "
            "A growth rate at or above the discount rate implies infinite value."
            % (terminal_growth, rate)
        )
    tv = last_fcff * (1.0 + terminal_growth) / (rate - terminal_growth)
    return tv / ((1.0 + rate) ** years)


def enterprise_value(ebit, tax_rate, dep, capex, delta_wc, growth,
                     terminal_growth, rate, years, nol=0.0):
    flows, full_tax_last, _ = project_fcff(ebit, tax_rate, dep, capex,
                                           delta_wc, growth, years, nol)
    pv_explicit = discount(flows, rate)
    pv_terminal = terminal_value(full_tax_last, rate, terminal_growth, years)
    return pv_explicit + pv_terminal, pv_explicit, pv_terminal


def equity_bridge(ev, net_debt, surplus_assets, contingent_liabilities,
                  severance_shortfall):
    return (ev - net_debt + surplus_assets - contingent_liabilities
            - severance_shortfall)


def apply_discounts(equity, dlom, dloc):
    """
    Discounts are multiplicative, not additive. A discount on NEGATIVE equity
    would raise the value, so negative equity is returned untouched.
    """
    if equity <= 0:
        return equity
    return equity * (1.0 - dlom) * (1.0 - dloc)


def stake_value(ev, bridge, stake, dlom, dloc):
    """
    Enterprise value -> equity -> the stake being valued -> discounts.

    Floored at zero: with limited liability a shareholding is not worth less
    than nothing (absent guarantees, which belong in the bridge as liabilities).
    """
    eq = equity_bridge(ev, **bridge)
    return max(apply_discounts(eq * stake, dlom, dloc), 0.0)


# A grid cell whose WACC sits within this distance of terminal growth is close
# to the Gordon singularity, so one cell would set the published high end.
MIN_GRID_SPREAD = 0.015


def sensitivity_grid(base_args, rate_steps, growth_steps, base_rate=None,
                     base_growth=None):
    """Enterprise value across a WACC band and a terminal growth band."""
    rows = []
    for r in rate_steps:
        row = []
        for g in growth_steps:
            is_base = (r == base_rate and g == base_growth)
            if r - g < MIN_GRID_SPREAD and not is_base:
                row.append(None)
                continue
            try:
                ev, _, _ = enterprise_value(
                    base_args["ebit"], base_args["tax_rate"], base_args["dep"],
                    base_args["capex"], base_args["delta_wc"],
                    base_args["growth"], g, r, base_args["years"],
                    base_args["nol"],
                )
                row.append(ev)
            except ValueError:
                row.append(None)
        rows.append((r, row))
    return rows


def country_data_age_days():
    """Days since the vintage was last confirmed to be the newest file."""
    confirmed = datetime.date.fromisoformat(COUNTRY_DATA_CONFIRMED_ISO)
    return (datetime.date.today() - confirmed).days


def pct0(x):
    """Percent with no decimals. Kept out of format literals on purpose."""
    return "{:.0f}".format(x * 100.0) + "%"


def pct1(x):
    """Percent with one decimal."""
    return "{:.1f}".format(x * 100.0) + "%"


def fmt(n):
    if n is None:
        return "{:>14}".format("n/a")
    return "{:>14,.0f}".format(n)


# (low, high) bounds for decimal inputs. A value outside them is almost always
# a percent typed as a whole number (25 instead of 0.25), which would otherwise
# be computed into a confident, absurd figure.
BOUNDS = {
    "risk_free": (-0.02, 0.20),
    "beta": (0.0, 5.0),
    "size_premium": (0.0, 0.20),
    "specific_premium": (0.0, 0.25),
    "country_risk_premium": (0.0, 0.20),
    "total_erp": (0.0, 0.25),
    "mature_erp": (0.0, 0.15),
    "kd": (0.0, 0.30),
    "equity_weight": (0.0, 1.0),
    "tax_rate": (0.0, 0.50),
    "growth": (-0.50, 0.50),
    "terminal_growth": (-0.05, 0.10),
    "dlom": (0.0, 0.90),
    "dloc": (0.0, 0.90),
}


def validate(p, a):
    for name, (lo, hi) in BOUNDS.items():
        v = getattr(a, name)
        if v is None:
            continue
        if not lo <= v <= hi:
            flag = "--" + name.replace("_", "-")
            p.error("%s=%s is outside %s to %s. Inputs are decimals: pass 0.25 "
                    "for 25%%, not 25." % (flag, v, lo, hi))
    if not 1 <= a.years <= 30:
        p.error("--years must be between 1 and 30")
    if not 0.0 < a.stake <= 1.0:
        p.error("--stake must be above 0 and at most 1 (0.30 for a 30% stake)")
    if a.nol < 0:
        p.error("--nol is a loss balance and cannot be negative")


def main():
    p = argparse.ArgumentParser(
        description="Israeli private company valuation model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--example", action="store_true",
                   help="run with illustrative inputs and exit")
    p.add_argument("--risk-free", type=float,
                   help="REQUIRED. Shekel government bond yield to maturity, "
                        "as a decimal (e.g. 0.041). Read live from the Bank of "
                        "Israel. No default is provided on purpose.")
    p.add_argument("--beta", type=float, default=None,
                   help="relevered equity beta. Treated as 1.0 if omitted, and "
                        "the output says so.")
    p.add_argument("--size-premium", type=float, default=None,
                   help="size premium as a decimal. Name your source in the "
                        "output. Treated as 0 if omitted, and the output says so.")
    p.add_argument("--specific-premium", type=float, default=None,
                   help="company-specific risk premium as a decimal. Treated as "
                        "0 if omitted, and the output says so.")
    p.add_argument("--country-risk-premium", type=float,
                   help="override the built-in Israel country risk premium as a "
                        "decimal. Supply a freshly fetched value; the built-in "
                        "one carries a vintage and goes stale.")
    p.add_argument("--total-erp", type=float,
                   help="override the built-in Israel total equity risk premium "
                        "as a decimal (country premium included).")
    p.add_argument("--mature-erp", type=float, default=None,
                   help="Mature-market ERP from the same vintage. Used only "
                        "with --separate-country-premium.")
    p.add_argument("--separate-country-premium", action="store_true",
                   help="use mature-market ERP plus a separate country premium "
                        "instead of the Israel total ERP")
    p.add_argument("--kd", type=float, default=None,
                   help="pre-tax cost of debt. Treated as 6%% if omitted, and "
                        "the output says so.")
    p.add_argument("--equity-weight", type=float, default=None,
                   help="equity share of the capital structure, 0 to 1. "
                        "Treated as 1.0 (no debt) if omitted, and the output "
                        "says so. Use target weights the bridge also reflects.")
    p.add_argument("--ebit", type=float,
                   help="REQUIRED. Normalized EBIT, year 0. Profit BEFORE TAX is "
                        "not EBIT: add back net interest expense and remove "
                        "interest income on surplus cash first.")
    p.add_argument("--tax-rate", type=float, default=None,
                   help="REQUIRED. The company's OWN effective rate as a decimal. "
                        "No default on purpose: 0.23 is wrong for a preferred "
                        "enterprise. See SKILL.md step 4.")
    p.add_argument("--nol", type=float, default=0.0,
                   help="carried-forward business losses available to offset "
                        "future EBIT. Used in the explicit years only; the "
                        "terminal value is fully taxed.")
    p.add_argument("--dep", type=float, default=0.0, help="depreciation and amortization")
    p.add_argument("--capex", type=float, default=0.0, help="capital expenditure")
    p.add_argument("--delta-wc", type=float, default=0.0, help="change in working capital")
    p.add_argument("--growth", type=float, default=0.03, help="explicit-period growth")
    p.add_argument("--terminal-growth", type=float, default=0.02)
    p.add_argument("--years", type=int, default=5)
    p.add_argument("--net-debt", type=float, default=0.0)
    p.add_argument("--surplus-assets", type=float, default=0.0)
    p.add_argument("--contingent-liabilities", type=float, default=0.0)
    p.add_argument("--severance-shortfall", type=float, default=0.0,
                   help="UNFUNDED severance only. Where employees are under a "
                        "full section 14 arrangement there is no company-level "
                        "shortfall for that pay, so pass 0 for them.")
    p.add_argument("--stake", type=float, default=1.0,
                   help="fraction of equity being valued, on the denominator "
                        "fixed in step 1 (e.g. 0.30). Default 1.0 = whole company.")
    p.add_argument("--dlom", type=float, default=0.0,
                   help="marketability discount as a decimal. There is no "
                        "Israeli published range; cite your empirical basis.")
    p.add_argument("--dloc", type=float, default=0.0,
                   help="lack-of-control discount. Only for a genuinely "
                        "non-controlling interest.")
    p.add_argument("--exit-multiple", type=float, default=None,
                   help="optional sector EV/EBITDA multiple for an exit-multiple "
                        "terminal value, run alongside Gordon growth")

    a = p.parse_args()

    if a.example:
        a.risk_free = 0.041
        a.ebit = 5_000_000
        a.tax_rate = 0.23
        a.dep = 400_000
        a.capex = 500_000
        a.delta_wc = 150_000
        a.beta = 1.1
        a.size_premium = 0.03
        a.specific_premium = 0.01
        a.net_debt = 2_000_000
        a.severance_shortfall = 300_000
        a.equity_weight = 0.90
        a.kd = 0.06
        a.stake = 0.30
        a.dlom = 0.25
        print("Running with ILLUSTRATIVE inputs. These are not market data.\n")

    if a.risk_free is None:
        p.error("--risk-free is required. Read the current shekel government "
                "bond yield from the Bank of Israel rather than using a "
                "remembered value. See SKILL.md step 5.")
    if a.ebit is None:
        p.error("--ebit is required (normalized EBIT). Run the normalization "
                "bridge first, see SKILL.md step 3.")
    if a.tax_rate is None:
        p.error("--tax-rate is required. Establish the company's own regime "
                "first (SKILL.md step 4); do not default to 23%.")
    validate(p, a)

    if a.ebit <= 0:
        # A DCF on non-positive cash flow is not a valuation. Printing one, with
        # a range and a terminal-share line, invites someone to quote it.
        print("Normalized EBIT is zero or negative, so no DCF valuation is")
        print("produced. Use the asset approach or, for a pre-revenue company,")
        print("the round-based methods in references/valuation-methods.md.")
        print("\n" + SCOPE_LIMIT)
        return 1

    assumed = []
    if a.beta is None:
        a.beta = 1.0
        assumed.append("beta 1.00 (market average, not relevered)")
    if a.size_premium is None:
        a.size_premium = 0.0
        assumed.append("size premium 0")
    if a.specific_premium is None:
        a.specific_premium = 0.0
        assumed.append("company-specific premium 0")
    if a.equity_weight is None:
        a.equity_weight = 1.0
        assumed.append("all-equity capital structure")
    if a.kd is None:
        a.kd = 0.06
        if a.equity_weight < 1.0:
            assumed.append("pre-tax cost of debt 6%")

    # Each convention consumes different premia. Accepting a premium the
    # chosen convention ignores would print it as if it had been used.
    if not a.separate_country_premium and (a.country_risk_premium is not None
                                           or a.mature_erp is not None):
        p.error("--country-risk-premium and --mature-erp are used only with "
                "--separate-country-premium. In the default convention pass the "
                "refreshed Israel total ERP (country premium included) as "
                "--total-erp.")
    if a.separate_country_premium and a.total_erp is not None:
        p.error("--total-erp is not used with --separate-country-premium. Pass "
                "--country-risk-premium and --mature-erp instead.")

    global ISRAEL_COUNTRY_RISK_PREMIUM, ISRAEL_TOTAL_EQUITY_RISK_PREMIUM
    global MATURE_MARKET_ERP
    if a.country_risk_premium is not None:
        ISRAEL_COUNTRY_RISK_PREMIUM = a.country_risk_premium
    if a.total_erp is not None:
        ISRAEL_TOTAL_EQUITY_RISK_PREMIUM = a.total_erp
    if a.mature_erp is not None:
        MATURE_MARKET_ERP = a.mature_erp

    # Only the parameters actually consumed by the chosen convention count as
    # refreshed. Keying this off the wrong one is how a stale premium used to
    # drive the answer with the warning suppressed.
    if a.separate_country_premium:
        overrode_in_use = (a.country_risk_premium is not None
                           and a.mature_erp is not None)
    else:
        overrode_in_use = a.total_erp is not None
    # Only the separate convention consumes two premia, so only it can mix
    # vintages (one refreshed, one built in).
    overrode_any = a.separate_country_premium and (
        a.country_risk_premium is not None or a.mature_erp is not None)
    age = country_data_age_days()
    stale = age > COUNTRY_DATA_STALE_AFTER_DAYS and not overrode_in_use

    ke, convention = cost_of_equity(
        a.risk_free, a.beta, a.size_premium, a.specific_premium,
        use_total_erp=not a.separate_country_premium,
    )
    w = wacc(ke, a.kd, a.tax_rate, a.equity_weight)

    # Positive EBIT is not enough: heavy reinvestment can make the terminal
    # free cash flow negative, and a Gordon value on it is a negative number
    # that would be printed as a range.
    _, full_tax_last_chk, _ = project_fcff(
        a.ebit, a.tax_rate, a.dep, a.capex, a.delta_wc, a.growth, a.years,
        a.nol)
    if full_tax_last_chk <= 0:
        print("Final-year free cash flow is zero or negative (reinvestment is")
        print("larger than after-tax operating profit), so a perpetuity on it has")
        print("no meaning and no DCF valuation is produced. Normalise terminal")
        print("reinvestment to the terminal growth rate, or use the asset approach")
        print("or the methods in references/valuation-methods.md.")
        print("\n" + SCOPE_LIMIT)
        return 1

    ev, pv_explicit, pv_terminal = enterprise_value(
        a.ebit, a.tax_rate, a.dep, a.capex, a.delta_wc,
        a.growth, a.terminal_growth, w, a.years, a.nol,
    )
    bridge = dict(net_debt=a.net_debt, surplus_assets=a.surplus_assets,
                  contingent_liabilities=a.contingent_liabilities,
                  severance_shortfall=a.severance_shortfall)
    eq = equity_bridge(ev, **bridge)
    eq_stake = eq * a.stake
    eq_after = apply_discounts(eq_stake, a.dlom, a.dloc)

    # Implied exit multiple of the Gordon terminal value, on terminal-year
    # EBITDA, so the terminal assumption can be compared with sector data.
    flows, full_tax_last, nol_left = project_fcff(
        a.ebit, a.tax_rate, a.dep, a.capex, a.delta_wc, a.growth, a.years,
        a.nol)
    factor_n = (1.0 + a.growth) ** a.years
    ebitda_n = (a.ebit + a.dep) * factor_n
    tv_n = full_tax_last * (1.0 + a.terminal_growth) / (w - a.terminal_growth)
    implied_exit = tv_n / ebitda_n if ebitda_n > 0 else None

    print("=" * 68)
    print("ISRAELI COMPANY VALUATION, INDICATIVE")
    print("=" * 68)
    print(SCOPE_LIMIT)
    print("\nCOUNTRY PARAMETERS")
    if overrode_in_use:
        print("  Dataset vintage        : supplied on the command line, NOT %s"
              % COUNTRY_DATA_VINTAGE)
        print("                           record the vintage you read in the write-up")
    elif overrode_any:
        print("  Dataset vintage        : MIXED. Some premia supplied on the command")
        print("                           line, the rest are the built-in %s values,"
              % COUNTRY_DATA_VINTAGE)
        print("                           so the cost of equity mixes vintages")
    else:
        print("  Dataset vintage        : %s (built in)" % COUNTRY_DATA_VINTAGE)
    print("  Sovereign rating       : %s" % ISRAEL_SOVEREIGN_RATING)
    if a.separate_country_premium:
        print("  Mature-market ERP      : {:.2%}".format(MATURE_MARKET_ERP))
        print("  Country risk premium   : {:.2%}".format(ISRAEL_COUNTRY_RISK_PREMIUM))
    else:
        print("  Israel total ERP       : {:.2%}  (country premium included)"
              .format(ISRAEL_TOTAL_EQUITY_RISK_PREMIUM))
    if not overrode_in_use:
        print("  Confirmed newest file  : %s, %d days ago"
              % (COUNTRY_DATA_CONFIRMED_ISO, age))
    if stale:
        print("  WARNING: no one has confirmed this is the newest country risk file in")
        print("  the last %d days. Check the" % COUNTRY_DATA_STALE_AFTER_DAYS)
        print("  data-current index for a newer file. Refetch and pass --total-erp (or, with")
        print("  --separate-country-premium, BOTH --country-risk-premium and")
        print("  --mature-erp), or say in the write-up that a stale premium was used.")
    else:
        print("  Check the vintage above against the data-current index.")

    print("\nDISCOUNT RATE BUILD-UP")
    print("  Risk-free rate         : {:.2%}  (must be read live)".format(a.risk_free))
    print("  Beta                   : {:.2f}".format(a.beta))
    print("  Convention             : %s" % convention)
    print("  Size premium           : {:.2%}".format(a.size_premium))
    print("  Company-specific       : {:.2%}".format(a.specific_premium))
    print("  Cost of equity         : {:.2%}".format(ke))
    print("  Pre-tax cost of debt   : {:.2%}".format(a.kd))
    print("  Effective tax rate     : {:.2%}  (same rate used in FCFF)".format(a.tax_rate))
    print("  Equity weight          : {:.0%}".format(a.equity_weight))
    print("  WACC                   : {:.2%}".format(w))
    if assumed:
        print("  ASSUMED, NOT SUPPLIED  : " + "; ".join(assumed))
        print("                           Build each one (SKILL.md step 5) or")
        print("                           disclose it as an assumption.")
    if a.equity_weight < 1.0 and a.net_debt <= 0:
        print("  NOTE: the WACC carries %s debt but the bridge has no net debt. Use"
              % pct0(1.0 - a.equity_weight))
        print("  target weights the bridge also reflects, or state why they differ.")

    print("\nVALUATION, WHOLE COMPANY")
    print("  PV of explicit period  : {:>18,.0f}".format(pv_explicit))
    print("  PV of terminal value   : {:>18,.0f}".format(pv_terminal))
    print("  Terminal share of EV   : " + pct0(pv_terminal / ev if ev else 0).rjust(17))
    print("  Enterprise value       : {:>18,.0f}".format(ev))
    print("  Discounting            :  end of year (mid-year would be higher)")
    print("  Implied EV/EBIT, yr 0  : {:>17.1f}x".format(ev / a.ebit))
    if "size premium 0" in assumed and "company-specific premium 0" in assumed:
        print("  NOTE: no size or company-specific premium was supplied. For a small")
        print("  owner-managed company, check this multiple against private-deal")
        print("  evidence before quoting anything (SKILL.md step 9).")
    if implied_exit is not None:
        print("  Implied exit EV/EBITDA : {:>17.1f}x  (terminal value / year-{} EBITDA)"
              .format(implied_exit, a.years))
    print("  Less net debt          : {:>18,.0f}".format(-a.net_debt))
    print("  Plus surplus assets    : {:>18,.0f}".format(a.surplus_assets))
    print("  Less contingents       : {:>18,.0f}".format(-a.contingent_liabilities))
    print("  Less severance gap     : {:>18,.0f}".format(-a.severance_shortfall))
    print("  Equity value, whole co : {:>18,.0f}".format(eq))
    if a.nol:
        print("  Losses used in forecast: {:>18,.0f}  (unused at year {}: {:,.0f})"
              .format(a.nol - nol_left, a.years, nol_left))
        if nol_left > 0:
            print("  NOTE: losses still unused at the end of the forecast are not")
            print("  valued here, which understates value. Extend --years or value")
            print("  the remaining shield separately.")

    print("\nVALUATION, STAKE")
    print("  Stake valued           : " + pct1(a.stake).rjust(17)
          + "  (pro rata; no class waterfall)")
    print("  Pro rata equity        : {:>18,.0f}".format(eq_stake))
    print("  Marketability discount : " + pct0(a.dlom).rjust(17))
    print("  Control discount       : " + pct0(a.dloc).rjust(17))
    print("  Stake after discounts  : {:>18,.0f}".format(max(eq_after, 0.0)))
    if a.stake < 1.0 and a.dloc == 0:
        print("  Control premium        :     not modelled. If the buyer ends up in")
        print("                           control, see SKILL.md step 8.")
    if eq <= 0:
        print("  NOTE: equity is negative, so no discount was applied, and the")
        print("  shares are worth nothing on this DCF beyond any option value.")

    if a.exit_multiple is not None:
        ev_exit = pv_explicit + (ebitda_n * a.exit_multiple) / ((1.0 + w) ** a.years)
        print("\nEXIT-MULTIPLE CROSS-CHECK")
        print("  Exit EV/EBITDA used    : {:>17.1f}x".format(a.exit_multiple))
        print("  Enterprise value       : {:>18,.0f}".format(ev_exit))
        print("  Gordon vs exit gap     : " + pct0(ev / ev_exit - 1.0).rjust(17))
        if ev_exit > 0 and abs(ev / ev_exit - 1.0) > 0.25:
            print("  NOTE: the two terminal constructions differ by more than a")
            print("  quarter. The terminal assumption is doing the work; say which")
            print("  one you rely on and why.")

    if ev and (pv_terminal / ev) > 0.75:
        print("\n  NOTE: terminal value is more than three quarters of enterprise")
        print("  value. The answer is driven by the terminal assumption, not by")
        print("  the forecast. Say so explicitly in the write-up.")
    if a.growth > a.terminal_growth + 0.02 and (a.capex > a.dep or a.delta_wc > 0):
        print("\n  NOTE: the terminal cash flow carries reinvestment sized for")
        print("  explicit-period growth into a perpetuity growing more slowly,")
        print("  which understates the terminal value. Consider normalising it.")
    if a.growth > 0 and a.capex <= a.dep and a.delta_wc <= 0:
        print("\n  NOTE: the forecast grows with no net reinvestment (capex at or")
        print("  below depreciation, no working capital build). Growth is not free;")
        print("  justify it or add the reinvestment.")

    rate_steps = [w - 0.02, w - 0.01, w, w + 0.01, w + 0.02]
    growth_steps = [a.terminal_growth - 0.01, a.terminal_growth,
                    a.terminal_growth + 0.01]
    base = dict(ebit=a.ebit, tax_rate=a.tax_rate, dep=a.dep, capex=a.capex,
                delta_wc=a.delta_wc, growth=a.growth, years=a.years,
                nol=a.nol)
    grid = sensitivity_grid(base, rate_steps, growth_steps,
                            base_rate=w, base_growth=a.terminal_growth)
    dlom_steps = sorted({max(0.0, a.dlom - 0.05), a.dlom, min(0.9, a.dlom + 0.05)}) \
        if a.dlom else [0.0]

    print("\nSENSITIVITY, STAKE VALUE AFTER DISCOUNTS (DLOM %s)" % pct0(a.dlom))
    print("  rows = WACC, columns = terminal growth")
    header = "  " + "WACC".ljust(10) + "".join(
        "{:>14}".format("g=" + pct1(g)) for g in growth_steps)
    print(header)
    ev_lo = ev_hi = st_lo = st_hi = None
    for r, row in grid:
        line = "  " + "{:.2%}".format(r).ljust(10)
        for v in row:
            if v is None:
                line += fmt(None)
                continue
            ev_lo = v if ev_lo is None or v < ev_lo else ev_lo
            ev_hi = v if ev_hi is None or v > ev_hi else ev_hi
            line += fmt(stake_value(v, bridge, a.stake, a.dlom, a.dloc))
            for d in dlom_steps:
                sv = stake_value(v, bridge, a.stake, d, a.dloc)
                st_lo = sv if st_lo is None or sv < st_lo else st_lo
                st_hi = sv if st_hi is None or sv > st_hi else st_hi
        print(line)

    if st_lo is not None:
        if a.dlom:
            print("\n  The range below also spans DLOM %s."
                  % " / ".join(pct0(d) for d in dlom_steps))
        if w - a.terminal_growth < MIN_GRID_SPREAD:
            print("  NOTE: the base WACC is within %s of terminal growth, close to the"
                  % pct1(MIN_GRID_SPREAD))
            print("  Gordon singularity, so the base case itself sets the high end.")
            print("  Revisit the WACC or the terminal growth before presenting this.")
            if any(v is None for _, row in grid for v in row):
                print("  Other cells that close to the singularity show n/a.")
        elif any(v is None for _, row in grid for v in row):
            print("  Cells marked n/a sit within %s of terminal growth and were left"
                  % pct1(MIN_GRID_SPREAD))
            print("  out, so one near-singular cell cannot set the high end.")
        label = ("WHOLE COMPANY EQUITY" if a.stake == 1.0
                 else "%s STAKE" % pct1(a.stake))
        print("\n  Indicative %s RANGE, after bridge and discounts:" % label)
        print("    {:,.0f} to {:,.0f}".format(st_lo, st_hi))
        print("  For reference only, enterprise value (whole company, before debt")
        print("  and discounts) spans {:,.0f} to {:,.0f}. Do not quote it as the"
              .format(ev_lo, ev_hi))
        print("  value of a stake.")
        if st_lo <= 0:
            print("  NOTE: the low end is zero. Under %s inputs in the grid equity"
                  % ("all" if st_hi <= 0 else "some"))
            print("  is wiped out by debt and the other bridge items.")
        elif st_hi / st_lo > 2.0:
            base_lo = min(stake_value(v, bridge, a.stake, a.dlom, a.dloc)
                          for _, row in grid for v in row if v is not None)
            base_hi = max(stake_value(v, bridge, a.stake, a.dlom, a.dloc)
                          for _, row in grid for v in row if v is not None)
            causes = []
            if base_lo > 0 and base_hi / base_lo > 1.5:
                causes.append("the WACC and terminal growth inputs")
            if len(dlom_steps) > 1:
                causes.append("the marketability discount band")
            if eq > 0 and ev / eq > 1.5:
                causes.append("leverage (equity is a thin slice of enterprise value)")
            print("  NOTE: the high end is more than twice the low end. Widest drivers")
            print("  here: %s. Narrow those inputs before presenting it."
                  % ", ".join(causes or ["the combined inputs"]))
        print("  Report the range. The central figure is a midpoint, not an answer.")

    print("\n" + SCOPE_LIMIT)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as exc:
        # These are the deliberate guard-rail messages raised above. Printing
        # the traceback instead buries the explanation the user needs.
        sys.stderr.write("error: %s\n" % exc)
        sys.exit(2)
