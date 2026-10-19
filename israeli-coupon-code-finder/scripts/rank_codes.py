#!/usr/bin/env python3
"""Rank candidate coupon codes and print one summary table.

This script does NOT find codes. It takes codes you already gathered from a
live web search and orders them, so the final answer is a single ranked table
instead of a messy list. It deliberately refuses to invent anything: a code
with no source or no date is pushed to the bottom and marked low confidence.

Input JSON (a list of objects):
  [
    {
      "code": "STRING",
      "source": "link to where the code was found",
      "date_seen": "YYYY-MM-DD",
      "discount": "human text, e.g. ten percent off",
      "conditions": "min cart / new-customer-only / exclusions",
      "confidence": "high | medium | low",  (optional; inferred if missing)
      "expires": "YYYY-MM-DD"               (optional; expired codes are dropped)
    }
  ]

Usage:
  python scripts/rank_codes.py --file candidates.json
  echo '[...]' | python scripts/rank_codes.py
  python scripts/rank_codes.py --file candidates.json --today 2026-10-19
  python scripts/rank_codes.py --example
"""

import argparse
import datetime
import json
import sys

CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


def infer_confidence(item):
    """A code is only as trustworthy as its provenance."""
    explicit = (item.get("confidence") or "").strip().lower()
    if explicit in CONFIDENCE_RANK:
        # A code whose expiry cannot be read is never "high", whatever the input says.
        if explicit == "high" and parse_expiry(item.get("expires")) == "unreadable":
            return "medium"
        return explicit
    has_source = bool((item.get("source") or "").strip())
    has_date = bool((item.get("date_seen") or "").strip())
    expiry = parse_expiry(item.get("expires"))
    has_terms = bool((item.get("conditions") or "").strip()) or isinstance(expiry, datetime.date)
    if has_source and has_date and has_terms and expiry != "unreadable":
        return "high"
    if has_source and has_date:
        return "medium"
    return "low"


def sort_key(item):
    conf = CONFIDENCE_RANK[infer_confidence(item)]
    # Newer date_seen first within the same confidence tier.
    date = item.get("date_seen") or ""
    return (conf, _negated(date))


def _negated(date_str):
    # Reverse lexical order for ISO dates so newer sorts first.
    return tuple(-ord(c) for c in date_str)


# The exact keys render() reads. Documented in SKILL.md; keep the two in step.
RECOGNISED_KEYS = {"code", "source", "date_seen", "discount", "conditions", "confidence",
                   "expires"}


def parse_expiry(value):
    """Return a date, None when absent, or the string "unreadable"."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return "unreadable"


def split_expired(items, today):
    """Drop codes whose expiry is before today. An expired code is not a discount."""
    live, expired, unreadable = [], [], []
    for it in items:
        exp = parse_expiry(it.get("expires"))
        if exp == "unreadable":
            unreadable.append(it)
            live.append(it)
        elif exp is not None and exp < today:
            expired.append(it)
        else:
            live.append(it)
    return live, expired, unreadable


def conditions_cell(item):
    exp = str(item.get("expires") or "").strip()
    cond = str(item.get("conditions") or "").strip()
    if exp:
        flag = "" if parse_expiry(exp) != "unreadable" else " (unreadable date, check it)"
        cond = f"expires {exp}{flag}" + (f"; {cond}" if cond else "")
    return cell(cond)


def cell(value):
    text = str(value if value not in (None, "") else "-")
    return text.replace("|", "/").replace("\n", " ").strip()


def render(items):
    if not items:
        return ("No verified codes to show. Do NOT invent any. "
                "Fall back to store-direct levers (newsletter, app, loyalty club) "
                "and tell the shopper to verify at checkout.")
    ranked = sorted(items, key=sort_key)
    header = ["Code", "Source", "Date seen", "Discount", "Conditions", "Confidence"]
    rows = [header, ["---"] * len(header)]
    for it in ranked:
        rows.append([
            cell(it.get("code")),
            cell(it.get("source")),
            cell(it.get("date_seen")),
            cell(it.get("discount")),
            conditions_cell(it),
            infer_confidence(it),
        ])
    table = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    best = ranked[0]
    note = (f"\n\nTry this first: {cell(best.get('code'))} "
            f"(confidence: {infer_confidence(best)}).\n"
            "Verify at checkout: codes expire fast. If it is rejected, try the next row.")
    return table + note


EXAMPLE = [
    {"code": "REAL-FROM-SEARCH-A", "source": "aggregator link", "date_seen": "2026-06-07",
     "discount": "fifteen percent off", "conditions": "min cart, new customers only",
     "confidence": "high", "expires": "2099-12-31"},
    {"code": "REAL-FROM-SEARCH-B", "source": "store newsletter", "date_seen": "2026-06-01",
     "discount": "free shipping", "conditions": "no minimum"},
    {"code": "REAL-FROM-SEARCH-C", "source": "", "date_seen": "",
     "discount": "claims big discount", "conditions": ""},
    {"code": "REAL-FROM-SEARCH-D", "source": "aggregator link", "date_seen": "2026-01-02",
     "discount": "twenty percent off", "conditions": "", "expires": "2026-01-31"},
]


def main():
    p = argparse.ArgumentParser(description="Rank candidate coupon codes into one summary table.")
    p.add_argument("--file", help="Path to a JSON file with candidate codes.")
    p.add_argument("--example", action="store_true", help="Print a worked example.")
    p.add_argument("--today", help="Date to test expiry against, YYYY-MM-DD (default: today).")
    args = p.parse_args()

    if args.today:
        try:
            today = datetime.date.fromisoformat(args.today)
        except ValueError:
            print(f"--today must be YYYY-MM-DD, got {args.today!r}.", file=sys.stderr)
            return 1
    else:
        today = datetime.date.today()

    if args.example:
        print(render(filter_expired(EXAMPLE, today)))
        return 0

    if args.file:
        try:
            raw = open(args.file, encoding="utf-8").read()
        except OSError as e:
            print(f"Cannot read {args.file}: {e.strerror}", file=sys.stderr)
            return 1
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        print("No input. Pass --file, pipe JSON to stdin, or use --example.", file=sys.stderr)
        return 1
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Input is not valid JSON: {e}", file=sys.stderr)
        return 1
    if not isinstance(items, list):
        print("Input must be a JSON list of candidate-code objects.", file=sys.stderr)
        return 1
    if not all(isinstance(it, dict) for it in items):
        print("Every item must be a JSON object.", file=sys.stderr)
        return 1

    # Guessed field names are the common failure here, and silently rendering a
    # table of dashes is worse than refusing: it looks like a real answer and
    # ends with "try this first" for a code nothing is known about.
    unknown = [it for it in items if not (RECOGNISED_KEYS & set(it))]
    if items and unknown:
        print(f"{len(unknown)} of {len(items)} item(s) carry none of the recognised keys.",
              file=sys.stderr)
        print("Expected keys: " + ", ".join(sorted(RECOGNISED_KEYS))
              + ". Note the field is date_seen, not date.", file=sys.stderr)
        return 1

    # Partial-schema input is the common real failure: an agent guesses "date"
    # or "expires", the column renders as "-", and the table still looks finished.
    # Name the keys being ignored rather than dropping them silently.
    ignored = sorted({k for it in items for k in it} - RECOGNISED_KEYS)
    if ignored:
        print("Ignoring unrecognised key(s): " + ", ".join(ignored)
              + ". Recognised keys are: " + ", ".join(sorted(RECOGNISED_KEYS))
              + " (the date field is date_seen).", file=sys.stderr)

    live = filter_expired(items, today)
    if items and not live:
        print("No verified codes to show: every candidate has expired. Do NOT invent any. "
              "Fall back to store-direct levers (newsletter, app, loyalty club).")
        return 0
    print(render(live))
    return 0


def filter_expired(items, today):
    live, expired, unreadable = split_expired(items, today)
    if expired:
        print(f"Dropped {len(expired)} expired code(s) (expiry before {today.isoformat()}): "
              + ", ".join(cell(it.get("code")) for it in expired), file=sys.stderr)
    if unreadable:
        print(f"{len(unreadable)} code(s) have an expiry the script cannot read "
              "(use YYYY-MM-DD); kept and flagged: "
              + ", ".join(cell(it.get("code")) for it in unreadable), file=sys.stderr)
    return live


if __name__ == "__main__":
    sys.exit(main())
