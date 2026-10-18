#!/usr/bin/env python3
"""Fetch and convert currencies using Bank of Israel exchange rates.

Current rates come from the live Bank of Israel JSON endpoint. Historical
(tax-date) rates come from the Bank of Israel SDMX EXR series, because the
JSON endpoint's ?date= parameter is ignored and always returns the most
recently published rate. Note that "most recently published" is not the same as
"today": the endpoint keeps serving the previous publication until the next one
lands, so before the daily publication it returns the PREVIOUS business day's
rate. The date reported for a conversion is therefore always taken from the
endpoint's own lastUpdate field (or the SDMX TIME_PERIOD), never from the
system clock.

Usage:
    python scripts/fetch_rates.py --list
    python scripts/fetch_rates.py --from USD --to ILS --amount 1000
    python scripts/fetch_rates.py --from ILS --to EUR --amount 5000
    python scripts/fetch_rates.py --from USD --to ILS --amount 100 --date 2026-01-15
"""

import sys
import argparse
import json
import csv
import io
import math
import ssl
from datetime import date, datetime, timedelta, timezone
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from typing import Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None


# Live JSON endpoint for current representative rates.
BOI_CURRENT_URL = "https://www.boi.org.il/PublicApi/GetExchangeRates"
# SDMX EXR series for historical rates: insert the currency code and date range.
BOI_SDMX_URL = (
    "https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/"
    "BOI.STATISTICS/EXR/1.0/RER_{cur}_ILS"
    "?startPeriod={start}&endPeriod={end}&format=csv"
)

# The 14 currencies the Bank of Israel publishes a representative rate for,
# with their Hebrew transliterations.
COMMON_CURRENCIES = {
    "USD": ("US Dollar", "dolar"),
    "GBP": ("British Pound", "lira sterling"),
    "JPY": ("Japanese Yen", "yen"),
    "EUR": ("Euro", "euro"),
    "AUD": ("Australian Dollar", "dolar australi"),
    "CAD": ("Canadian Dollar", "dolar kanadi"),
    "DKK": ("Danish Krone", "krone dani"),
    "NOK": ("Norwegian Krone", "krone norvegi"),
    "ZAR": ("South African Rand", "rand"),
    "SEK": ("Swedish Krona", "krona shvedit"),
    "CHF": ("Swiss Franc", "frank shveitzi"),
    "JOD": ("Jordanian Dinar", "dinar yardeni"),
    "LBP": ("Lebanese Pound", "lira levanonit"),
    "EGP": ("Egyptian Pound", "lira mitzrit"),
}

# One new shekel replaced 1,000 old shekels on this date. The SDMX series runs
# back past it, with earlier observations expressed in new-shekel terms.
CURRENCY_REFORM_DATE = "1985-09-04"
# The (old) shekel replaced the Israeli pound (lira) on this date.
SHEKEL_INTRODUCED_DATE = "1980-02-24"

# Rounding a published rate to its last decimal place bounds a converted total
# by +/- half a unit in that place, relative to the rate. Warn above this.
PRECISION_WARN_PCT = 0.5


class RateFetchError(Exception):
    """Raised when a real rate cannot be fetched. The caller must FAIL LOUD and
    must never substitute sample data for a tax-stamped conversion."""


def israel_today() -> date:
    """Today's date in Israel, which is what decides whether a rate is due.

    The machine's local date is wrong for this: a user in Tokyo after midnight
    can be a calendar day ahead of Israel.
    """
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo("Asia/Jerusalem")).date()
        except Exception:
            pass
    # Fallback without tz data: Israel is UTC+2 or UTC+3; UTC+2 is the safe
    # side (it never runs ahead of Israel).
    return (datetime.now(timezone.utc) + timedelta(hours=2)).date()


def _open(url: str, timeout: int):
    """Open a URL with certificate verification, retrying on the certifi bundle.

    edge.boi.gov.il chains to the Sectigo Public Server Authentication Root R46,
    which some system CA bundles (for example /etc/ssl/cert.pem on macOS with a
    python.org build) do not contain. When verification fails for that reason
    and certifi is installed, retry against certifi's bundle. Verification is
    never disabled.
    """
    try:
        return urlopen(url, timeout=timeout)
    except URLError as e:
        if not isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError):
            raise
        try:
            import certifi
        except ImportError:
            raise URLError(
                f"{e.reason}. Install certifi (pip install certifi) or run "
                "Python's 'Install Certificates' step; verification is never "
                "disabled."
            ) from e
        ctx = ssl.create_default_context(cafile=certifi.where())
        return urlopen(url, timeout=timeout, context=ctx)


def fetch_current_rates() -> tuple[dict, dict]:
    """Fetch current representative rates from the Bank of Israel JSON endpoint.

    Returns:
        Tuple of (rates, stamps). rates maps currency code to
        (rate, unit, change_pct, raw_rate_text); change_pct is the percentage
        daily move, not an absolute NIS delta. stamps maps each currency to the
        date its rate was actually published, taken from that entry's own
        lastUpdate field. Each leg of a conversion is dated from ITS stamp, so
        a currency that stopped updating cannot borrow another's newer date.

        Do NOT substitute today's date. The endpoint keeps serving the previous
        publication until the next one lands (soon after 15:15, or soon after
        12:15 on Fridays and holiday eves, Israel time), so before today's
        publication it returns YESTERDAY's rate.

    Raises:
        RateFetchError: if the endpoint cannot be reached or returns no usable
            rates. The caller must abort, NOT fall back to sample data.
    """
    try:
        with _open(BOI_CURRENT_URL, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"), parse_float=str)
    except (URLError, ValueError) as e:
        raise RateFetchError(
            f"Could not fetch live rates from Bank of Israel: {e}"
        ) from e

    rates, stamps = {}, {}
    for entry in data.get("exchangeRates", []):
        code = entry.get("key")
        raw = entry.get("currentExchangeRate")
        stamp = entry.get("lastUpdate")
        if not code or raw in (None, "", 0):
            continue
        if not stamp:
            # An undated rate cannot be used for a date-attributed conversion.
            continue
        rates[code] = (float(raw), int(entry.get("unit", 1)),
                       float(entry.get("currentChange", 0) or 0), str(raw))
        stamps[code] = stamp[:10]
    if not rates:
        raise RateFetchError(
            "Bank of Israel endpoint returned no usable dated rates, so the "
            "publication date cannot be established. Refusing to emit a "
            "tax-stamped rate with an unknown date."
        )
    return rates, stamps


def fetch_historical_rate(currency: str, target_date: str) -> Optional[tuple]:
    """Fetch a historical representative rate from the SDMX EXR series.

    The series omits non-publication days (Saturday, Sunday, Israeli holidays,
    Christmas Day, New Year's Day, Easter), so this walks back to the most
    recent published date on or before target_date.

    Returns:
        Tuple of (rate, unit, used_date, raw_rate_text), or None if the series
        has no published observation in the look-back window (for example a
        date before the series or the currency began). The unit is derived
        from the SDMX UNIT_MULT column (unit = 10 ** UNIT_MULT).

    Raises:
        RateFetchError: if the SDMX endpoint cannot be reached. The caller must
            abort, NOT fall back to sample data.
    """
    currency = currency.upper()
    if currency == "ILS":
        return (1.0, 1, target_date, "1")

    # Look back up to 21 days to cross weekends + multi-day holiday clusters.
    end = datetime.strptime(target_date, "%Y-%m-%d").date()
    start = end - timedelta(days=21)
    url = BOI_SDMX_URL.format(
        cur=currency, start=start.isoformat(), end=end.isoformat()
    )
    try:
        with _open(url, timeout=20) as response:
            text = response.read().decode("utf-8")
    except HTTPError as e:
        if e.code == 404:
            # SDMX answers an empty window with 404, not an empty CSV. That is
            # "no data for this date", not an outage, and re-running won't help.
            return None
        raise RateFetchError(
            f"Could not fetch historical rate for {currency} from BOI SDMX: {e}"
        ) from e
    except URLError as e:
        raise RateFetchError(
            f"Could not fetch historical rate for {currency} from BOI SDMX: {e}"
        ) from e

    reader = csv.DictReader(io.StringIO(text))
    eligible = [r for r in reader
                if r.get("OBS_VALUE") and r.get("TIME_PERIOD", "") <= target_date]
    if not eligible:
        return None
    chosen = max(eligible, key=lambda r: r["TIME_PERIOD"])
    try:
        unit = 10 ** int(chosen.get("UNIT_MULT", "0"))
    except (TypeError, ValueError):
        unit = 1
    raw = chosen["OBS_VALUE"]
    return (float(raw), unit, chosen["TIME_PERIOD"], raw)


def _sample_rates() -> dict:
    """ILLUSTRATIVE sample rates for offline demo ONLY (2026-08-26 snapshot).

    These are NOT live and NOT the official representative rate. They are only
    reachable via the explicit --demo flag, and any output built from them is
    labeled as illustrative sample data that must not be used for tax.
    """
    sample = {
        "USD": ("2.972", 1),
        "EUR": ("3.4685", 1),
        "GBP": ("4.0511", 1),
        "JPY": ("1.8684", 100),
        "CHF": ("3.697", 1),
        "CAD": ("2.1441", 1),
        "AUD": ("2.1357", 1),
    }
    return {k: (float(v), u, 0.0, v) for k, (v, u) in sample.items()}


def _decimals(raw: str) -> int:
    """Decimal places in the published text, floored at 4.

    The JSON endpoint is a number, so a published trailing zero (EGP 0.0570)
    reaches us as 0.057. In the 2026-10-16 publication every non-USD rate
    carried 4 decimals and USD 3, so 4 is the floor; a longer published value
    keeps its own length.
    """
    text = raw.strip()
    places = len(text.split(".", 1)[1]) if "." in text else 0
    return max(places, 4)


def _margin_pct(raw: str) -> float:
    """Worst-case relative error from rounding the published rate."""
    value = float(raw)
    if value <= 0:
        return 0.0
    return 0.5 * 10 ** (-_decimals(raw)) / value * 100


def _fmt_rate(value: float) -> str:
    """Format a per-unit rate with at least four significant figures.

    A fixed 4-decimal format prints the Lebanese pound as "0.0000" and cuts a
    1979 dollar rate of 0.003309 to "0.0033", so the printed rate no longer
    reproduces the printed total. This is a DISPLAY fix only: it cannot add
    precision the Bank of Israel did not publish.
    """
    if value == 0:
        return "0"
    places = max(4, math.ceil(-math.log10(abs(value))) + 3)
    return f"{value:.{min(places, 12)}f}"


def _precision_warning(raw: str) -> Optional[str]:
    """Warn when rounding of the published rate alone moves the total materially.

    The Lebanese pound is published as 0.0003 per 10 units: rounding to the
    fourth decimal bounds any converted amount to about plus or minus 17
    percent. That IS the official representative rate, so using it is not
    wrong, but a total printed to the agora must not be presented as precise.
    """
    pct = _margin_pct(raw)
    if pct <= PRECISION_WARN_PCT:
        return None
    return (
        f"  WARNING: the Bank of Israel published this rate as {raw}, so rounding\n"
        f"        alone bounds the converted total to about +/-{pct:.1f}%. It is the\n"
        "        official published rate, but do not rely on the total to the\n"
        "        agora; confirm the figure with the Bank of Israel before filing."
    )


def _rate_label(currency: str, rate: float, unit: int, raw: str) -> str:
    """Show the rate on the unit basis the Bank of Israel published it on."""
    if unit == 1:
        return f"1 {currency} = {raw} ILS"
    return (f"{unit} {currency} = {raw} ILS as published "
            f"(1 {currency} = {_fmt_rate(rate / unit)} ILS)")


def convert(
    amount: float,
    from_currency: str,
    to_currency: str,
    rates: dict,
) -> Optional[tuple[float, float, str, bool]]:
    """Convert between currencies using Bank of Israel rates.

    Returns:
        Tuple of (result, rate_used, description, is_derived) or None if the
        conversion is impossible. is_derived is True for a cross between two
        foreign currencies, which the Bank of Israel never publishes.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == "ILS" and to_currency in rates:
        rate, unit, _, raw = rates[to_currency]
        return (amount / rate * unit, rate / unit,
                _rate_label(to_currency, rate, unit, raw), False)

    if to_currency == "ILS" and from_currency in rates:
        rate, unit, _, raw = rates[from_currency]
        return (amount * rate / unit, rate / unit,
                _rate_label(from_currency, rate, unit, raw), False)

    if from_currency in rates and to_currency in rates:
        from_rate, from_unit, _, _ = rates[from_currency]
        to_rate, to_unit, _, _ = rates[to_currency]
        nis_amount = amount * from_rate / from_unit
        result = nis_amount / to_rate * to_unit
        cross_rate = (from_rate / from_unit) / (to_rate / to_unit)
        return (
            result,
            cross_rate,
            f"1 {from_currency} = {_fmt_rate(cross_rate)} {to_currency} "
            "(DERIVED from two Bank of Israel shekel rates; the Bank of Israel "
            "publishes no direct rate for this pair)",
            True,
        )

    return None


def _same_day(resolved: dict) -> str:
    """Both legs must carry the SAME publication date, or the caller aborts.

    Stamping one date on a conversion built from two different days is the
    exact date-misattribution this skill exists to prevent.
    """
    distinct = sorted(set(resolved.values()))
    if len(distinct) > 1:
        detail = ", ".join(f"{c} published {d}" for c, d in sorted(resolved.items()))
        raise RateFetchError(
            "The two currencies carry different publication dates "
            f"({detail}). Refusing to stamp one date on a conversion built from "
            "two different days. Request each leg against the shekel separately."
        )
    return distinct[0]


def build_dated_rates(
    from_currency: str, to_currency: str, target_date: str
) -> tuple[dict, Optional[str]]:
    """Build a rates dict for a specific historical date using SDMX.

    Returns the rates dict plus the publication date used (earlier than
    target_date if the requested day had no publication), or None as the date
    when the series has no observation for a needed leg.
    """
    rates = {}
    resolved = {}
    for cur in sorted({from_currency.upper(), to_currency.upper()} - {"ILS"}):
        hist = fetch_historical_rate(cur, target_date)
        if hist is None:
            return rates, None
        rate, unit, when, raw = hist
        rates[cur] = (rate, unit, 0.0, raw)
        resolved[cur] = when
    return rates, _same_day(resolved)


def _live_if_newer(legs: set, used_date: str, target_date: str):
    """Use the JSON publication when SDMX lags behind it.

    The SDMX series can trail the live JSON endpoint. If the live publication
    for every leg is dated after what SDMX gave us and not after the requested
    date, it is the correct rate for that date.
    """
    try:
        live, stamps = fetch_current_rates()
    except RateFetchError:
        return None
    if not legs or any(c not in live for c in legs):
        return None
    try:
        live_date = _same_day({c: stamps[c] for c in legs})
    except RateFetchError:
        return None
    if used_date < live_date <= target_date:
        return {c: live[c] for c in legs}, live_date
    return None


def format_result(
    amount: float,
    from_currency: str,
    to_currency: str,
    result: float,
    description: str,
    rate_date: Optional[str] = None,
    is_sample: bool = False,
    published_raw: Optional[str] = None,
    requested_date: Optional[str] = None,
    is_derived: bool = False,
) -> str:
    """Format conversion result for display."""
    if is_sample:
        lines = [
            "=== Currency Conversion (DEMO) ===",
            "",
            f"  {amount:,.2f} {from_currency.upper()} = {result:,.2f} {to_currency.upper()}",
            "",
            f"  Rate: {description}",
            "  Source: ILLUSTRATIVE SAMPLE DATA, NOT the official rate.",
            "",
            "  WARNING: Sample data only. Do NOT use for tax, VAT, or any filing.",
        ]
        return "\n".join(lines)
    if rate_date is None:
        raise ValueError("rate_date is required: a shaar yatzig must carry the "
                         "date it was actually published, never today's date.")
    source = ("Derived from two Bank of Israel representative rates (not itself "
              "a published rate)" if is_derived
              else "Bank of Israel representative rate (shaar yatzig)")
    lines = [
        "=== Currency Conversion ===",
        "",
        f"  {amount:,.2f} {from_currency.upper()} = {result:,.2f} {to_currency.upper()}",
        "",
        f"  Rate: {description}",
        f"  Date: {rate_date}",
        f"  Source: {source}",
    ]
    if requested_date and requested_date != rate_date:
        lines.append(
            f"  NOTE: No publication on {requested_date}; this is the last rate "
            f"published before it ({rate_date})."
        )
    if rate_date < SHEKEL_INTRODUCED_DATE:
        lines.append(
            "  NOTE: This date precedes 1980-02-24, when the shekel replaced the "
            "Israeli pound (lira). The series expresses it in new-shekel terms, "
            "not in the lirot quoted at the time."
        )
    elif rate_date < CURRENCY_REFORM_DATE:
        lines.append(
            "  NOTE: This date precedes the 1985-09-04 currency reform (1 new "
            "shekel = 1,000 old shekels). The series expresses it in new-shekel "
            "terms, not as the old-shekel figure quoted at the time."
        )
    lines += [
        "",
        "  NOTE: Representative rate for reference. Actual bank rates may differ.",
        "  NOTE: This is the rate PUBLISHED on the date shown. If you need a rate",
        "        for a later date, it may not be published yet: the Bank of Israel",
        "        publishes once per business day and this endpoint keeps serving the",
        "        previous publication until the next one lands.",
        "  NOTE: Import VAT on GOODS uses the customs rate (this rate x 1.005,",
        "        fixed weekly from the preceding Friday's publication unless it",
        "        moves 3% or more, Customs Rules 5749-1989), published by the Tax",
        "        Authority. Intangible goods use the bank purchase rate when the",
        "        currency was bought or sent.",
    ]
    if published_raw is not None:
        warning = _precision_warning(published_raw)
        if warning:
            lines.extend(["", warning])
    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert currencies using Bank of Israel rates"
    )
    parser.add_argument("--from", dest="from_curr", help="Source currency (e.g., USD)")
    parser.add_argument("--to", dest="to_curr", help="Target currency (e.g., ILS)")
    parser.add_argument("--amount", type=float, help="Amount to convert")
    parser.add_argument("--date", type=str, help="Historical date (YYYY-MM-DD)")
    parser.add_argument("--list", action="store_true", help="List available currencies")
    parser.add_argument(
        "--demo", "--offline", dest="demo", action="store_true",
        help="Use illustrative SAMPLE rates offline (NOT official, not for tax)",
    )

    args = parser.parse_args()

    if args.list:
        print("=== Bank of Israel Published Currencies (14) ===")
        print(f"  {'Code':<6} {'Currency':<25} {'Hebrew':<20}")
        print(f"  {'-' * 51}")
        print(f"  {'ILS':<6} {'Israeli New Shekel':<25} {'shekel chadash':<20}")
        for code, (name, hebrew) in COMMON_CURRENCIES.items():
            print(f"  {code:<6} {name:<25} {hebrew:<20}")
        return

    if args.from_curr is None or args.to_curr is None or args.amount is None:
        parser.print_help()
        sys.exit(1)

    src, dst = args.from_curr.upper(), args.to_curr.upper()
    supported = set(COMMON_CURRENCIES) | {"ILS"}
    unsupported = {src, dst} - supported
    if unsupported:
        print(
            f"Error: Currency not published by the Bank of Israel: "
            f"{', '.join(sorted(unsupported))}.",
            file=sys.stderr,
        )
        print(
            "Only these 14 currencies are supported: "
            + ", ".join(COMMON_CURRENCIES) + ".",
            file=sys.stderr,
        )
        sys.exit(2)

    if src == dst:
        print(f"{args.amount:,.2f} {src} = {args.amount:,.2f} {dst} (same currency, no rate involved)")
        return

    today_il = israel_today()
    if args.date:
        try:
            requested = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: --date must be YYYY-MM-DD, got {args.date!r}.",
                  file=sys.stderr)
            sys.exit(2)
        # Normalise "2026-10-5" to "2026-10-05": every later date comparison is
        # on ISO strings, and an unpadded day sorts wrongly against them.
        args.date = requested.isoformat()
        if requested > today_il:
            print(
                f"Error: {args.date} is in the future in Israel (today there is "
                f"{today_il.isoformat()}), so no representative rate exists for "
                "it yet. Request a past date or omit --date for the latest "
                "publication. Sample rates are never a substitute.",
                file=sys.stderr,
            )
            sys.exit(2)

    legs = {src, dst} - {"ILS"}
    is_sample = False
    try:
        if args.demo:
            rates = _sample_rates()
            is_sample = True
            used_date = None
        elif args.date:
            rates, used_date = build_dated_rates(src, dst, args.date)
            if used_date is not None and used_date < args.date:
                newer = _live_if_newer(legs, used_date, args.date)
                if newer is not None:
                    rates, used_date = newer
            # Saturday and Sunday never carry a rate, so walking back is right.
            # On any other day, a missing row for TODAY may simply mean the
            # publication has not landed yet; do not call it a non-publication day.
            if (used_date is not None and used_date < args.date == today_il.isoformat()
                    and today_il.weekday() not in (5, 6)):
                raise RateFetchError(
                    f"No rate for today ({args.date}) yet; the latest publication "
                    f"found is {used_date}. Either today's rate has not been "
                    "published (soon after 15:15, or 12:15 on Fridays and holiday "
                    "eves, Israel time) or today is a non-publication day (an "
                    "Israeli holiday, Christmas Day, New Year's Day or Easter). "
                    "Re-run later, or state the date of the rate you are using."
                )
        else:
            rates, stamps = fetch_current_rates()
            missing = legs - set(rates)
            if missing:
                raise RateFetchError(
                    f"The live endpoint carried no dated rate for {', '.join(sorted(missing))}."
                )
            used_date = _same_day({c: stamps[c] for c in legs})
    except RateFetchError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "Aborting: no rate emitted, and sample rates are never substituted "
            "for a real conversion. Use --demo only for clearly-labeled "
            "illustrative output.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not is_sample and used_date is None:
        print(
            f"Error: The Bank of Israel series has no published rate on or "
            f"within 21 days before {args.date} for {src}/{dst}. The date may "
            "precede the series or the currency (for example EUR before 1999); "
            "re-running will not help.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = convert(args.amount, src, dst, rates)
    if result is None:
        print(f"Error: Could not convert {src} to {dst}.", file=sys.stderr)
        sys.exit(1)

    converted, _rate_used, description, is_derived = result
    # Judge precision on the coarsest figure the Bank actually published for a
    # leg, not on a derived cross rate (whose float carries spurious digits).
    raws = [rates[c][3] for c in legs if c in rates]
    coarsest = max(raws, key=_margin_pct) if raws else None
    print(format_result(
        args.amount, src, dst, converted, description, used_date,
        is_sample=is_sample,
        published_raw=None if is_sample else coarsest,
        requested_date=args.date,
        is_derived=is_derived,
    ))


if __name__ == "__main__":
    main()
