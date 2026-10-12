#!/usr/bin/env python3
"""Fetch Israeli economic data: BOI exchange rates, the BOI policy rate, and the CBS CPI.

Data sources:
  - Bank of Israel SDMX API (Fusion Edge Server) for exchange rates and the policy rate.
  - Central Bureau of Statistics index API for the headline Consumer Price Index.

This script never invents numbers. If a source is unreachable or returns no
observations it exits non-zero. Use --example for clearly-labelled sample output.

Usage:
    python scripts/fetch_boi_rates.py --currency USD
    python scripts/fetch_boi_rates.py --currency EUR --days 30
    python scripts/fetch_boi_rates.py --currency USD --date 2025-12-25
    python scripts/fetch_boi_rates.py --currency USD --from 2025-01-01 --to 2025-12-31 --average
    python scripts/fetch_boi_rates.py --interest
    python scripts/fetch_boi_rates.py --cpi
    python scripts/fetch_boi_rates.py --cpi --cpi-from 01-2019 --cpi-to 03-2019
    python scripts/fetch_boi_rates.py --list-currencies
    python scripts/fetch_boi_rates.py --example
"""

import re
import ssl
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

try:  # certifi carries current roots; some Python installs ship none at all
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


# BOI SDMX 2.1 REST API ("new series database" / Fusion Edge Server).
# Two data paths are live and return the same observations:
#   ws/public/sdmxapi/rest/data/{DATAFLOW}/{series}            (used here)
#   sdmx/v2/data/dataflow/BOI.STATISTICS/{DATAFLOW}/1.0/{series}
# A bare dataflow query with no date filter returns EVERY series in the
# dataflow with full history (.../data/EXR/ is ~20 MB back to 1948), so
# always name the series or bound the request with dates/lastNObservations.
BOI_API_BASE = "https://edge.boi.gov.il/FusionEdgeServer/ws/public/sdmxapi/rest/data"

# Representative exchange rates: EXR dataflow, series RER_<CUR>_ILS.
EXR_ENDPOINT = f"{BOI_API_BASE}/EXR"

# BOI policy rate (ריבית בנק ישראל): BR dataflow, daily series MNT_RIB_BOI_D.
# NOT the BIR dataflow, which is commercial-bank credit rates excluding housing.
BR_SERIES = f"{BOI_API_BASE}/BR/MNT_RIB_BOI_D"

# CBS headline CPI (מדד המחירים לצרכן - כללי), index id 120010.
# This API answers HTTP 200 even for an unknown id (with "month": null), so the
# payload must be validated rather than the status code.
# Responses are paged at 100 months, so a long range spans several pages.
# coef=true adds prevBase: the same month restated on every earlier base, via
# the CBS chaining coefficients, which is what a cross-rebase comparison needs.
CBS_CPI_URL = ("https://api.cbs.gov.il/index/data/price"
               "?id=120010&format=json&download=false&coef=true")
CBS_PAGE_SIZE = 100

# Supported currencies for exchange rates.
# מטבעות נתמכים לשערי חליפין
CURRENCIES = {
    "USD": {"name": "US Dollar", "hebrew": "דולר אמריקאי"},
    "EUR": {"name": "Euro", "hebrew": "אירו"},
    "GBP": {"name": "British Pound", "hebrew": "לירה שטרלינג"},
    "JPY": {"name": "Japanese Yen", "hebrew": "ין יפני"},
    "CHF": {"name": "Swiss Franc", "hebrew": "פרנק שוויצרי"},
    "AUD": {"name": "Australian Dollar", "hebrew": "דולר אוסטרלי"},
    "CAD": {"name": "Canadian Dollar", "hebrew": "דולר קנדי"},
    "ZAR": {"name": "South African Rand", "hebrew": "ראנד דרום אפריקאי"},
    "SEK": {"name": "Swedish Krona", "hebrew": "כתר שוודי"},
    "NOK": {"name": "Norwegian Krone", "hebrew": "כתר נורווגי"},
    "DKK": {"name": "Danish Krone", "hebrew": "כתר דני"},
    "JOD": {"name": "Jordanian Dinar", "hebrew": "דינר ירדני"},
    "EGP": {"name": "Egyptian Pound", "hebrew": "לירה מצרית"},
    "LBP": {"name": "Lebanese Pound", "hebrew": "לירה לבנונית"},
}

USER_AGENT = "Mozilla/5.0 (compatible; boi-economic-data-skill/1.x)"


def die(message: str) -> None:
    """Print an error to stderr and exit non-zero.

    A data skill must fail loudly. Returning plausible-looking placeholder
    numbers on failure is worse than returning nothing.
    """
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def progress(message: str) -> None:
    """Status lines go to stderr so that --json output stays parseable."""
    print(message, file=sys.stderr)


def fetch_url(url: str, accept: str = "application/xml",
              attempts: int = 3) -> str:
    """Fetch URL content as text, retrying transient failures.

    api.cbs.gov.il drops connections intermittently under repeated automated
    requests, returning no HTTP status at all, so a single-shot fetch turns a
    recoverable blip into a hard failure. An HTTP error status is NOT retried:
    a 404 will not become a 200.
    """
    req = Request(url)
    req.add_header("Accept", accept)
    req.add_header("User-Agent", USER_AGENT)

    host = urlparse(url).hostname
    last_reason = None
    for attempt in range(attempts):
        try:
            with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            die(f"{url} returned HTTP {exc.code}.")
        except URLError as exc:
            if isinstance(exc.reason, ssl.SSLCertVerificationError):
                # A local trust-store problem, not a server one: retrying
                # cannot fix it, and verification must never be switched off.
                die(f"TLS certificate verification failed for {host} "
                    f"({exc.reason.verify_message}). This Python has no "
                    f"usable CA bundle. Install certifi (pip install "
                    f"certifi), run 'Install Certificates.command' for a "
                    f"python.org build on macOS, or point SSL_CERT_FILE at a "
                    f"current CA bundle. Do not disable verification.")
            last_reason = exc.reason
            if attempt < attempts - 1:
                time.sleep(1 + 2 * attempt)

    hint = ""
    if host == "api.cbs.gov.il":
        hint = (" api.cbs.gov.il resets connections intermittently under "
                "repeated automated requests and usually recovers; this is "
                "not evidence that the endpoint is gone.")
    die(f"could not reach {url} after {attempts} attempts "
        f"({last_reason}).{hint}")
    return ""  # unreachable; keeps type checkers happy


def parse_sdmx(xml_data: str, url: str) -> tuple:
    """Parse an SDMX-XML response into (series_attributes, observations).

    Observations are <Obs> elements carrying TIME_PERIOD and OBS_VALUE as
    ATTRIBUTES. The server emits them as <Obs ...></Obs> (not self-closing),
    so match on the element name, never on the raw text shape.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        die(f"{url} did not return parseable XML (a bot-protection or error "
            f"page is the usual cause).")

    attrs, observations = {}, []
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag == "Series" and not attrs:
            attrs = dict(element.attrib)
        elif tag == "Obs":
            date, value = element.get("TIME_PERIOD"), element.get("OBS_VALUE")
            if date and value:
                try:
                    observations.append({"date": date, "value": float(value)})
                except ValueError:
                    continue

    if not observations:
        die(f"{url} returned no observations. The usual cause is a date "
            f"range that covers only non-publication days; try "
            f"lastNObservations=1 instead.")

    observations.sort(key=lambda o: o["date"], reverse=True)
    return attrs, observations


def _validated(currency: str) -> str:
    """Upper-case a currency code and reject anything not in the allowlist."""
    currency = currency.upper()
    if currency not in CURRENCIES:
        die(f"unsupported currency {currency}. "
            f"Supported: {', '.join(CURRENCIES)}")
    return currency


def fetch_exchange_rate(currency: str, days: int, start: str = None,
                        end: str = None) -> tuple:
    """Fetch representative exchange rates for a currency from the BOI API.

    Either the last `days` days, or an explicit start/end (YYYY-MM-DD).
    """
    currency = _validated(currency)

    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()
    end_date = end_dt.strftime("%Y-%m-%d")
    # Without --from, the window is the --days days ending at --to (or today).
    start_date = start or (end_dt - timedelta(days=days)).strftime("%Y-%m-%d")
    url = (f"{EXR_ENDPOINT}/RER_{currency}_ILS"
           f"?startPeriod={start_date}&endPeriod={end_date}")

    progress(f"Fetching {currency} representative rate from the Bank of Israel...")
    return parse_sdmx(fetch_url(url), url)


def fetch_rate_on_or_before(currency: str, date: str) -> tuple:
    """Fetch the last rate published on or before `date` (YYYY-MM-DD).

    This is the fallback most rules name for a day with no publication
    (weekend, holiday, Christmas, or a day the BOI simply did not publish):
    endPeriod bounds the search, lastNObservations=1 takes the last one.
    """
    currency = _validated(currency)
    url = (f"{EXR_ENDPOINT}/RER_{currency}_ILS"
           f"?endPeriod={date}&lastNObservations=1")
    progress(f"Fetching the {currency} representative rate published on or "
             f"before {date}...")
    return parse_sdmx(fetch_url(url), url)


def fetch_latest_exchange_rate(currency: str) -> tuple:
    """Fetch only the most recently published rate, ignoring calendar gaps.

    lastNObservations is the correct primitive here. Do NOT use lastNPeriods:
    the BOI server accepts it, returns HTTP 200, and silently ignores it,
    handing back the entire series back to 1948.
    """
    currency = _validated(currency)
    url = f"{EXR_ENDPOINT}/RER_{currency}_ILS?lastNObservations=1"
    return parse_sdmx(fetch_url(url), url)


def fetch_interest_rate(days: int) -> tuple:
    """Fetch the Bank of Israel policy rate (ריבית בנק ישראל) from BR."""
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"{BR_SERIES}?startPeriod={start_date}"
    progress("Fetching the Bank of Israel policy rate...")
    return parse_sdmx(fetch_url(url), url)


def fetch_cpi(last: int = None, start: str = None, end: str = None) -> list:
    """Fetch the headline CBS Consumer Price Index (מדד המחירים לצרכן - כללי).

    Either the `last` N months, or a startPeriod/endPeriod range in mm-yyyy.
    The API pages its answer (page / pagesize, default 100 months per page),
    so every page is read; stopping at page 1 would silently drop the oldest
    months, which is exactly where a contract's base month is.
    """
    query = CBS_CPI_URL
    if start or end:
        if start:
            query += f"&startPeriod={start}"
        if end:
            query += f"&endPeriod={end}"
    else:
        query += f"&last={last}"
    progress("Fetching the CBS Consumer Price Index...")

    entries, page, expected = [], 1, None
    while True:
        url = f"{query}&Page={page}&PageSize={CBS_PAGE_SIZE}"
        raw = fetch_url(url, accept="application/json")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            die(f"{url} did not return JSON. This API answers HTTP 200 with "
                f"an HTML error page for an undefined path.")

        months = payload.get("month")
        if not months or not months[0].get("date"):
            if entries:
                break
            die(f"{url} returned no CPI observations. This API answers HTTP "
                f"200 with \"month\": null for an unknown index id, and "
                f"omits a month the CBS has not published yet, so the "
                f"payload must be validated rather than the status code.")
        entries.extend(months[0]["date"])

        paging = payload.get("paging") or {}
        if expected is None:
            expected = paging.get("total_items")
        if page >= int(paging.get("last_page") or 1):
            break
        page += 1
        time.sleep(1)  # the server resets bursts of requests

    seen, rows = set(), []
    for entry in entries:
        key = (entry.get("year"), entry.get("month"))
        if key in seen:
            continue
        seen.add(key)
        base = entry.get("currBase") or {}
        by_base = {base.get("baseDesc"): base.get("value")}
        for prev in entry.get("prevBase") or []:
            by_base.setdefault(prev.get("baseDesc"), prev.get("value"))
        rows.append({
            "year": entry.get("year"),
            "month": entry.get("month"),
            "index": base.get("value"),
            "base": base.get("baseDesc"),
            "monthly_pct": entry.get("percent"),
            "yearly_pct": entry.get("percentYear"),
            "_by_base": by_base,
        })
    rows.sort(key=lambda r: (r["year"], r["month"]), reverse=True)

    # Each month is published on the base that was current at the time, so a
    # range that crosses a rebase mixes bases (2019 is on "2018 ממוצע", 2026
    # on "2024 ממוצע"). Dividing those raw values is wrong. Restate every row
    # on the OLDEST row's base, which every later month carries in prevBase.
    common = rows[-1]["base"]
    for row in rows:
        value = row.pop("_by_base").get(common)
        row["index_on_common_base"] = (round(value, 4)
                                       if value is not None else None)
        row["common_base"] = common

    # A month published between two page requests shifts a sliding window
    # (last=N) by one, and the oldest month silently falls off the end.
    complete = expected is None or len(rows) >= int(expected)
    if not complete:
        progress(f"WARNING: the CBS reported {expected} months but "
                 f"{len(rows)} arrived (likely a release between page "
                 f"requests). Re-run before relying on the oldest month.")
    return rows, complete


def cpi_summary(rows: list, complete: bool, requested_end: str) -> dict:
    """Facts a reader must not lose, kept with the data in --json output."""
    newest = (rows[0]["year"], rows[0]["month"])
    tail_unpublished = False
    if requested_end:
        wanted = (int(requested_end[3:]), int(requested_end[:2]))
        tail_unpublished = newest < wanted
    return {
        "common_base": rows[0]["common_base"],
        "bases": sorted({row["base"] for row in rows}),
        "newest_returned": f"{newest[0]}-{newest[1]:02d}",
        "requested_end": requested_end,
        "tail_unpublished": tail_unpublished,
        "complete": complete,
        "unrestated_months": [f"{r['year']}-{r['month']:02d}" for r in rows
                              if r["index_on_common_base"] is None],
        "rows": rows,
    }


def unit_label(attrs: dict) -> tuple:
    """Derive the quotation unit from the API's own UNIT_MULT attribute.

    UNIT_MULT is the power of ten the rate is quoted per: 0 means per 1 unit,
    2 means per 100 (the Japanese yen). Reading it beats a hardcoded table,
    which silently diverges if the BOI changes a quotation basis.
    """
    try:
        unit = 10 ** int(attrs.get("UNIT_MULT", 0))
    except (TypeError, ValueError):
        unit = 1
    return unit, (f" per {unit}" if unit > 1 else "")


def average(observations: list) -> float:
    """Simple mean of the published business-day rates in the window.

    Days with no publication are NOT filled in; there is no BOI annual or
    monthly average series for individual currencies.
    """
    return sum(o["value"] for o in observations) / len(observations)


def print_rates(currency: str, attrs: dict, observations: list,
                show_all: bool = False, want_average: bool = False,
                label: str = "Latest") -> None:
    """Print exchange rates in a formatted table."""
    info = CURRENCIES.get(currency, {})
    unit, suffix = unit_label(attrs)

    print(f"  {info.get('name', currency)} ({info.get('hebrew', '')}){suffix}")
    print(f"  {'Date':<12} {'Rate (NIS)':<12}")
    print(f"  {'-' * 12} {'-' * 12}")
    shown = observations if show_all else observations[:10]
    for obs in shown:
        print(f"  {obs['date']:<12} {obs['value']:<12.4f}")
    if len(observations) > len(shown):
        print(f"  ... {len(observations) - len(shown)} older rows not shown "
              f"(use --from/--to to print a whole range, or --json)")
    if want_average:
        print(f"\n  Simple mean of {len(observations)} published rates "
              f"({observations[-1]['date']} to {observations[0]['date']}): "
              f"{average(observations):.4f} NIS per {unit} {currency}")

    latest = observations[0]
    print(f"\n  {label} ({latest['date']}): "
          f"{unit} {currency} = {latest['value']} NIS")
    if unit == 1:
        print(f"  Inverse: {1 / latest['value']:.4f} {currency} per shekel")


def print_interest(observations: list) -> None:
    """Print the current policy rate and the dates it changed."""
    latest = observations[0]
    print(f"  Bank of Israel policy rate (ריבית בנק ישראל)")
    print(f"  Current: {latest['value']}% (as published for {latest['date']})")
    print()
    print("  Recent changes (effective dates; each decision is announced a")
    print("  few days earlier):")
    ordered = list(reversed(observations))
    previous = None
    for obs in ordered:
        if previous is not None and obs["value"] != previous:
            print(f"    {obs['date']}  {previous}% -> {obs['value']}%")
        previous = obs["value"]
    if previous == ordered[0]["value"]:
        print(f"    no change in the fetched window "
              f"(from {ordered[0]['date']})")


def print_cpi(summary: dict) -> None:
    """Print CPI readings, flagging a range that crosses a rebase."""
    rows = summary["rows"]
    bases = summary["bases"]
    common = summary["common_base"]
    print(f"  Consumer Price Index (מדד המחירים לצרכן - כללי)")
    print()
    print(f"  {'Month':<9} {'Index':<9} {'Published base':<16} "
          f"{'On ' + common:<16} {'Monthly %':<10} {'Yearly %':<8}")
    print(f"  {'-' * 9} {'-' * 9} {'-' * 16} {'-' * 16} {'-' * 10} {'-' * 8}")
    for row in rows:
        month = f"{row['year']}-{row['month']:02d}"
        print(f"  {month:<9} {str(row['index']):<9} {row['base']:<16} "
              f"{str(row['index_on_common_base']):<16} "
              f"{str(row['monthly_pct']):<10} {str(row['yearly_pct']):<8}")
    print()
    if summary["unrestated_months"]:
        print(f"  WARNING: {', '.join(summary['unrestated_months'])} could "
              f"not be restated on {common} (no chaining coefficient in the "
              f"response). Do not compare those rows across a rebase.")
    if len(bases) > 1:
        print(f"  WARNING: this range spans {len(bases)} bases "
              f"({', '.join(bases)}). Do not divide values from the Index "
              f"column across a rebase; use the \"On {common}\" column, "
              f"which restates every month on one base with the CBS chaining "
              f"coefficients.")
    else:
        print(f"  All months are on one base ({common}); the two index "
              f"columns agree.")
    if summary["tail_unpublished"]:
        print(f"  NOTE: the newest month returned is "
              f"{summary['newest_returned']}. Later months in the requested "
              f"range are not published yet (the CBS releases each month's "
              f"index around the 15th of the next month).")


def print_example() -> None:
    """Print clearly-labelled sample output (no network access)."""
    print("=== EXAMPLE OUTPUT -- SAMPLE VALUES, NOT LIVE DATA ===")
    print()
    print("  US Dollar (דולר אמריקאי)")
    print(f"  {'Date':<12} {'Rate (NIS)':<12}")
    print(f"  {'-' * 12} {'-' * 12}")
    for date, rate in (("2026-08-26", 2.9720), ("2026-08-25", 2.9860),
                       ("2026-08-24", 2.9940), ("2026-08-21", 2.9910)):
        print(f"  {date:<12} {rate:<12.4f}")
    print()
    print("  Note the gap over Saturday and Sunday: the representative rate is")
    print("  published Monday to Friday only.")
    print()
    print("Run without --example for live data.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch Israeli economic data "
                    "(שליפת נתונים כלכליים מבנק ישראל ומהלמ\"ס)"
    )
    parser.add_argument("--currency",
                        help=f"Currency code for the representative exchange "
                             f"rate ({', '.join(list(CURRENCIES)[:6])}...)")
    parser.add_argument("--days", type=int, default=7,
                        help="Days of rate history (default: 7)")
    parser.add_argument("--date", metavar="YYYY-MM-DD",
                        help="With --currency, the rate published on that "
                             "date, or the last one published before it")
    parser.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD",
                        help="With --currency, first day of an explicit "
                             "range (prints every row)")
    parser.add_argument("--to", dest="date_to", metavar="YYYY-MM-DD",
                        help="With --currency, last day of an explicit range "
                             "(default: today)")
    parser.add_argument("--average", action="store_true",
                        help="With --currency, also print the simple mean of "
                             "the published rates in the window")
    parser.add_argument("--latest", action="store_true",
                        help="With --currency, fetch only the most recently "
                             "published rate (skips weekend/holiday gaps)")
    parser.add_argument("--interest", action="store_true",
                        help="Fetch the BOI policy rate (ריבית בנק ישראל)")
    parser.add_argument("--interest-days", type=int, default=400,
                        help="Days of policy-rate history to scan for change "
                             "points (default: 400)")
    parser.add_argument("--cpi", action="store_true",
                        help="Fetch the CBS Consumer Price Index (מדד המחירים)")
    parser.add_argument("--cpi-last", type=int, default=6,
                        help="Months of CPI history to fetch (default: 6). "
                             "Raise it to reach the base month a contract "
                             "names; a 2019 lease needs roughly 90")
    parser.add_argument("--cpi-from", metavar="MM-YYYY",
                        help="With --cpi, first month of an explicit range "
                             "(e.g. 01-2019). Overrides --cpi-last")
    parser.add_argument("--cpi-to", metavar="MM-YYYY",
                        help="With --cpi, last month of the range. Without "
                             "--cpi-from, the range is the --cpi-last months "
                             "ending here")
    parser.add_argument("--list-currencies", action="store_true",
                        help="List all supported currencies")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true",
                        help="Show clearly-labelled sample output")

    args = parser.parse_args()

    if args.days < 0 or args.interest_days < 1 or args.cpi_last < 1:
        die("--days must be 0 or more, and --interest-days and --cpi-last "
            "must be 1 or more.")
    for value in (args.cpi_from, args.cpi_to):
        if value and not re.fullmatch(r"(0[1-9]|1[0-2])-(19|20)\d\d", value):
            die(f"{value} is not a month in MM-YYYY form (e.g. 01-2019).")
    if args.cpi_from and args.cpi_to:
        def ym(v):
            return (int(v[3:]), int(v[:2]))
        if ym(args.cpi_from) > ym(args.cpi_to):
            die("--cpi-from is later than --cpi-to.")
    if (args.cpi_from or args.cpi_to) and not args.cpi:
        die("--cpi-from and --cpi-to need --cpi.")
    for value in (args.date, args.date_from, args.date_to):
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                die(f"{value} is not a date in YYYY-MM-DD form.")
    if (args.date or args.date_from or args.date_to or args.average
            or args.latest) and not args.currency:
        die("--date, --from, --to, --average and --latest need --currency.")
    if args.date and (args.date_from or args.date_to or args.latest):
        die("--date cannot be combined with --from, --to or --latest.")
    if args.latest and (args.date_from or args.date_to):
        die("--latest cannot be combined with --from or --to.")
    if args.date_from and args.date_to and args.date_from > args.date_to:
        die("--from is later than --to.")

    if not any([args.currency, args.interest, args.cpi,
                args.list_currencies, args.example]):
        parser.print_help()
        sys.exit(1)

    if args.list_currencies:
        print("Supported currencies (מטבעות נתמכים):")
        print(f"  {'Code':<6} {'Name':<25} {'Hebrew':<20}")
        print(f"  {'-' * 6} {'-' * 25} {'-' * 20}")
        for code, info in CURRENCIES.items():
            print(f"  {code:<6} {info['name']:<25} {info['hebrew']:<20}")
        return

    if args.example:
        print_example()
        return

    if args.currency:
        if args.date:
            attrs, observations = fetch_rate_on_or_before(args.currency,
                                                          args.date)
        elif args.latest:
            attrs, observations = fetch_latest_exchange_rate(args.currency)
        else:
            attrs, observations = fetch_exchange_rate(
                args.currency, args.days, args.date_from, args.date_to)
        if args.json:
            unit, _ = unit_label(attrs)
            payload = {
                "currency": args.currency.upper(),
                "quoted_per": unit,
                "unit_measure": attrs.get("UNIT_MEASURE"),
                "data_type": attrs.get("DATA_TYPE"),
                "series_code": attrs.get("SERIES_CODE"),
                "observations": observations,
            }
            if args.date:
                payload["requested_date"] = args.date
            if args.average:
                payload["simple_mean"] = round(average(observations), 6)
                payload["observation_count"] = len(observations)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            if args.date and observations[0]["date"] != args.date:
                later = args.date > datetime.now().strftime("%Y-%m-%d")
                print(f"  No rate was published on {args.date}"
                      f"{' (a future date)' if later else ''}; showing the "
                      f"last one published before it.")
            print_rates(args.currency.upper(), attrs, observations,
                        show_all=bool(args.date_from), want_average=args.average,
                        label="Rate used" if args.date else "Latest")

    if args.interest:
        _, observations = fetch_interest_rate(args.interest_days)
        if args.json:
            print(json.dumps(observations, indent=2, ensure_ascii=False))
        else:
            print_interest(observations)

    if args.cpi:
        cpi_from = args.cpi_from
        if args.cpi_to and not cpi_from:
            # --cpi-to alone would otherwise fetch every month since 1951.
            year, month = int(args.cpi_to[3:]), int(args.cpi_to[:2])
            index = year * 12 + month - 1 - (args.cpi_last - 1)
            cpi_from = f"{index % 12 + 1:02d}-{index // 12}"
        rows, complete = fetch_cpi(args.cpi_last, cpi_from, args.cpi_to)
        summary = cpi_summary(rows, complete, args.cpi_to)
        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print_cpi(summary)


if __name__ == "__main__":
    main()
