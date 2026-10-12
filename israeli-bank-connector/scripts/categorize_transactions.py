#!/usr/bin/env python3
"""Categorize Israeli bank transactions by spending category.

Applies Israeli-specific merchant categorization to bank transaction data,
supporting common Israeli merchants, supermarkets, and service providers.

Usage:
    python scripts/categorize_transactions.py --json transactions.json
    python scripts/categorize_transactions.py --example

Input: either a JSON array of transaction objects, or the scrape result that
israeli-bank-scrapers (and israeli-bank-mcp's fetch-transactions tool) returns,
i.e. an object with "accounts": [{"accountNumber", "currency"?, "txns": [...]}].
Each transaction needs a "description" and an amount. The amount is read from
"amount" (CSV-style input) or, when that is absent, from "chargedAmount", which is
the field the library actually emits. The library has no "amount" field at all.
"""

import sys
import json
import argparse
import re
from collections import defaultdict


# Israeli merchant patterns mapped to categories
MERCHANT_PATTERNS = {
    # Lines that dominate a real Israeli statement and previously all fell into Other.
    r"(?i)(mashkanta|משכנתא|משכנת)": "housing",
    r"(?i)(halvaa|הלוואה|החזר\s*הלוואה)": "housing",
    r"(?i)(sechar\s*dira|שכר\s*דירה)": "housing",
    r"(?i)(amlat|עמלת|עמלה|דמי\s*ניהול\s*חשבון)": "other",
    # Tax and National Insurance remittances. Real outflows, but not consumption and not a
    # business expense, so they get their own bucket rather than hiding in Insurance/Other.
    r"(?i)(bituach\s*leumi|ביטוח\s*לאומי)": "taxes",
    # Only a TAX advance. A bare "מקדמה" is any down payment (a wedding hall, a contractor).
    r"(?i)(mas\s*hachnasa|מס\s*הכנסה|מקדמו?ת?ה?\s*(?:ל?מס|ל?מע\"מ|ל?מע״מ|ל?ביטוח\s*לאומי)|מע\"מ|מע״מ)": "taxes",
    r"(?i)(gan\s*yeladim|גן\s*ילדים|בית\s*ספר|קורס(?![א-ת])|צהרון)": "education",
    # Groceries (mazon)
    r"(?i)(shufersal|שופרסל)": "groceries",
    r"(?i)(rami.?levy|רמי לוי)": "groceries",
    r"(?i)(victory|ויקטורי)": "groceries",
    r"(?i)(yochananof|יוחננוף)": "groceries",
    r"(?i)(osher.?ad|אושר עד)": "groceries",
    r"(?i)(mega|מגה)": "groceries",
    r"(?i)(tiv.?taam|טיב טעם)": "groceries",
    r"(?i)(am.?pm|עם:פם)": "groceries",
    # Transportation (tahaburah)
    r"(?i)(rav.?kav|רב קו)": "transportation",
    r"(?i)(sonol|סונול)": "transportation",
    r"(?i)(paz|פז(?![א-ת]))": "transportation",
    r"(?i)(delek|דלק(?![א-ת]))": "transportation",
    r"(?i)(gett|גט(?![א-ת]))": "transportation",
    r"(?i)(yango|יאנגו)": "transportation",
    # Utilities (shartuim)
    r"(?i)(israel\s*electric|חברת\s*ה?\s*חשמל)": "utilities",
    r"(?i)(mekorot|מקורות)": "utilities",
    r"(?i)(bezeq|בזק(?![א-ת]))": "utilities",
    r"(?i)(partner|פרטנר)": "utilities",
    r"(?i)(cellcom|סלקום)": "utilities",
    r"(?i)(hot|הוט(?![א-ת]))": "utilities",
    r"(?i)(pelephone|פלאפון)": "utilities",
    # Healthcare (briut)
    r"(?i)(clalit|כללית)": "healthcare",
    r"(?i)(maccabi|מכבי)": "healthcare",
    r"(?i)(meuhedet|מאוחדת)": "healthcare",
    r"(?i)(leumit|לאומית)": "healthcare",
    r"(?i)(super.?pharm|סופר פארם)": "healthcare",
    # Housing (diur)
    r"(?i)(arnona|ארנונה)": "housing",
    r"(?i)(vaad\s*bayit|ועד\s*ה?\s*בית)": "housing",
    r"(?i)(rent(?!\s*-?\s*a\s*-?\s*car)|שכירות)": "housing",
    # Education (chinuch)
    r"(?i)(university|אוניברסיט)": "education",
    r"(?i)(college|מכללה)": "education",
    # Entertainment (bilui)
    r"(?i)(cinema|סינמה|yes.?planet)": "entertainment",

    # Restaurants and cafes. SKILL.md lists them under Entertainment; two unreachable
    # "restaurants"/"shopping" category names were removed rather than left as dead code.
    r"(?i)(restaurant|מסעד|cafe|קפה(?![א-ת])|wolt|וולט|tenbis|10bis|תן ביס|מזנון|פיצה|pizza|בורגר|burger)": "entertainment",
    r"(?i)(netflix)": "entertainment",
    r"(?i)(spotify)": "entertainment",
    r"(?i)(apple.*music|itunes)": "entertainment",
    # Insurance (bituach). NOTE: these are ALSO the names of the companies that manage
    # pension and gemel funds, so the savings patterns below must be tested FIRST.
    r"(?i)(harel|הראל)": "insurance",
    r"(?i)(migdal|מגדל(?![א-ת]))": "insurance",
    r"(?i)(menora|מנורה)": "insurance",
    r"(?i)(clal.?bituach|כלל.?ביטוח)": "insurance",
}

# Tested BEFORE MERCHANT_PATTERNS. A line like "הפקדה לקרן פנסיה מגדל" contains both a
# savings word and an insurance-company name; first-match ordering over a single dict
# classified it as insurance, which put pension money into Total Spending and defeated the
# whole savings/spending split. Priority patterns resolve that collision explicitly.
PRIORITY_PATTERNS = {
    # Cooking-gas (LPG) suppliers are utilities. Tested here, ahead of the Paz fuel
    # pattern in MERCHANT_PATTERNS: v1.3.0 guarded "פז" so it no longer fires on "פזגז",
    # but nothing then matched "פזגז" and a real gas bill fell through to Other.
    r"(?i)(pazgas|פזגז|סופרגז|supergas|אמישראגז|amisragas|דורגז|dorgas)": "utilities",
    # The monthly credit-card bill as it appears in the BANK account. Tested first: when
    # the card company's own itemised transactions are also loaded, counting this line as
    # well counts every card purchase twice. Bare "max"/"מקס" is NOT a token here: it is also
    # Max Brenner, Max Stock, Max Fashion. "מקס" alone as the WHOLE description is handled
    # in categorize_transaction instead.
    # Bare "amex"/"אמקס" is treated like bare "max": only as the whole description.
    r"(?i)(isracard|ישראכרט|max\s*it|מקס\s*איט|visa\s*cal|כאל(?![א-ת])|כ\.א\.ל|כרטיסי\s*אשראי|לאומי\s*קארד|leumi\s*card|american\s*express|אמריקן\s*אקספרס|diners|דיינרס)": "card_bill",
    # Money the user moves to themselves: buying foreign currency into their own forex
    # account. The ILS leg would otherwise be "spending" while the USD leg is excluded.
    r"(?i)(המרת\s*מט\"ח|רכישת\s*מט\"ח|המרת\s*מט״ח|רכישת\s*מט״ח)": "transfer",
    r"(?i)(pension|פנסי)": "savings",
    # Pension products and fund managers that appear on a direct debit with no "pension"
    # word, plus bank deposits and securities purchases: all the user's own money.
    # Generic words ("מיטב", "חיסכון", "פקדון") also name shops and bottle deposits, so they
    # only count with a fund or deposit context.
    r"(?i)(makefet|מקפת|mivtachim|מנורה\s*מבטחים|מבטחים\s*(?:פנסיה|גמל|החדשה)|altshuler|אלטשולר|meitav\s*dash|מיטב\s*(?:דש|גמל|השקעות|פנסיה|בית\s*השקעות)|ילין\s*לפידות|yelin\s*lapidot|פק\"מ|פק״מ)": "savings",
    r"(?i)((?:הפקדה|העברה|פתיחת)\s*(?:ל|ב)?\s*(?:פי?קדון|חיסכון|תו?כנית\s*חיסכון)|פי?קדון\s*(?:שקלי|דולרי|מט\"ח|קצר|ארוך|מתחדש|נזיל|בנקאי)|תו?כנית\s*חיסכון|קרן\s*כספית|ני\"ע|ני״ע|ניירות\s*ערך)": "savings",
    r"(?i)(hishtalmut|השתלמות)": "savings",
    r"(?i)(gemel|גמל(?![א-ת]))": "savings",
    r"(?i)(kupat.?gemel|קופת.?גמל)": "savings",
}

CATEGORY_NAMES = {
    "groceries": ("Groceries", "mazon"),
    "transportation": ("Transportation", "tahaburah"),
    "utilities": ("Utilities", "shartuim"),
    "healthcare": ("Healthcare", "briut"),
    "housing": ("Housing", "diur"),
    "education": ("Education", "chinuch"),
    "entertainment": ("Entertainment", "bilui"),
    "insurance": ("Insurance", "bituach"),
    "savings": ("Savings", "chisachon"),
    "card_bill": ("Card bill", "chiyuv kartis"),
    "transfer": ("Own transfer", "haavara"),
    "taxes": ("Taxes and BL", "misim"),
    "other": ("Other", "acher"),
}


# The one-letter Hebrew prefixes. A statement line says "הפקדה לפנסיה", not "הפקדה פנסיה",
# so any guard that treats the preceding letter as part of the word will refuse to match
# the very phrasing that is normal in Hebrew. Rather than try to express that in a
# lookbehind, the description is expanded before matching (see _expand_hebrew_prefixes).
# ONLY lamed. The other one-letter prefixes are what generate false positives when the
# de-prefixed fragment collides with a pattern: "הדלקה" -> "דלקה" hits the fuel stem,
# "בגט" -> "גט" hits Gett, "מבזק" -> "בזק", "מקפה" -> "קפה", "שגמל" -> "גמל". Lamed is the
# prefix that actually matters here, because the phrasing this exists to rescue is
# "הפקדה לפנסיה" and "ניכוי לגמל", and it introduces none of those collisions.
HEBREW_PREFIXES = "ל"


def _expand_hebrew_prefixes(description: str) -> str:
    """Append a de-prefixed copy of every Hebrew token that starts with a prefix letter.

    Only the prefix lamed is stripped; see HEBREW_PREFIXES for why.

    The leading Hebrew-letter guard in _whole_word() exists to stop a pattern matching in
    the MIDDLE of a longer word, but it cannot tell a prefix letter from a word letter, so
    it also blocks "לפנסיה" and "לגמל". Matching against the original text plus a
    space-separated de-prefixed copy keeps the mid-word protection (the copy is tokenised,
    so a fragment is never adjacent to anything) while letting a prefixed word match.
    """
    tokens = re.findall(r"[\u05d0-\u05ea]+", description)
    stripped = [tok[1:] for tok in tokens if len(tok) > 2 and tok[0] in HEBREW_PREFIXES]
    if not stripped:
        return description
    return description + " " + " ".join(stripped)


def _whole_word(pattern: str) -> str:
    """Make a pattern match as a whole token in BOTH scripts.

    Two guards, because the two scripts fail differently:

    - Hebrew has no word boundary the regex engine understands, so a bare substring fires
      inside a longer word ("פז" inside "פזגז", "מגדל" inside "קניון מגדל שלום"). A leading
      Hebrew-letter lookbehind fixes that. A trailing Hebrew guard cannot be applied
      blanketly because several patterns are deliberately stems: "פנסי" has to keep matching
      "פנסיה". Patterns that must match as a complete token carry their own trailing guard
      in the tables above.
    - Latin needs the opposite treatment and previously had NONE, which is why "hot" fired
      on "Hotel Dan" and "PHOTO SHOP", "mega" on "Omega Watches", "rent" on "Parent Teacher
      Assoc", and "paz" on "Pazzo Pizza". Latin letter guards on both sides fix those and
      cannot affect Hebrew, since Hebrew characters are not in A-Za-z.
    """
    flags = ""
    if pattern.startswith("(?i)"):
        flags, pattern = "(?i)", pattern[4:]
    return (
        f"{flags}(?<![\u05d0-\u05ea])(?<![A-Za-z])"
        f"{pattern}"
        f"(?![A-Za-z])"
    )


def categorize_transaction(description: str) -> str:
    """Categorize a transaction based on merchant description.

    Args:
        description: Transaction merchant description text.

    Returns:
        Category string.
    """
    # Match against the description PLUS a de-prefixed copy of its Hebrew tokens, so that
    # "הפקדה לפנסיה" reaches the savings pattern while "קניון מגדל שלום" still cannot be
    # split mid-word. See _expand_hebrew_prefixes and _whole_word.
    if re.fullmatch(r"(?i)\s*(max|מקס|amex|אמקס)\s*", description or ""):
        # The card company named alone, which is how some banks print the bill line.
        return "card_bill"
    if re.fullmatch(r"\s*(מיטב|מבטחים|פי?קדון)\s*", description or ""):
        # A fund manager or a deposit named alone is how a bank prints the debit. As part of a
        # longer name the same words are shops and bottle deposits, so only the bare form counts.
        return "savings"
    if re.fullmatch(r"\s*מקדמות\s*", description or ""):
        return "taxes"
    haystack = _expand_hebrew_prefixes(description)
    for pattern, category in PRIORITY_PATTERNS.items():
        if re.search(_whole_word(pattern), haystack):
            if category == "card_bill" and re.search(r"(?i)(דמי\s*כרטיס|עמלת|עמלה|ריבית|הלוואה|הלוואת|fee|interest|loan)", description):
                # A card fee or interest line names the issuer but is real spending,
                # not the duplicated monthly bill.
                continue
            return category
    for pattern, category in MERCHANT_PATTERNS.items():
        if re.search(_whole_word(pattern), haystack):
            return category
    return "other"


# The ways israeli-bank-scrapers spells a shekel amount (src/constants.ts), plus the
# common CSV spellings. Anything else is a foreign-currency line.
SHEKEL_CODES = {"ILS", "NIS", "₪", 'ש"ח', "שח", "ש״ח"}
# Symbols normalised so "$" and "USD" do not become two separate foreign buckets.
CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}

# Buckets that are NOT spending. Savings is the user's own money changing pocket, a card
# bill duplicates the card's itemised lines, an own transfer moves money between the
# user's own accounts.
NOT_SPENDING = ("savings", "card_bill", "transfer")

# Every account number seen in a scrape object, including accounts with no transactions in
# the period (a Leumi savings account is usually empty), so a transfer INTO one is still
# recognised as an own transfer.
SCRAPED_ACCOUNTS = set()


def flatten_scrape_result(data):
    """Return a flat list of transaction dicts from either accepted input shape.

    The library returns {"success": ..., "accounts": [{..., "txns": [...]}]}. Feeding that
    object straight in used to be rejected, and feeding the extracted txns used to produce
    an all-zero report, because the script read only "amount". Each flattened transaction
    carries its account's currency (if any) so a foreign-currency account, which Leumi
    exposes from library 6.12.0, is not summed into shekel totals.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("accounts"), list):
        if data.get("success") is False:
            print(
                f"Error: the scrape reported failure ({data.get('errorType', 'unknown error')}"
                f"{': ' + str(data.get('errorMessage')) if data.get('errorMessage') else ''}). "
                "There are no transactions to analyse.",
                file=sys.stderr,
            )
            sys.exit(1)
        flat = []
        SCRAPED_ACCOUNTS.clear()
        SCRAPED_ACCOUNTS.update(
            str(a.get("accountNumber")) for a in data["accounts"]
            if isinstance(a, dict) and a.get("accountNumber")
        )
        for acc in data["accounts"]:
            if not isinstance(acc, dict):
                continue
            for txn in acc.get("txns") or []:
                if isinstance(txn, dict):
                    flat.append({**txn, "_accountCurrency": acc.get("currency"),
                                 "_accountNumber": acc.get("accountNumber")})
        return flat
    return None


def _norm_currency(cur):
    if cur is None:
        return None
    cur = str(cur).strip()
    return CURRENCY_SYMBOLS.get(cur, cur) or None


def _line_currency(txn: dict, uses_charged: bool):
    """Best-known currency of the amount this script will sum, or None for shekels."""
    cur = txn.get("chargedCurrency") if uses_charged else txn.get("currency")
    cur = cur or txn.get("_accountCurrency")
    if not cur and uses_charged:
        # A pending card charge can arrive unconverted: chargedCurrency missing and the
        # charged figure equal to a foreign original amount (visa-cal does this).
        orig_cur = txn.get("originalCurrency")
        try:
            same = abs(float(txn.get("chargedAmount"))) == abs(float(txn.get("originalAmount")))
        except (TypeError, ValueError):
            same = False
        if orig_cur and str(orig_cur).strip() not in SHEKEL_CODES and same:
            cur = orig_cur
    if not cur or str(cur).strip() in SHEKEL_CODES:
        return None
    return _norm_currency(cur)


def _to_number(raw, desc):
    """Coerce an amount to a finite float, or stop with a message. Never returns None."""
    if isinstance(raw, bool) or raw is None or (isinstance(raw, str) and not raw.strip()):
        print(
            f"Error: amount on {desc!r} is {raw!r}. A blank or null amount is not zero; it is "
            "usually a CSV with separate debit and credit columns. Merge them into one signed "
            "amount (debit negative, credit positive) before running this.",
            file=sys.stderr,
        )
        sys.exit(1)
    if isinstance(raw, str):
        try:
            raw = float(raw.replace(",", "").replace("₪", "").strip())
        except ValueError:
            print(
                f"Error: amount {raw!r} on {desc!r} is not a number. "
                "Bank CSV and Excel exports often quote amounts as text; convert the "
                "amount column to numbers before running this.",
                file=sys.stderr,
            )
            sys.exit(1)
    if not isinstance(raw, (int, float)):
        print(f"Error: amount on {desc!r} is a {type(raw).__name__}, not a number.", file=sys.stderr)
        sys.exit(1)
    if raw != raw or raw in (float("inf"), float("-inf")):
        print(f"Error: amount on {desc!r} is not a finite number.", file=sys.stderr)
        sys.exit(1)
    return float(raw)


def _names_account(desc, acct):
    """True if the description names this account number as its own token.

    Matches the full digits or the account part (last 6 digits, after bank and branch), but
    only as a delimited number, never inside a longer reference number. Hyphenated forms such
    as 12-800-123456 are read both whole and piecewise.
    """
    text = str(desc)
    # Joined on "-" and "/" only: a space between two numbers usually separates them.
    runs = re.findall(r"\d+", text) + [re.sub(r"\D", "", m) for m in re.findall(r"\d+(?:[-/]\d+)+", text)]
    tail = acct[-6:]
    for r in runs:
        if r == acct or (len(acct) > 6 and r == tail):
            return True
    return False


def _own_account_digits(transactions):
    digits = set()
    for raw in [t.get("_accountNumber") for t in transactions] + list(SCRAPED_ACCOUNTS):
        d = re.sub(r"\D", "", str(raw or ""))
        if len(d) >= 5:
            digits.add(d)
    return digits


def analyze_transactions(transactions: list[dict]) -> dict:
    """Analyze and categorize a list of transactions.

    Args:
        transactions: transaction dicts with 'description' and either 'amount' or the
            library's 'chargedAmount'.

    Returns:
        Analysis dictionary with category totals, top merchants, etc.
    """
    categories = defaultdict(float)
    category_count = defaultdict(int)
    merchants = defaultdict(float)
    credits = defaultdict(float)
    credit_total = 0.0
    categorized = []
    foreign_out = defaultdict(float)
    foreign_in = defaultdict(float)
    foreign_count = 0
    pending_total = 0.0
    pending_count = 0
    pending_unknown_count = 0
    pending_unknown_original = defaultdict(float)
    own_transfers_in = 0.0
    pending_full_price_count = 0
    pending_full_price_total = 0.0
    instalment_count = 0
    own_accounts = _own_account_digits(transactions)

    for txn in transactions:
        desc = txn.get("description", "Unknown")
        status = txn.get("status")
        if "amount" in txn:
            uses_charged = False
            raw_amount = _to_number(txn.get("amount"), desc)
        elif "chargedAmount" in txn:
            # israeli-bank-scrapers shape. chargedAmount is what is billed this period: for a
            # COMPLETED credit-card instalment purchase (tashlumim) it is the single
            # instalment, while originalAmount is the full purchase price. Pending lines are
            # the exception, handled below.
            uses_charged = True
            charged = txn.get("chargedAmount")
            # The library itself emits 0 for a not-yet-known charge (Max sends a null
            # actualPaymentAmount for pending lines), so on this path null means 0.
            raw_amount = 0.0 if charged is None and status == "pending" else _to_number(charged, desc)
        else:
            # Never treat a missing amount as zero. That is how the library's own output
            # used to produce an empty report with exit code 0.
            print(
                f"Error: transaction {desc!r} has neither 'amount' nor 'chargedAmount'. "
                "Pass a list of {description, amount} objects, or the israeli-bank-scrapers "
                "result object ({accounts: [{txns: [...]}]}).",
                file=sys.stderr,
            )
            sys.exit(1)

        original = txn.get("originalAmount")
        if isinstance(original, str):
            try:
                original = float(original.replace(",", "").strip())
            except ValueError:
                original = None
        original = original if isinstance(original, (int, float)) and not isinstance(original, bool) else None
        if uses_charged and status == "pending" and original and raw_amount and (original > 0) != (raw_amount > 0):
            # Visa Cal emits a pending CREDIT with a negative chargedAmount and a positive
            # originalAmount. The original's sign is the one that says refund vs purchase.
            raw_amount = abs(raw_amount) if original > 0 else -abs(raw_amount)

        if raw_amount == 0:
            if uses_charged and status == "pending":
                # Pending with the charge not yet known. Not summed, but not silently lost.
                pending_unknown_count += 1
                if original:
                    cur = _norm_currency(txn.get("originalCurrency")) or "ILS"
                    cur = "ILS" if cur in SHEKEL_CODES else cur
                    pending_unknown_original[cur] += abs(original)
            # A zero line otherwise carries no signal and would create an empty merchant row.
            continue
        amount = abs(raw_amount)

        currency = _line_currency(txn, uses_charged)
        if currency:
            # A foreign-currency figure is not a shekel figure. Adding it to the totals
            # would mix USD and ILS in one number, so it is reported apart, by currency,
            # with money out and money in kept separate.
            (foreign_in if raw_amount > 0 else foreign_out)[currency] += amount
            foreign_count += 1
            categorized.append({**txn, "amount": raw_amount, "category": None,
                                "is_credit": raw_amount > 0, "currency": currency,
                                "excluded": "foreign_currency"})
            continue

        inst = txn.get("installments") if isinstance(txn.get("installments"), dict) else {}
        if (uses_charged and status == "pending" and txn.get("type") == "installments"
                and (inst.get("total") or 0) > 1 and original and abs(original) == amount):
            # Visa Cal reports a PENDING instalment purchase at the full price. Counting it
            # would put the whole purchase into this month; dividing would be a guess.
            pending_full_price_count += 1
            pending_full_price_total += amount
            categorized.append({**txn, "amount": raw_amount, "category": None,
                                "is_credit": raw_amount > 0,
                                "excluded": "pending_instalment_full_price"})
            continue

        if status == "pending" and raw_amount < 0:
            # Pending lines are included (they are real spending) but surfaced, because a
            # pending figure can still change or disappear before it is billed.
            pending_total += amount
            pending_count += 1
        if txn.get("type") == "installments" and raw_amount < 0:
            instalment_count += 1
        category = categorize_transaction(desc)
        if own_accounts and category not in ("savings", "card_bill"):
            line_acct = re.sub(r"\D", "", str(txn.get("_accountNumber") or ""))
            if any(a != line_acct and _names_account(desc, a) for a in own_accounts):
                # The description names another of the user's own scraped accounts.
                category = "transfer"

        # A positive amount on a statement line is money coming IN: a refund, a reversal,
        # but ALSO salary, a transfer in, a loan drawdown. Counting its absolute value as
        # spending inflates every total and every percentage, so it is tracked separately.
        # It is NOT netted off the category totals, and NO net view is offered, because
        # nothing here can tell a refund from a salary: both are simply positive amounts.
        if raw_amount > 0 and category == "transfer":
            # The inbound leg of an own transfer is not income either.
            own_transfers_in += raw_amount
        elif raw_amount > 0:
            credits[category] += raw_amount
            credit_total += raw_amount
        else:
            categories[category] += amount
            merchants[desc] += amount
            category_count[category] += 1
        categorized.append({**txn, "amount": raw_amount, "category": category, "is_credit": raw_amount > 0})

    # Money moved into a pension, keren hishtalmut, gemel or deposit is NOT spending, a
    # card bill duplicates the itemised card lines, and an own transfer is not an outflow.
    savings = categories.get("savings", 0.0)
    card_bills = categories.get("card_bill", 0.0)
    own_transfers = categories.get("transfer", 0.0)
    credits_by_category = {k: round(v, 2) for k, v in sorted(credits.items(), key=lambda x: x[1], reverse=True)}
    total = sum(v for k, v in categories.items() if k not in NOT_SPENDING)
    total_outflow = total + savings

    excluded_descs = {t.get("description", "Unknown") for t in categorized if t.get("category") in NOT_SPENDING}
    top_merchants = sorted(
        ((m, a) for m, a in merchants.items() if m not in excluded_descs),
        key=lambda x: x[1], reverse=True,
    )[:10]

    warnings = []
    debit_lines = sum(category_count.values())
    if debit_lines == 0 and credit_total > 0:
        warnings.append(
            "Every shekel line is positive, so Total Spending is 0. Some exports (card "
            "statements especially) show charges as positive numbers. Check the sign "
            "convention before reporting this."
        )

    return {
        "total_spending": round(total, 2),
        "total_savings": round(savings, 2),
        "total_outflow": round(total_outflow, 2),
        "total_card_bills": round(card_bills, 2),
        "total_own_transfers": round(own_transfers, 2),
        "total_credits": round(credit_total, 2),
        "credits_by_category": credits_by_category,
        "pending_included": round(pending_total, 2),
        "pending_count": pending_count,
        "pending_unknown_count": pending_unknown_count,
        "pending_unknown_original": {k: round(v, 2) for k, v in sorted(pending_unknown_original.items())},
        "total_own_transfers_in": round(own_transfers_in, 2),
        "pending_full_price_count": pending_full_price_count,
        "pending_full_price_total": round(pending_full_price_total, 2),
        "instalment_lines": instalment_count,
        "foreign_currency_out": {k: round(v, 2) for k, v in sorted(foreign_out.items())},
        "foreign_currency_in": {k: round(v, 2) for k, v in sorted(foreign_in.items())},
        "foreign_currency_count": foreign_count,
        # by_category holds only what Total Outflow is made of (spending + savings), so the
        # percentage column always divides the same population it lists.
        "by_category": {k: round(v, 2) for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)
                        if k not in ("card_bill", "transfer")},
        "category_counts": dict(category_count),
        "top_merchants": [(m, round(a, 2)) for m, a in top_merchants],
        "warnings": warnings,
        "transactions": categorized,
    }


def format_analysis(analysis: dict, period: str = "Current") -> str:
    """Format spending analysis for display."""
    fx = lambda d: ", ".join(f"{v:,.2f} {k}" for k, v in d.items()) or "none"
    lines = [
        f"=== Spending Analysis ({period}) ===",
        "",
        *[f"  WARNING: {w}" for w in analysis.get("warnings", [])],
        f"  Total Spending: {analysis['total_spending']:>10,.2f} NIS",
        f"  Into Savings:   {analysis['total_savings']:>10,.2f} NIS  (not counted as spending)",
        f"  Total Outflow:  {analysis['total_outflow']:>10,.2f} NIS  (spending + savings)",
        *([f"  Card Bills:     {analysis['total_card_bills']:>10,.2f} NIS  (bank-side card bill: in NEITHER figure above. Add it to spending only if the card's own transactions are absent from this data)"]
          if analysis.get("total_card_bills") else []),
        *([f"  Own Transfers:  {analysis['total_own_transfers']:>10,.2f} NIS out, {analysis['total_own_transfers_in']:,.2f} NIS in  (between the user's own accounts or into their own forex account: in no other figure)"]
          if analysis.get("total_own_transfers") or analysis.get("total_own_transfers_in") else []),
        *([f"  Credits In:     {analysis['total_credits']:>10,.2f} NIS  (refunds, reversals, salary, transfers in: excluded above)"]
          if analysis.get("total_credits") else []),
        *([f"  Pending:        {analysis['pending_included']:>10,.2f} NIS  ({analysis['pending_count']} not-yet-billed lines, included above; may still change)"]
          if analysis.get("pending_count") else []),
        *([f"  Pending, amount unknown: {analysis['pending_unknown_count']} lines (original amounts: {fx(analysis['pending_unknown_original'])}): NOT summed"]
          if analysis.get("pending_unknown_count") else []),
        *([f"  Pending instalment purchases at full price: {analysis['pending_full_price_count']} lines, {analysis['pending_full_price_total']:,.2f} NIS: NOT summed (this month's share is unknown until billed)"]
          if analysis.get("pending_full_price_count") else []),
        *([f"  Instalments:    {analysis['instalment_lines']} lines counted at the instalment charged, not the full purchase price"]
          if analysis.get("instalment_lines") else []),
        *([f"  Foreign currency, not summed: out {fx(analysis['foreign_currency_out'])}; in {fx(analysis['foreign_currency_in'])} ({analysis['foreign_currency_count']} lines)"]
          if analysis.get("foreign_currency_count") else []),
        "",
        "  By Category:",
        f"  {'Category':<25} {'Amount':>10}  {'% of outflow':>12}",
        f"  {'─' * 52}",
    ]

    total = analysis.get("total_outflow") or 1
    for category, amount in analysis["by_category"].items():
        en_name, he_name = CATEGORY_NAMES.get(category, (category, ""))
        pct = amount / total * 100
        label = f"{en_name} ({he_name})"
        lines.append(f"  {label:<25} {amount:>10,.2f}  {pct:>11.1f}%")

    lines.extend([
        "",
        "  Top Merchants:",
        f"  {'Merchant':<30} {'Amount':>10}",
        f"  {'─' * 42}",
    ])
    for merchant, amount in analysis["top_merchants"]:
        lines.append(f"  {merchant[:30]:<30} {amount:>10,.2f}")

    return "\n".join(lines)


_IL_TZ = None


def _line_date(txn: dict, field: str):
    """The calendar date of a line in Israel time, from ISO or dd/mm/yyyy text."""
    global _IL_TZ
    from datetime import datetime, date
    raw = txn.get(field)
    if not isinstance(raw, str) or not raw.strip():
        return None
    raw = raw.strip()
    m = re.fullmatch(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4})", raw)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is not None:
        # The library stores Israeli local midnight as a UTC instant ("...T21:00:00.000Z"
        # is the NEXT day in Israel). Taking the first ten characters would move every such
        # line back one day, and across a month boundary into the wrong month.
        if _IL_TZ is None:
            try:
                from zoneinfo import ZoneInfo
                _IL_TZ = ZoneInfo("Asia/Jerusalem")
            except Exception:
                print(
                    "Error: no time-zone data for Asia/Jerusalem (common on Windows). "
                    "Install it with `pip install tzdata` and re-run.",
                    file=sys.stderr,
                )
                sys.exit(1)
        dt = dt.astimezone(_IL_TZ)
    return dt.date()


def filter_by_period(transactions, start, end, field):
    from datetime import date
    lo = date.fromisoformat(start) if start else None
    hi = date.fromisoformat(end) if end else None
    kept = []
    for t in transactions:
        d = _line_date(t, field)
        if d is None:
            print(
                f"Error: {t.get('description', 'Unknown')!r} has no usable {field!r} "
                "(ISO or dd/mm/yyyy), so it cannot be placed in the period.",
                file=sys.stderr,
            )
            sys.exit(1)
        if (lo is None or d >= lo) and (hi is None or d <= hi):
            kept.append(t)
    return kept


def generate_example_transactions() -> list[dict]:
    """Generate example Israeli transactions for testing."""
    return [
        {"date": "2026-01-03", "description": "Shufersal Deal", "amount": -450.00},
        {"date": "2026-01-05", "description": "Rav-Kav Charge", "amount": -220.00},
        {"date": "2026-01-06", "description": "Israel Electric Company", "amount": -380.00},
        {"date": "2026-01-08", "description": "Rami Levy", "amount": -320.00},
        {"date": "2026-01-10", "description": "Partner Communications", "amount": -99.00},
        {"date": "2026-01-12", "description": "Arnona Payment", "amount": -850.00},
        {"date": "2026-01-14", "description": "Netflix", "amount": -49.90},
        {"date": "2026-01-15", "description": "Clalit Health Services", "amount": -120.00},
        {"date": "2026-01-18", "description": "Sonol Fuel", "amount": -280.00},
        {"date": "2026-01-20", "description": "Super Pharm", "amount": -95.00},
        {"date": "2026-01-22", "description": "Shufersal Online", "amount": -510.00},
        {"date": "2026-01-25", "description": "Harel Insurance", "amount": -450.00},
        {"date": "2026-01-27", "description": "Pension Contribution", "amount": -1200.00},
        {"date": "2026-01-28", "description": "Random Store", "amount": -150.00},
        {"date": "2026-01-30", "description": "Yes Planet Cinema", "amount": -85.00},
    ]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Categorize Israeli bank transactions"
    )
    parser.add_argument("--json", type=str, help="JSON file with transactions")
    parser.add_argument("--period", type=str, default="Current", help="Period label (a label only; use --from/--to to filter)")
    parser.add_argument("--from", dest="date_from", type=str, help="Keep lines on or after this date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", type=str, help="Keep lines on or before this date (YYYY-MM-DD)")
    parser.add_argument("--exclude-pending", action="store_true",
                        help="Drop pending lines before analysis (for a closed month or an accountant export)")
    parser.add_argument("--date-field", choices=["date", "processedDate"], default="date",
                        help="Which date --from/--to filter on: date (transaction) or processedDate (billing)")
    parser.add_argument(
        "--example", action="store_true", help="Run with example transactions"
    )
    parser.add_argument(
        "--output-json", action="store_true",
        help="Output categorized transactions as JSON"
    )

    args = parser.parse_args()

    if args.example:
        transactions = generate_example_transactions()
        analysis = analyze_transactions(transactions)
        # --output-json must be honoured here too. It is documented as a general flag, so
        # returning the human-readable table for --example --output-json hands an agent
        # text it cannot parse.
        if args.output_json:
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
        else:
            print(format_analysis(analysis, "January 2026 (Example)"))
        return

    if args.json:
        try:
            with open(args.json, encoding="utf-8") as f:
                data = json.load(f)
            transactions = flatten_scrape_result(data)
            if transactions is None:
                print(
                    f"Error: {args.json} must contain a JSON array of transaction objects, or "
                    "an israeli-bank-scrapers result object with an 'accounts' array, "
                    f"got {type(data).__name__}.",
                    file=sys.stderr,
                )
                sys.exit(1)
            bad = next((i for i, x in enumerate(transactions) if not isinstance(x, dict)), None)
            if bad is not None:
                print(
                    f"Error: {args.json} entry {bad} is a {type(transactions[bad]).__name__}, "
                    "not a transaction object. Each entry needs at least a 'description' and "
                    "an 'amount'.",
                    file=sys.stderr,
                )
                sys.exit(1)
        except FileNotFoundError:
            print(f"Error: File not found: {args.json}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        if args.exclude_pending:
            transactions = [t for t in transactions if t.get("status") != "pending"]
        if args.date_from or args.date_to:
            try:
                transactions = filter_by_period(transactions, args.date_from, args.date_to, args.date_field)
            except ValueError as e:
                print(f"Error: --from/--to must be YYYY-MM-DD ({e})", file=sys.stderr)
                sys.exit(1)
        analysis = analyze_transactions(transactions)
        for w in analysis["warnings"]:
            print(f"Warning: {w}", file=sys.stderr)

        if args.output_json:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print(format_analysis(analysis, args.period))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
