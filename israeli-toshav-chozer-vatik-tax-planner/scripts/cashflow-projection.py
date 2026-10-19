#!/usr/bin/env python3
"""
cashflow-projection.py

Plain-text cash-flow projector for an Israeli returning resident, classifying
income streams as EXEMPT vs. TAXABLE, tax year by tax year, under three tracks:

  - vatik       (10 years foreign-resident, section 14 full exemption)
  - regular     (6-10 years foreign-resident, 5-year passive + 10-year capital gains)
  - none        (no track, regular Israeli taxation from day 1)

An oleh chadash uses the vatik track: section 14(a) gives a first-time resident
the same 10-year foreign-income exemption, and Hok Iddud covers both.

CRITICAL DISCLAIMER
-------------------
This script does NOT compute tax owed (no NIS amount, no marginal rate).
It classifies gross income as exempt vs. taxable. It is a planning aid,
not tax advice. A CPA must review your specific case before any filing.

Usage:
  python3 cashflow-projection.py                       # interactive prompts
  python3 cashflow-projection.py --json input.json     # batch mode

Rows are TAX YEARS (calendar years). Year 1 is the tax year in which you became
resident (usually a partial year), so the 10-year window ends inside Year 11.
Enter each stream's amount as what it earns in that tax year. In Year 1, count only
what is earned FROM the residency date: income earned earlier, while you were a
foreign resident, is outside Israeli tax on foreign income and outside Hok Iddud,
so leave it out rather than letting it be labelled TAXABLE or IL-LABOUR.

JSON shape:
{
  "track": "vatik" | "regular" | "none",
  "residency_start": "YYYY-MM-DD",       # the date your center of life actually
                                          # moved to Israel; ignore any
                                          # acclimation-year election
  "us_person": true | false,             # holds US citizenship or a green card
  "us_status": "citizen" | "green-card", # optional, defaults to citizen
  "income_streams": [
    {
      "label": "Freelance design work",
      "source": "foreign" | "israeli",    # for active income: where the WORK is
                                          # performed (Section 4A), not where the
                                          # client or payer is
      "kind":   "active" | "passive" | "capital-gain",
      "annual_amount": 250000,            # in whatever currency, no conversion done
      "currency": "USD",
      "asset_acquired_before_return": true,   # for regular track only
      "acquired_by_gift": false,          # capital gains: asset received as a
                                          # tax-exempt gift under s.97(a)(5)
      "years_active": [1,2,3,4,5,6,7,8,9,10,11]  # tax-year indices, 1 = residency year
    }
  ]
}
"""
import argparse
import json
import sys
from datetime import date, datetime
from typing import List, Dict, Optional

DISCLAIMER = (
    "PLANNING AID, NOT TAX ADVICE. This output classifies each income stream as exempt "
    "vs. taxable under section 14 of the Income Tax Ordinance. It does NOT compute the "
    "shekel amount of tax owed. A CPA must review before any filing. From 1.1.2026, "
    "vatikim must REPORT foreign income to Mas Hachnasa even though it remains exempt."
)

MAX_YEARS = 11
HOK_IDDUD_WINDOW = (date(2025, 11, 5), date(2026, 12, 31))
# Hok Iddud s.2(a) annual caps on Israeli personal-exertion income (NIS).
HOK_IDDUD_CAPS = {2026: 600_000, 2027: 1_000_000, 2028: 1_000_000, 2029: 350_000, 2030: 150_000}


def add_years(d: date, n: int) -> date:
    """Exclusive end of an n-year period starting on d. A period starting on
    29 February runs through 28 February n years later, so it ends (exclusive)
    on 1 March."""
    try:
        return d.replace(year=d.year + n)
    except ValueError:  # 29 February in a non-leap target year
        return date(d.year + n, 3, 1)


def hok_iddud_eligible(track: str, residency_start: date) -> bool:
    """Hok Iddud covers an oleh or a toshav chozer vatik who became resident in
    the window. A regular toshav chozer, or anyone resident outside the window,
    gets nothing under it, so their Israeli labour is plainly TAXABLE."""
    return track == "vatik" and HOK_IDDUD_WINDOW[0] <= residency_start <= HOK_IDDUD_WINDOW[1]


def hok_iddud_cap(tax_year: int, residency_start: date) -> Optional[int]:
    """Annual cap for a tax year. s.2(d) pro-rates 2026 to the residency period;
    Circular 07/2026 counts days from becoming resident to the end of the year,
    over 365 (its example: 1 July -> 183/365). A 1 January start is resident for
    the whole year and gets the full cap."""
    cap = HOK_IDDUD_CAPS.get(tax_year)
    if cap is None:
        return None
    if tax_year == 2026 and residency_start.year == 2026:
        if residency_start == date(2026, 1, 1):
            return cap
        days = max(1, (date(2026, 12, 31) - residency_start).days)
        return round(cap * days / 365)
    return cap


def window_verdict(tax_year: int, end: date) -> str:
    """EXEMPT for a tax year wholly inside a window ending on `end` (exclusive),
    PART-EX for the tax year in which it ends, TAXABLE after."""
    if tax_year < end.year:
        return "EXEMPT"
    if tax_year == end.year and end > date(tax_year, 1, 1):
        return "PART-EX"
    return "TAXABLE"


def gain_verdict(tax_year: int, end: date) -> str:
    """A capital gain on a qualifying asset sold in or after the year the window
    ends is not fully taxable: s.97(b)(3) keeps the slice of the real gain accrued
    up to the end of the window exempt, apportioned linearly over the holding
    period. So there is no cliff, only a shrinking exempt share."""
    v = window_verdict(tax_year, end)
    return "EXEMPT" if v == "EXEMPT" else "LINEAR-EX"


def classify_stream(track: str, source: str, kind: str, tax_year: int,
                    residency_start: date, asset_acquired_before_return: bool,
                    iddud_cap: Optional[int] = None,
                    acquired_by_gift: bool = False) -> str:
    """Return EXEMPT, PART-EX, TAXABLE or IL-LABOUR for one stream in one tax year."""
    # Israeli-source income is outside section 14 under every track. Israeli
    # personal-exertion income may still be exempt under Hok Iddud, but only for
    # an eligible vatik/oleh and only in a cap year.
    if source == "israeli":
        if kind == "active" and iddud_cap is not None:
            return "IL-LABOUR"
        return "TAXABLE"

    if track == "none":
        return "TAXABLE"

    end10 = add_years(residency_start, 10)
    if track == "vatik":
        # s.97(b)(1) excludes an asset received under the s.97(a)(5) exempt-gift
        # route, so a gifted foreign asset does not get the 10-year gain exemption.
        if kind == "capital-gain" and acquired_by_gift:
            return "GIFT-TAX"
        if kind == "capital-gain":
            return gain_verdict(tax_year, end10)
        return window_verdict(tax_year, end10)

    if track == "regular":
        # 5 years on passive, 10 years on capital gains, NEVER on active, and only
        # for an asset acquired during the period abroad.
        if kind == "active" or not asset_acquired_before_return:
            return "TAXABLE"
        if kind == "passive":
            return window_verdict(tax_year, add_years(residency_start, 5))
        if kind == "capital-gain":
            return gain_verdict(tax_year, end10)
        return "TAXABLE"

    return "TAXABLE"


VALID_TRACKS = ("vatik", "regular", "none")
VALID_SOURCES = ("foreign", "israeli")
VALID_KINDS = ("active", "passive", "capital-gain")
VALID_US_STATUS = ("citizen", "green-card")


class PlanError(Exception):
    """A problem with the input plan that the user must fix."""


def validate(plan: Dict) -> None:
    """Fail loudly on a malformed plan.

    A silently-wrong track is the worst failure mode this script has: an
    unrecognised value used to fall through to 'TAXABLE' for every stream,
    producing a confident all-taxable projection with no warning. Since the
    whole point of the script is to distinguish the tracks, that is a wrong
    answer dressed as an answer.
    """
    if not isinstance(plan, dict):
        raise PlanError("Input must be a JSON object.")
    track = plan.get("track")
    if track not in VALID_TRACKS:
        raise PlanError(
            f"track must be one of {VALID_TRACKS}, got {track!r}. "
            "Refusing to guess: an unrecognised track would silently classify "
            "every stream as taxable."
        )
    rstart = plan.get("residency_start")
    if not rstart:
        raise PlanError("residency_start is required (YYYY-MM-DD).")
    try:
        datetime.fromisoformat(str(rstart)).date()
    except Exception:
        raise PlanError(
            f"residency_start {rstart!r} is not a valid YYYY-MM-DD date. "
            "This date selects the Amendment 272 reporting regime, so it "
            "cannot be skipped."
        )
    us_status = plan.get("us_status")
    if us_status is not None and us_status not in VALID_US_STATUS:
        raise PlanError(f"us_status must be one of {VALID_US_STATUS}, got {us_status!r}.")
    streams = plan.get("income_streams")
    if not isinstance(streams, list) or not streams:
        raise PlanError("income_streams must be a non-empty list.")
    for i, s in enumerate(streams, 1):
        where = f"income_streams[{i}] ({s.get('label', 'unlabelled')})"
        for field in ("label", "source", "kind", "annual_amount"):
            if field not in s:
                raise PlanError(f"{where}: missing required field {field!r}.")
        if s["source"] not in VALID_SOURCES:
            raise PlanError(f"{where}: source must be one of {VALID_SOURCES}, got {s['source']!r}.")
        if s["kind"] not in VALID_KINDS:
            raise PlanError(f"{where}: kind must be one of {VALID_KINDS}, got {s['kind']!r}.")
        years = s.get("years_active")
        if not isinstance(years, list) or not years:
            raise PlanError(f"{where}: years_active must be a non-empty list of tax-year indices 1-{MAX_YEARS}.")
        for y in years:
            if not isinstance(y, int) or not 1 <= y <= MAX_YEARS:
                raise PlanError(f"{where}: years_active entries must be integers 1-{MAX_YEARS}, got {y!r}.")
        if plan["track"] == "regular" and s["kind"] in ("passive", "capital-gain") \
                and s["source"] == "foreign" and "asset_acquired_before_return" not in s:
            raise PlanError(
                f"{where}: on the regular track, asset_acquired_before_return decides "
                "whether this stream is exempt at all. State it explicitly rather than "
                "letting it default to false."
            )


def render(plan: Dict) -> str:
    track = plan["track"]
    residency_start = plan["residency_start"]
    streams = plan["income_streams"]
    us_person = plan.get("us_person", False) or plan.get("us_status") is not None
    us_status = plan.get("us_status") or ("citizen" if us_person else None)
    rdate = datetime.fromisoformat(residency_start).date()
    end10 = add_years(rdate, 10)
    iddud = hok_iddud_eligible(track, rdate)

    lines = []
    lines.append("=" * 72)
    lines.append("ISRAELI RETURNING-RESIDENT CASH-FLOW PROJECTION")
    lines.append("=" * 72)
    lines.append(f"Track: {track}")
    lines.append(f"Israeli tax-residency start date: {residency_start}")
    lines.append(f"US person: {us_status or 'no'}")
    lines.append(f"Streams: {len(streams)}")
    lines.append("")
    lines.append("DISCLAIMER: " + DISCLAIMER)
    lines.append("")
    lines.append("Rows are tax years. Year 1 is the tax year you became resident.")
    if track == "vatik":
        lines.append(f"The 10-year section 14 window ends on {end10.isoformat()} (that day not included).")
    elif track == "regular":
        end5 = add_years(rdate, 5)
        lines.append(f"Regular track: passive income window ends {end5.isoformat()}, capital-gains window")
        lines.append(f"ends {end10.isoformat()} (each day not included).")
    lines.append("Year 1: enter only income earned from the residency date on.")
    lines.append("The residency date must be when your center of life actually moved;")
    lines.append("an acclimation-year election does not change it for Hok Iddud.")
    lines.append("For active income, 'source' must be WHERE THE WORK IS DONE (Section 4A):")
    lines.append("work done in Israel for a foreign client or employer is israeli, not foreign.")
    lines.append("")
    lines.append("VERDICTS: EXEMPT / TAXABLE are section 14 classifications of FOREIGN income.")
    if track != "none":
        lines.append("PART-EX: the window ends inside that tax year; income up to the end date is")
        lines.append("exempt and income after it is taxable.")
        lines.append("LINEAR-EX: a capital gain on a qualifying asset sold in or after the year the")
        lines.append("window ends. Under s.97(b)(3) the share of the real gain accrued up to the")
        lines.append("end date stays exempt, apportioned linearly by holding period; only the rest")
        lines.append("is taxed. There is no cliff at year 10, so do not rush a sale.")
    if iddud:
        lines.append("IL-LABOUR marks Israeli personal-exertion income (salary or business) that")
        lines.append("section 14 never exempts but Hok Iddud MAY exempt up to the cap printed for")
        lines.append("that tax year, if you meet its conditions; the assessing officer decides in")
        lines.append("the annual return. Conditions: the Misrad HaKlitah certificate (vatik) or")
        lines.append("oleh status; the exemption is voided if you leave in 2028 or 2029 with fewer")
        lines.append("than 75 days in Israel. Not covered: income attributed from a transparent")
        lines.append("entity in which you are a substantial shareholder. Lower limits: income")
        lines.append("from a relative (140,000 NIS a year in 2026-2029, pro-rated in 2026; a")
        lines.append("company you hold 25%+ of but do not wholly own is a relative), and in-year")
        lines.append("relief through Form 116ע capped at 300,000 / 500,000 NIS. See Step 5.")
    else:
        lines.append("Israeli salary and business income are TAXABLE here: Hok Iddud applies only")
        lines.append("to an oleh or a toshav chozer vatik who became resident between 5.11.2025")
        lines.append("and 31.12.2026, and this plan is outside that (track or residency date).")
    gift_unknown = [s["label"] for s in streams if track == "vatik" and s["source"] == "foreign"
                    and s["kind"] == "capital-gain" and "acquired_by_gift" not in s]
    if gift_unknown:
        lines.append("GIFT CHECK: a foreign asset received as a tax-exempt gift (s.97(a)(5)) is")
        lines.append("excluded from the vatik capital-gains exemption. These streams do not say")
        lines.append("whether they were gifts, so their EXEMPT rows assume they were not:")
        lines.append("  " + ", ".join(gift_unknown) + "  (set acquired_by_gift)")
    if any(s.get("acquired_by_gift") for s in streams):
        lines.append("GIFT-TAX: a gifted foreign asset on the vatik track; its gain is outside the")
        lines.append("s.97(b)(1) exemption. Have a CPA confirm.")
    lines.append("")

    for year_idx in range(1, MAX_YEARS + 1):
        tax_year = rdate.year + year_idx - 1
        cap = hok_iddud_cap(tax_year, rdate) if iddud else None
        header = f"--- Year {year_idx} (tax year {tax_year}) ---"
        if cap is not None:
            header += f"  Hok Iddud cap: {cap:,} NIS"
        lines.append(header)
        exempt_total, taxable_total, il_labour_total, part_total = {}, {}, {}, {}
        for s in streams:
            if year_idx not in s.get("years_active", []):
                continue
            verdict = classify_stream(
                track=track,
                source=s["source"],
                kind=s["kind"],
                tax_year=tax_year,
                residency_start=rdate,
                asset_acquired_before_return=s.get("asset_acquired_before_return", False),
                iddud_cap=cap,
                acquired_by_gift=bool(s.get("acquired_by_gift", False)),
            )
            currency = s.get("currency", "?")
            amount = s["annual_amount"]
            bucket = {"EXEMPT": exempt_total, "IL-LABOUR": il_labour_total,
                      "PART-EX": part_total, "LINEAR-EX": part_total}.get(verdict, taxable_total)
            bucket[currency] = bucket.get(currency, 0) + amount
            lines.append(f"  [{verdict:9}] {s['label']}: {amount:,} {currency}  ({s['source']}/{s['kind']})")
        if exempt_total or taxable_total or il_labour_total or part_total:
            lines.append("  TOTAL EXEMPT (foreign, s.14):  " + (", ".join(f"{v:,} {k}" for k, v in exempt_total.items()) or "none"))
            if part_total:
                lines.append("  PARTLY EXEMPT (PART-EX / LINEAR-EX): " + ", ".join(f"{v:,} {k}" for k, v in part_total.items()))
            lines.append("  TOTAL TAXABLE:                " + (", ".join(f"{v:,} {k}" for k, v in taxable_total.items()) or "none"))
            if il_labour_total:
                lines.append("  ISRAELI LABOUR (check Hok Iddud cap): " + ", ".join(f"{v:,} {k}" for k, v in il_labour_total.items()))
        else:
            lines.append("  (no streams active this year)")
        lines.append("")

    if rdate >= date(2026, 1, 1):
        lines.append("REPORTING NOTE: Your residency start is on/after 1.1.2026.")
        lines.append("Amendment 272 applies: foreign income above is EXEMPT but must be")
        lines.append("REPORTED annually on Form 1301 + Schedule D-1. Capital declarations")
        lines.append("(hatzharat hon) on Tax Authority request. Trust + CFC disclosures may apply.")
    else:
        lines.append("REPORTING NOTE: Your residency start is before 1.1.2026.")
        lines.append("Legacy regime: foreign income above is EXEMPT and NOT reportable for")
        lines.append("the remainder of your 10-year window. Verify the residency-start date")
        lines.append("with a CPA before relying on this position.")
    lines.append("")
    if us_status == "citizen":
        lines.append("US-PERSON WARNING: You hold US citizenship.")
        lines.append("The Israeli section 14 exemption above does NOT relieve US tax.")
        lines.append("The US-Israel treaty saving clause (Article 6(3)) lets the US tax")
        lines.append("its citizens as if the treaty did not exist. No foreign tax credit")
        lines.append("offsets the US bill because no Israeli tax was paid on exempt income.")
        lines.append("There is no US-Israel totalization agreement, so self-employment")
        lines.append("income can bear both Bituach Leumi and US self-employment tax.")
        lines.append("Route every 'EXEMPT' line above through a US-Israel cross-border CPA.")
        lines.append("")
    elif us_status == "green-card":
        lines.append("GREEN-CARD WARNING: US worldwide taxation continues until the green card")
        lines.append("is formally abandoned (Form I-407) or you take an Israeli treaty-residence")
        lines.append("position and notify the IRS. With permanent residence in at least 8 of")
        lines.append("the last 15 tax years you are a long-term resident, and ending that status")
        lines.append("is an expatriation under IRC 877A (Form 8854, possible exit tax). Decide")
        lines.append("with a US-Israel cross-border CPA before doing either.")
        lines.append("")
    lines.append("=" * 72)
    lines.append(DISCLAIMER)
    lines.append("=" * 72)
    return "\n".join(lines)


def interactive() -> Dict:
    print("Interactive mode. Press Ctrl+C to exit.\n")
    track = input("Track [vatik/regular/none]: ").strip().lower()
    if track not in ("vatik", "regular", "none"):
        print(f"Unknown track: {track}", file=sys.stderr)
        sys.exit(1)
    residency_start = input("Date your center of life moved to Israel (YYYY-MM-DD): ").strip()
    us = input("US status [none/citizen/green-card]: ").strip().lower()
    n = int(input("How many income streams? ").strip())
    streams = []
    for i in range(n):
        print(f"\nStream #{i+1}")
        label = input("  Label: ").strip()
        source = input("  Source [foreign/israeli] (active income: where the work is done): ").strip().lower()
        kind = input("  Kind [active/passive/capital-gain]: ").strip().lower()
        amt = int(input("  Amount per tax year, Year 1 only from the residency date (integer, no commas): ").strip())
        cur = input("  Currency [e.g. USD, EUR, NIS]: ").strip().upper()
        acquired = input("  Asset acquired before return? [y/n] (for regular track only): ").strip().lower() == "y"
        years_raw = input(f"  Tax years active, 1 = residency year [e.g. 1-{MAX_YEARS} or 1,2,5-8]: ").strip()
        years = parse_years(years_raw)
        streams.append({
            "label": label, "source": source, "kind": kind,
            "annual_amount": amt, "currency": cur,
            "asset_acquired_before_return": acquired,
            "years_active": years,
        })
    plan = {"track": track, "residency_start": residency_start, "income_streams": streams}
    if us in VALID_US_STATUS:
        plan["us_person"] = True
        plan["us_status"] = us
    return plan


def parse_years(s: str) -> List[int]:
    out = set()
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", help="Path to JSON input file")
    args = ap.parse_args()
    if args.json:
        try:
            with open(args.json) as f:
                plan = json.load(f)
        except FileNotFoundError:
            print(f"error: no such file: {args.json}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"error: {args.json} is not valid JSON: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        plan = interactive()
    try:
        validate(plan)
    except PlanError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    print(render(plan))


if __name__ == "__main__":
    main()
