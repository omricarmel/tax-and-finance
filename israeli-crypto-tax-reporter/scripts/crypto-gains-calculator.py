#!/usr/bin/env python3
"""
Israeli Crypto Capital Gains Calculator (FIFO Method)

Calculates cryptocurrency capital gains tax per Israeli Tax Authority regulations.
Uses FIFO (First In, First Out) cost basis method. Performs NO currency
conversion: every price_nis and fee_nis must already be in shekels.
Prints a disposal schedule in the Form 1399י columns and an advance-payment
(mikdama) schedule.

Usage:
    python crypto-gains-calculator.py --input transactions.csv --year 2024
    python crypto-gains-calculator.py --input transactions.csv --year 2024 --other-income 300000
    python crypto-gains-calculator.py --input transactions.csv --year 2024 --schedule
    python crypto-gains-calculator.py --input transactions.csv --year 2024 --advance-payments
    python crypto-gains-calculator.py --input transactions.csv --year 2024 --json
    python crypto-gains-calculator.py --demo

CSV Format:
    date,type,asset,amount,price_nis,fee_nis,exchange,notes

    price_nis is the TOTAL shekel consideration for the row, NOT the price per
    unit. Two ETH bought at 8,000 each is price_nis=16000. Getting this backwards
    rescales every gain by the quantity and the tool cannot detect it.

    type must be one of: buy, trade_buy, sell, trade_sell, staking, interest,
    airdrop, mining, fork, transfer, deposit, withdrawal. Any other value
    (including Hebrew labels from an Israeli exchange export) is NOT processed
    and is reported as an unrecognised row.
    2024-01-15,buy,BTC,0.5,75000,375,bits-of-gold,
    2024-08-20,sell,BTC,0.3,120000,600,bits-of-gold,

Requirements:
    Python 3.8+
    No external dependencies
"""

import argparse
import csv
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


# ============================================================
# Constants
# ============================================================

INDIVIDUAL_TAX_RATE = 0.25
# Section 91(b)(2)'s 30% rate is for the sale of a "נייר ערך בחבר-בני-אדם", a
# SECURITY IN A BODY CORPORATE, by a material shareholder. A fungible token is
# not one, and Circular 05/2018 classifies crypto as a נכס under s.88 taxed
# under s.91 without ever invoking (b)(2). This calculator never applies 30%.
CORPORATE_TAX_RATE = 0.23
# Surtax (mas yesafim), s.121B. Two limbs with two DIFFERENT tests:
#   (a)  3% on TOTAL taxable income above the threshold (salary included).
#   (a1) 2% on the part of CAPITAL-SOURCE taxable income that ITSELF exceeds the
#        threshold. Capital income stacked on top of a salary does not attract the
#        2% unless the capital income alone crosses the threshold. ITA execution instruction
#        (הוראת ביצוע) 05/2025, example 2: salary 400,000 + capital 700,000 -> 3% on
#        378,440 and no 2% at all. An earlier version of this script applied 5% to
#        the capital income sitting above the threshold after the salary, which
#        overstated the surtax for every salaried user.
# (a1) was added by amendment תשפ"ה-2 and applies from tax year 2025. Before
# that only the 3% limb existed, and it already reached capital gains, because
# "הכנסה חייבת" in s.121B(e) is total taxable income.
# "Capital-source" income excludes s.2(1)/(2) income and income from personal
# exertion, so mining (business income per Circular 05/2018 s.3.1.4) is not
# capital-source.
SURTAX_BASE_RATE = 0.03
SURTAX_CAPITAL_RATE = 0.02
SURTAX_CAPITAL_LIMB_FIRST_YEAR = 2025
# Threshold by tax year, from the Ordinance (s.121B(a) note and the s.121 table).
# The Ordinance fixes 721,560 for 2024 through 2027, so do not apply CPI.
SURTAX_THRESHOLDS = {
    2019: 649_560, 2020: 651_600, 2021: 647_640, 2022: 663_240, 2023: 698_280,
    2024: 721_560, 2025: 721_560, 2026: 721_560, 2027: 721_560,
}
SURTAX_THRESHOLD = SURTAX_THRESHOLDS[2026]
# Income-event types treated as capital-source for the 2% limb. Staking, airdrop
# and lending receipts are not produced by work or by a business unless the
# activity is itself a business, in which case s.2(1) applies and they are not.
CAPITAL_SOURCE_INCOME_TYPES = ("staking", "interest", "airdrop")
ADVANCE_PAYMENT_DAYS = 30


# ============================================================
# Data Types
# ============================================================

@dataclass
class Transaction:
    date: datetime
    tx_type: str  # buy, sell, trade_sell, trade_buy, income, airdrop, fork, mining
    asset: str
    amount: float
    # price_nis is the TOTAL shekel consideration for the whole row, NOT the price
    # per unit. A 2-ETH buy at 8,000 per ETH is price_nis=16000, not 8000. Getting
    # this backwards silently rescales every gain by the quantity: the skill's own
    # Scenario 2, transcribed per-unit, turns a 23,040 gain into a 627 loss.
    price_nis: float  # TOTAL NIS consideration for this row (never per unit)
    fee_nis: float
    exchange: str
    notes: str
    # Tax an Israeli platform withheld at source on this sale (optional column).
    tax_withheld_nis: float = 0.0
    # Position in the file, so that two separate sales on one day are never
    # folded into one 1399י notice.
    row: int = 0

    @property
    def price_per_unit(self) -> float:
        if self.amount == 0:
            return 0.0
        return self.price_nis / self.amount

    @property
    def cost_per_unit(self) -> float:
        """Cost per unit including fees for purchases."""
        if self.amount == 0:
            return 0.0
        return (self.price_nis + self.fee_nis) / self.amount

    @property
    def net_proceeds_per_unit(self) -> float:
        """Net proceeds per unit after fees for sales."""
        if self.amount == 0:
            return 0.0
        return (self.price_nis - self.fee_nis) / self.amount


@dataclass
class Lot:
    """A purchase lot for FIFO tracking."""
    date: datetime
    asset: str
    amount: float
    cost_per_unit_nis: float
    exchange: str
    notes: str

    @property
    def total_cost(self) -> float:
        return self.amount * self.cost_per_unit_nis


@dataclass
class GainEvent:
    """A realized gain/loss event."""
    disposal_date: datetime
    acquisition_date: datetime
    asset: str
    amount: float
    acquisition_cost_nis: float
    disposal_proceeds_nis: float
    gain_nis: float
    holding_days: int
    is_long_term: bool  # 12+ months
    exchange: str
    notes: str
    disposal_row: int = 0          # source row of the sale this lot belongs to
    tax_withheld_nis: float = 0.0  # withholding on the whole sale (first lot only)
    acquired_pre_2012: bool = False

    @property
    def tax_25(self) -> float:
        if self.gain_nis is None:
            return None
        return max(0, self.gain_nis * INDIVIDUAL_TAX_RATE)


@dataclass
class IncomeEvent:
    """An income event (staking, airdrop, mining)."""
    date: datetime
    asset: str
    amount: float
    value_nis: float
    income_type: str  # staking, airdrop, mining, interest
    notes: str


@dataclass
class AdvancePayment:
    """One Form 1399י notice: every disposal, gain or loss, gets one."""
    gain_event_date: datetime
    due_date: datetime
    gain_nis: float
    tax_due_nis: float
    asset: str
    loss_offset_nis: float = 0.0  # earlier losses (carried forward or same-year) used
    tax_withheld_nis: float = 0.0  # withheld at source by an Israeli platform


@dataclass
class TaxReport:
    year: int
    gain_events: list = field(default_factory=list)
    income_events: list = field(default_factory=list)
    advance_payments: list = field(default_factory=list)
    total_gains: float = 0.0
    total_losses: float = 0.0
    net_gain: float = 0.0
    total_income: float = 0.0
    other_income: float = 0.0  # non-crypto taxable income (salary, business) for surtax base
    other_capital_income: float = 0.0  # the part of other_income that is capital-source
    loss_carryforward: float = 0.0       # capital loss brought forward (Form 1344)
    loss_carryforward_used: float = 0.0
    tax_withheld_total: float = 0.0
    surtax_basis: str = "s.121B(a) 3% + s.121B(a1) 2%"
    capital_gains_tax: float = 0.0
    surtax_base: float = 0.0     # s.121B(a) 3% limb on the supplied total
    surtax_capital: float = 0.0  # s.121B(a1) 2% limb
    surtax_computed: bool = True
    surtax: float = 0.0
    total_tax_estimate: float = 0.0
    remaining_lots: dict = field(default_factory=dict)
    unpriced: list = field(default_factory=list)
    unrecognised_rows: int = 0
    warnings: list = field(default_factory=list)


# ============================================================
# Parser
# ============================================================

ISRAELI_PLATFORMS = ("bits of gold", "bits-of-gold", "bitsofgold", "bits_of_gold",
                     "bit2c", "ביטס אוף גולד", "ביט2סי")


def _israeli_platform(exchange: str) -> bool:
    """Whole-name match, so a foreign exchange such as Bitstamp is not flagged."""
    e = exchange.strip().lower()
    return any(e == k or e.startswith(k + " ") for k in ISRAELI_PLATFORMS)

def parse_csv(filepath: str):
    """Parse the transaction CSV. Returns (transactions, row_errors).

    A row that cannot be parsed is NEVER skipped silently. An Israeli export
    with DD/MM/YYYY dates or "200,000" amounts used to drop the row with a
    stderr-only line, after which the report printed complete:true and exit 0
    with a whole sale (and its 30-day notice) missing.
    """
    transactions = []
    row_errors = []

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            required_fields = {"date", "type", "asset", "amount", "price_nis"}
            if not required_fields.issubset(set(reader.fieldnames or [])):
                missing = required_fields - set(reader.fieldnames or [])
                print(f"Error: CSV missing required columns: {missing}", file=sys.stderr)
                print("Required columns: date, type, asset, amount, price_nis, fee_nis, exchange, notes", file=sys.stderr)
                sys.exit(1)

            has_currency = "currency" in (reader.fieldnames or [])
            for i, row in enumerate(reader, start=2):
                if has_currency and (row.get("currency") or "").strip().upper() not in ("", "ILS", "NIS", "₪", 'ש"ח', "ש״ח", "שח", "שקל"):
                    row_errors.append(
                        f"row {i}: currency={row.get('currency')!r}. This tool computes in "
                        f"SHEKELS only; convert the row to ILS before it reaches price_nis.")
                    continue
                try:
                    tx = Transaction(
                        date=datetime.strptime(row["date"].strip(), "%Y-%m-%d"),
                        tx_type=row["type"].strip().lower(),
                        asset=row["asset"].strip().upper(),
                        amount=float(row["amount"].strip()),
                        price_nis=float(row["price_nis"].strip()),
                        fee_nis=float(row.get("fee_nis", "0").strip() or "0"),
                        exchange=(row.get("exchange") or "").strip(),
                        notes=(row.get("notes") or "").strip(),
                        tax_withheld_nis=float((row.get("tax_withheld_nis") or "0").strip() or "0"),
                        row=i,
                    )
                    transactions.append(tx)
                except (ValueError, KeyError, AttributeError) as e:
                    row_errors.append(
                        f"row {i}: cannot be parsed ({e}). Dates must be YYYY-MM-DD and "
                        f"numbers must carry no thousands separator (200000, not 200,000).")

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Within one day, acquisitions before disposals. Rows carry no time, and
    # exchanges often export newest-first, which used to turn a same-day
    # buy-then-sell into an UNPRICED sale. FIFO still consumes the oldest lot.
    disposal_types = ("sell", "trade_sell")
    transactions.sort(key=lambda t: (t.date, t.tx_type in disposal_types, t.row))
    return transactions, row_errors


# Bitcoin's genesis block. Nothing on-chain predates it, so an earlier
# acquisition date is a data error (a mis-parsed format, or a placeholder),
# not a very early investor.
GENESIS = datetime(2009, 1, 3)


def validate_transactions(transactions: list) -> list:
    """Return a list of blocking data-quality problems in the parsed rows.

    Every check here exists because the calculator would otherwise produce a
    confident, wrong, SILENT answer. A sign-flipped exchange export or a
    mis-parsed date used to yield a zero-tax report with exit code 0, which a
    calling agent cannot distinguish from a genuinely tax-free year.
    """
    problems = []
    today = datetime.now()
    for tx in transactions:
        where = f"{tx.date:%Y-%m-%d} {tx.tx_type} {tx.asset}"
        if tx.amount < 0:
            problems.append(
                f"{where}: negative amount ({tx.amount}). Some exchanges export "
                f"disposals as negative quantities; convert them to positive rows "
                f"with type=sell rather than feeding the sign through.")
        elif tx.amount == 0:
            problems.append(f"{where}: zero amount. A zero-quantity row cannot be "
                            f"priced or matched; remove it or supply the quantity.")
        if tx.price_nis < 0:
            problems.append(f"{where}: negative price_nis ({tx.price_nis}).")
        if tx.fee_nis < 0:
            problems.append(f"{where}: negative fee_nis ({tx.fee_nis}).")
        if tx.tax_withheld_nis < 0:
            problems.append(f"{where}: negative tax_withheld_nis ({tx.tax_withheld_nis}).")
        if tx.tax_withheld_nis > 0 and tx.tx_type not in ("sell", "trade_sell"):
            problems.append(f"{where}: tax_withheld_nis on a row that is not a sale.")
        if tx.date < GENESIS:
            problems.append(
                f"{where}: date precedes the Bitcoin genesis block "
                f"({GENESIS:%Y-%m-%d}). Almost always a mis-parsed date format.")
        if tx.date > today:
            problems.append(f"{where}: date is in the future.")

    # Circular 05/2018 s.3.1.5.1 requires the consideration in a barter trade to be
    # the SAME shekel figure on both sides: the seller's proceeds and the buyer's
    # original cost. Divergent legs silently plant a wrong basis on the acquired
    # asset that only surfaces years later, on its disposal.
    from collections import defaultdict as _dd
    legs = _dd(lambda: {"sell": [], "buy": []})
    for tx in transactions:
        if tx.tx_type == "trade_sell":
            legs[tx.date]["sell"].append(tx)
        elif tx.tx_type == "trade_buy":
            legs[tx.date]["buy"].append(tx)
    for day, sides in legs.items():
        if not sides["sell"] or not sides["buy"]:
            side = "trade_buy" if sides["sell"] else "trade_sell"
            problems.append(
                f"{day:%Y-%m-%d}: a swap leg has no counterpart. Every trade_sell "
                f"needs a matching trade_buy on the same date and vice versa; the "
                f"missing side is {side}.")
            continue
        sold = sum(t.price_nis for t in sides["sell"])
        bought = sum(t.price_nis for t in sides["buy"])
        if sold and abs(sold - bought) > max(1.0, 0.01 * sold):
            problems.append(
                f"{day:%Y-%m-%d}: the two legs of the swap carry different shekel "
                f"values ({sold:,.2f} sold vs {bought:,.2f} bought). Circular "
                f"05/2018 s.3.1.5.1 requires the SAME figure to serve as the "
                f"seller's proceeds and the buyer's original cost, so one of the "
                f"two is wrong and the acquired asset's basis will be wrong too.")
    return problems


# ============================================================
# FIFO Engine
# ============================================================

class FIFOEngine:
    """FIFO cost basis calculator."""

    def __init__(self):
        # Asset -> deque of Lots (oldest first)
        self.lots: dict = defaultdict(deque)
        # Disposals with no matching purchase lot. Never priced, never guessed.
        self.unpriced: list = []
        self.gain_events: list = []
        self.income_events: list = []

    def process_buy(self, tx: Transaction):
        """Add a purchase lot to the FIFO queue."""
        lot = Lot(
            date=tx.date,
            asset=tx.asset,
            amount=tx.amount,
            cost_per_unit_nis=tx.cost_per_unit,
            exchange=tx.exchange,
            notes=tx.notes,
        )
        self.lots[tx.asset].append(lot)

    def process_sell(self, tx: Transaction) -> list:
        """Process a sale using FIFO, returning gain events."""
        events = []
        remaining_to_sell = tx.amount
        net_proceeds_per_unit = tx.net_proceeds_per_unit

        asset_lots = self.lots[tx.asset]

        while remaining_to_sell > 1e-10 and asset_lots:
            lot = asset_lots[0]

            if lot.amount <= remaining_to_sell + 1e-10:
                # Consume entire lot
                sell_amount = lot.amount
                remaining_to_sell -= sell_amount
                asset_lots.popleft()
            else:
                # Partial lot consumption
                sell_amount = remaining_to_sell
                lot.amount -= sell_amount
                remaining_to_sell = 0

            acquisition_cost = sell_amount * lot.cost_per_unit_nis
            disposal_proceeds = sell_amount * net_proceeds_per_unit
            gain = disposal_proceeds - acquisition_cost
            holding_days = (tx.date - lot.date).days

            event = GainEvent(
                disposal_date=tx.date,
                acquisition_date=lot.date,
                asset=tx.asset,
                amount=sell_amount,
                acquisition_cost_nis=acquisition_cost,
                disposal_proceeds_nis=disposal_proceeds,
                gain_nis=gain,
                holding_days=holding_days,
                is_long_term=holding_days >= 365,
                exchange=tx.exchange,
                notes=tx.notes,
                disposal_row=tx.row,
                tax_withheld_nis=tx.tax_withheld_nis if not events else 0.0,
                acquired_pre_2012=lot.date < datetime(2012, 1, 1),
            )
            events.append(event)

        if remaining_to_sell > 1e-10:
            print(
                f"WARNING: FIFO queue exhausted for {tx.asset}. "
                f"Attempted to sell {tx.amount} but only had enough lots for "
                f"{tx.amount - remaining_to_sell:.8f}. "
                f"Missing purchase records for {remaining_to_sell:.8f} {tx.asset}.",
                file=sys.stderr,
            )
            # NO cost basis is known for this portion. Do NOT invent one, and do
            # NOT invent an acquisition date: an earlier version set
            # acquisition_date = the disposal date and acquisition_cost = 0, so
            # the JSON output carried a fabricated acquisition fact and a tax
            # figure that overstated the client's liability, with no warning on
            # the JSON path at all. Record the event as UNPRICED and make the
            # caller resolve it.
            self.unpriced.append({
                "asset": tx.asset,
                "disposal_date": tx.date.strftime("%Y-%m-%d"),
                "unmatched_amount": remaining_to_sell,
                "disposal_proceeds_nis": remaining_to_sell * net_proceeds_per_unit,
            })
            event = GainEvent(
                disposal_date=tx.date,
                acquisition_date=None,
                asset=tx.asset,
                amount=remaining_to_sell,
                acquisition_cost_nis=None,
                disposal_proceeds_nis=remaining_to_sell * net_proceeds_per_unit,
                gain_nis=None,
                holding_days=None,
                is_long_term=False,
                exchange=tx.exchange,
                disposal_row=tx.row,
                notes=("UNPRICED: no matching purchase lot. Cost basis is UNKNOWN "
                       "and is NOT assumed to be zero. Supply the acquisition "
                       "record, or use the earliest available market price for "
                       "the asset and document the basis you used."),
            )
            events.append(event)

        self.gain_events.extend(events)
        return events

    def process_income(self, tx: Transaction, income_type: str):
        """Process income (staking, airdrop, mining) - creates both income event and cost basis lot."""
        income = IncomeEvent(
            date=tx.date,
            asset=tx.asset,
            amount=tx.amount,
            value_nis=tx.price_nis,
            income_type=income_type,
            notes=tx.notes,
        )
        self.income_events.append(income)

        # Also create a cost basis lot at the income value
        lot = Lot(
            date=tx.date,
            asset=tx.asset,
            amount=tx.amount,
            cost_per_unit_nis=tx.price_per_unit if tx.amount > 0 else 0,
            exchange=tx.exchange,
            notes=f"From {income_type}: {tx.notes}",
        )
        self.lots[tx.asset].append(lot)

    def process_fork(self, tx: Transaction):
        """Process hard fork tokens (zero cost basis)."""
        lot = Lot(
            date=tx.date,
            asset=tx.asset,
            amount=tx.amount,
            cost_per_unit_nis=0,
            exchange=tx.exchange,
            notes=f"Hard fork: {tx.notes}",
        )
        self.lots[tx.asset].append(lot)

    def get_remaining_lots(self) -> dict:
        """Get summary of remaining positions."""
        positions = {}
        for asset, lots in self.lots.items():
            total_amount = sum(lot.amount for lot in lots)
            total_cost = sum(lot.total_cost for lot in lots)
            if total_amount > 1e-10:
                positions[asset] = {
                    "amount": total_amount,
                    "total_cost_nis": total_cost,
                    "avg_cost_per_unit": total_cost / total_amount if total_amount > 0 else 0,
                    "num_lots": len(lots),
                }
        return positions


def process_transactions(transactions: list, year: int, other_income: float = 0.0,
                         other_capital_income: float = 0.0,
                         loss_carryforward: float = 0.0) -> TaxReport:
    """Process all transactions and generate a tax report for the specified year.

    other_income: the taxpayer's NON-crypto taxable income for the year (salary,
    business, etc.). Required to assess mas yesafim correctly, because the surtax
    threshold applies to TOTAL taxable income, not crypto gains alone.
    """
    # Rows built in code (the demo, a caller) carry no file position; give each a
    # unique one so separate sales are never folded into one notice.
    for i, tx in enumerate(transactions):
        if not tx.row:
            tx.row = 1_000_000 + i
    engine = FIFOEngine()
    report = TaxReport(year=year, other_income=other_income,
                       other_capital_income=min(other_capital_income, other_income),
                       loss_carryforward=max(0.0, loss_carryforward))
    unknown_types = []

    for tx in transactions:
        if tx.tx_type in ("buy", "trade_buy"):
            engine.process_buy(tx)
        elif tx.tx_type in ("sell", "trade_sell"):
            engine.process_sell(tx)
        elif tx.tx_type in ("staking", "interest"):
            engine.process_income(tx, tx.tx_type)
        elif tx.tx_type == "airdrop":
            engine.process_income(tx, "airdrop")
        elif tx.tx_type == "mining":
            engine.process_income(tx, "mining")
        elif tx.tx_type == "fork":
            engine.process_fork(tx)
        elif tx.tx_type in ("transfer", "deposit", "withdrawal"):
            pass  # Transfers are not taxable events
        else:
            # NOT a warning. An unrecognised type set (a Hebrew-labelled export, or
            # a typo like "purchase") used to be dropped silently, so a file whose
            # every row was discarded still printed a clean zero-tax report with
            # exit 0 and warnings:[] in JSON. A wholly discarded file is the worst
            # possible confident wrong answer.
            unknown_types.append((tx.date, tx.tx_type))

    if unknown_types:
        kinds = sorted({t for _, t in unknown_types})
        report.warnings.append(
            f"UNRECOGNISED TRANSACTION TYPES: {len(unknown_types)} row(s) using "
            f"{kinds} were NOT processed and contribute nothing to any figure below. "
            f"Recognised types are: buy, trade_buy, sell, trade_sell, staking, "
            f"interest, airdrop, mining, fork, transfer, deposit, withdrawal. "
            f"Hebrew or vendor-specific labels must be mapped to these first. "
            f"A zero result here may simply mean the file was discarded.")
        report.unrecognised_rows = len(unknown_types)

    # Filter events for the specified year
    year_gains = [e for e in engine.gain_events if e.disposal_date.year == year]
    year_income = [e for e in engine.income_events if e.date.year == year]

    report.gain_events = year_gains
    report.income_events = year_income

    # Calculate totals. An UNPRICED event has gain_nis=None and is excluded from
    # every total: an unknown basis must not silently become a zero basis.
    for event in year_gains:
        if event.gain_nis is None:
            continue
        if event.gain_nis >= 0:
            report.total_gains += event.gain_nis
        else:
            report.total_losses += abs(event.gain_nis)

    report.net_gain = report.total_gains - report.total_losses
    report.total_income = sum(e.value_nis for e in year_income)

    report.unpriced = [u for u in engine.unpriced
                       if datetime.strptime(u["disposal_date"], "%Y-%m-%d").year == year]
    if report.unpriced:
        total_unpriced = sum(u["disposal_proceeds_nis"] for u in report.unpriced)
        report.warnings.append(
            f"INCOMPLETE: {len(report.unpriced)} disposal(s) totalling "
            f"{total_unpriced:,.2f} NIS in proceeds have NO matching purchase lot, "
            f"so their cost basis is UNKNOWN. They are EXCLUDED from every total "
            f"below, which means the figures UNDERSTATE the gain. Supply the "
            f"acquisition records, or establish a basis (the earliest available "
            f"market price for the asset) and document it, then re-run. Do not "
            f"file on these numbers.")

    # Calculate tax. A capital loss brought forward (s.92(b), Form 1344) is set
    # against this year's net gain first; only allowed if a return was filed for
    # the loss year, which the user must confirm.
    report.loss_carryforward_used = min(report.loss_carryforward, max(0.0, report.net_gain))
    taxable_gain = max(0.0, report.net_gain) - report.loss_carryforward_used
    report.capital_gains_tax = taxable_gain * INDIVIDUAL_TAX_RATE
    if report.loss_carryforward > 0:
        report.warnings.append(
            f"A brought-forward capital loss of {report.loss_carryforward:,.2f} NIS was "
            f"applied ({report.loss_carryforward_used:,.2f} used this year). s.92(b) "
            f"allows it only if a return was filed for the year the loss arose.")
    # 25% is a CAP, not a flat rate: s.91(b)(1) taxes the real gain "כאמור בסעיף
    # 121, בשיעור שלא יעלה על 25%" as the top layer of income. From age 60 the
    # s.121(b)(1) brackets (10%/14%/20%) apply to all income, so a retiree with
    # modest income can owe less. This tool has no age input.
    if taxable_gain > 0:
        report.warnings.append(
            "25% is the CEILING for an individual (s.91(b)(1)). If the taxpayer is 60 "
            "or over, the s.121(b)(1) lower brackets can make part of the gain cheaper "
            "when total income is modest, and s.91(e)(1) lets a real gain be spread "
            "over up to four tax years. This tool applies 25% throughout.")
    pre_2012 = [e for e in year_gains if e.acquired_pre_2012 and e.gain_nis is not None and e.gain_nis > 0]
    if pre_2012:
        report.warnings.append(
            f"{len(pre_2012)} disposal lot(s) were acquired before 1.1.2012. Under "
            f"s.91(b1) their real gain is split by days: the part up to 31.12.2011 is "
            f"taxed at no more than 20%, the rest at 25%. This tool applies 25% to the "
            f"whole gain, so the tax on these lots is overstated.")
    unused_loss = max(0.0, -report.net_gain) + (report.loss_carryforward - report.loss_carryforward_used)
    if unused_loss > 0 and report.other_capital_income > 0:
        report.warnings.append(
            f"An unused capital loss of {unused_loss:,.2f} NIS (this year's net loss and any "
            f"unused brought-forward loss) can offset other "
            f"capital gains of the year (s.92(a)(1)), but this tool cannot tell capital "
            f"GAINS from dividends, interest or rent inside --other-capital-income, so it "
            f"does not net the loss. The surtax printed is overstated if any of that "
            f"income is a capital gain.")
    # Income events (staking, airdrop, mining, lending interest) are NOT given a
    # tax figure. An earlier version applied a "25% passive floor", which is not
    # a floor at all: income not from personal exertion is taxed under s.121
    # from 31% for an individual under 60 (s.121(a)(1)), interest may be 15%,
    # 25% or marginal under s.125C, and mining is business income. The rate
    # turns on age, other income and classification, which this tool does not
    # know, so it reports the shekel amounts and leaves the rate to the user.
    if report.total_income > 0:
        report.warnings.append(
            f"INCOME EVENTS NOT TAXED IN THE TOTAL: {report.total_income:,.2f} NIS of "
            f"staking/airdrop/mining/interest receipts is income at receipt, and its "
            f"income tax is NOT included in any total. Under s.121 income not from personal "
            f"exertion starts at 31% for an individual under 60 (lower brackets from "
            f"age 60); interest may instead be 15%, 25% or marginal under s.125C; "
            f"mining is business income. Apply the user's own marginal rate.")

    # Surtax, s.121B. The threshold applies to TOTAL taxable income, which this
    # tool only knows if --other-income is supplied. Computed on the supplied
    # total, so the 3% limb includes the user's own salary above the threshold.
    threshold = SURTAX_THRESHOLDS.get(year)
    crypto_income_capital = sum(e.value_nis for e in year_income
                                if e.income_type in CAPITAL_SOURCE_INCOME_TYPES)
    total_taxable = report.other_income + taxable_gain + report.total_income
    capital_source = taxable_gain + crypto_income_capital + report.other_capital_income
    if threshold is None:
        report.surtax_computed = False
        report.surtax_basis = "not computed for this year"
        report.warnings.append(
            f"SURTAX NOT COMPUTED for tax year {year}: this tool carries the "
            f"s.121B thresholds for 2019-2027 only (the 3% limb has existed since "
            f"2017, from a 640,000 base). Establish that year's threshold and rate "
            f"from the Ordinance as it then stood.")
    else:
        report.surtax_base = max(0.0, total_taxable - threshold) * SURTAX_BASE_RATE
        if year >= SURTAX_CAPITAL_LIMB_FIRST_YEAR:
            report.surtax_capital = max(0.0, capital_source - threshold) * SURTAX_CAPITAL_RATE
        else:
            report.surtax_basis = "s.121B(a) 3% only (the 2% limb starts in 2025)"
        report.surtax = report.surtax_base + report.surtax_capital
    if (report.surtax_computed and report.other_income == 0
            and (report.net_gain + report.total_income) > 0):
        report.warnings.append(
            "Surtax (mas yesafim) was assessed on crypto income ALONE because no "
            "--other-income was supplied. The 3% limb applies to TOTAL taxable "
            "income above the threshold, so a salaried user may owe it even when "
            "crypto gains alone are below it. Re-run with --other-income "
            "<salary+other> (and --other-capital-income for any dividends, interest "
            "or rent inside it) for an accurate figure.")
    if crypto_income_capital > 0 and report.surtax_capital > 0:
        report.warnings.append(
            "The 2% capital-source limb counts staking, airdrop and interest receipts "
            "as capital-source income. If that activity is a business, it is s.2(1) "
            "income instead and only the 3% limb applies to it.")

    report.total_tax_estimate = report.capital_gains_tax + report.surtax

    # Advance payments (s.91(d)(1)). One Form 1399י per SALE, gain or loss: the
    # section requires the notice to set out "רווח ההון או הפסד ההון". The advance
    # on a later gain is computed after offsetting capital losses already realised
    # earlier in the same year (the 1399י loss line counts "הפסדי הון השנה"). A
    # later loss does not refund an earlier advance; that is settled in the return.
    # An earlier version listed gains only, lot by lot, and demanded advances on
    # gross gains while ignoring same-year losses.
    disposals = []
    for event in year_gains:
        if event.gain_nis is None:
            continue
        # Fold the FIFO lots of ONE sale (same source row) back into one notice.
        # Keyed on the source row, never on free-text fields, so two separate
        # same-day sales stay two notices.
        if disposals and disposals[-1][0] == event.disposal_row:
            disposals[-1][3] += event.gain_nis
            disposals[-1][4] += event.tax_withheld_nis
        else:
            disposals.append([event.disposal_row, event.disposal_date, event.asset,
                              event.gain_nis, event.tax_withheld_nis, event.exchange])
    # The 1399י loss line counts losses brought forward AND this year's earlier
    # losses, so both reduce a later advance.
    loss_pool = report.loss_carryforward
    israeli_platform_unflagged = False
    for _row, d_date, d_asset, gain, withheld, exchange in disposals:
        due_date = d_date + timedelta(days=ADVANCE_PAYMENT_DAYS)
        if gain <= 0:
            loss_pool += -gain
            report.advance_payments.append(AdvancePayment(
                gain_event_date=d_date, due_date=due_date, gain_nis=gain,
                tax_due_nis=0.0, asset=d_asset, tax_withheld_nis=withheld))
            continue
        used = min(loss_pool, gain)
        loss_pool -= used
        due = max(0.0, (gain - used) * INDIVIDUAL_TAX_RATE - withheld)
        if withheld == 0 and _israeli_platform(exchange):
            israeli_platform_unflagged = True
        report.advance_payments.append(AdvancePayment(
            gain_event_date=d_date, due_date=due_date, gain_nis=gain,
            tax_due_nis=due, asset=d_asset, loss_offset_nis=used,
            tax_withheld_nis=withheld))
    surplus = sum(max(0.0, a.tax_withheld_nis - (a.gain_nis - a.loss_offset_nis) * INDIVIDUAL_TAX_RATE)
                  if a.gain_nis > 0 else a.tax_withheld_nis for a in report.advance_payments)
    report.tax_withheld_total = sum(a.tax_withheld_nis for a in report.advance_payments)
    if surplus > 0:
        report.warnings.append(
            f"{surplus:,.2f} NIS withheld at source exceeds the advance due on those sales "
            f"(or was withheld on a loss sale). It is not lost: credit it in the annual return.")
    by_day = defaultdict(set)
    for _row, d_date, _a, gain, _w, _e in disposals:
        by_day[d_date].add(gain > 0)
    if any(len(kinds) == 2 for kinds in by_day.values()):
        report.warnings.append(
            "On at least one day there are both a gain sale and a loss sale. Rows carry "
            "no time, so the tool processes them in file order, and that order decides "
            "which advance absorbs the loss. Put same-day rows in the order executed, or "
            "use the 1399י monthly-aggregation route, which nets a month's trades.")
    buys_by_day = defaultdict(set)
    for tx in transactions:
        if tx.tx_type in ("buy", "trade_buy") and tx.amount > 0:
            buys_by_day[(tx.date, tx.asset)].add(round(tx.cost_per_unit, 6))
    if any(len(v) > 1 for v in buys_by_day.values()):
        report.warnings.append(
            "Several acquisitions of one asset on one day at different unit costs. FIFO "
            "follows file order within the day; if the export is newest-first, reverse "
            "those rows so they appear in the order executed, or the basis is mismatched.")
    if israeli_platform_unflagged:
        report.warnings.append(
            "Some sales were made on an Israeli platform with no tax_withheld_nis "
            "recorded. Ask the platform whether it withheld tax at source; if it did, "
            "enter the amount in a tax_withheld_nis column so no second advance is "
            "demanded for the same sale.")

    report.remaining_lots = engine.get_remaining_lots()
    return report


# ============================================================
# Output Formatters
# ============================================================

FILING_DISCLAIMER = ("ESTIMATE for your own preparation only: not a filed Form 1399י, "
                     "not tax advice. The binding computation is the Tax Authority's; "
                     "verify with a tax adviser or CPA before filing or paying.")


def _report_tail(report: TaxReport) -> list:
    """Warnings and disclaimer, shared by the complete and incomplete branches."""
    tail = []
    if report.warnings:
        tail.extend(["", "-" * 70, "WARNINGS", "-" * 70])
        for w in report.warnings:
            tail.append(f"  ! {w}")
    tail.extend(["", "-" * 70,
                 "This is an ESTIMATE, not tax advice. Verify with a CPA before filing.",
                 "-" * 70])
    return tail


def format_report(report: TaxReport) -> str:
    lines = [
        "=" * 70,
        f"ISRAELI CRYPTO TAX REPORT - TAX YEAR {report.year}",
        "=" * 70,
        "",
    ]

    # Capital Gains Section
    lines.extend([
        "-" * 70,
        "CAPITAL GAINS DISPOSAL SCHEDULE",
        "-" * 70,
    ])

    if report.gain_events:
        for i, event in enumerate(report.gain_events, 1):
            gain_str = ("UNPRICED" if event.gain_nis is None
                        else (f"+{event.gain_nis:,.2f}" if event.gain_nis >= 0
                              else f"{event.gain_nis:,.2f}"))
            # NOT a US-style long/short-term rate distinction: the Israeli rate is
            # 25% either way. The label only flags whether the inflationary split
            # is likely to matter.
            term = "OVER 1Y" if event.is_long_term else "UNDER 1Y"
            acquired = (event.acquisition_date.strftime('%Y-%m-%d')
                        if event.acquisition_date else "UNKNOWN")
            lines.extend([
                f"\n  Event #{i}:",
                f"    Asset:              {event.asset}",
                f"    Amount:             {event.amount:.8f}",
                f"    Acquired:           {acquired}",
                f"    Disposed:           {event.disposal_date.strftime('%Y-%m-%d')}",
                f"    Holding period:     " + (
                    "UNKNOWN" if event.holding_days is None
                    else f"{event.holding_days} days ({term}-term)"),
                f"    Acquisition cost:   " + (
                    "UNKNOWN, no matching purchase lot"
                    if event.acquisition_cost_nis is None
                    else f"{event.acquisition_cost_nis:,.2f} NIS"),
                f"    Disposal proceeds:  {event.disposal_proceeds_nis:,.2f} NIS",
                f"    Gain/Loss:          {gain_str} NIS",
            ])
            if event.notes:
                lines.append(f"    Notes:              {event.notes}")
    else:
        lines.append("  No capital gain events for this year.")

    # Income Section
    lines.extend([
        "",
        "-" * 70,
        "INCOME EVENTS (Staking, Airdrops, Mining)",
        "-" * 70,
    ])

    if report.income_events:
        for i, event in enumerate(report.income_events, 1):
            lines.extend([
                f"\n  Income #{i}:",
                f"    Date:     {event.date.strftime('%Y-%m-%d')}",
                f"    Type:     {event.income_type}",
                f"    Asset:    {event.asset}",
                f"    Amount:   {event.amount:.8f}",
                f"    Value:    {event.value_nis:,.2f} NIS",
            ])
    else:
        lines.append("  No income events for this year.")

    # Summary
    lines.extend([
        "",
        "-" * 70,
        "TAX SUMMARY",
        "-" * 70,
    ])

    # A total that EXCLUDES unpriced disposals looks complete and is low, and a
    # taxpayer signs his own return: a plausible low number gets filed, a blank
    # does not. So suppress every summary figure while any disposal is unpriced
    # or any row was not recognised, and show the priced part clearly labelled as
    # a partial. The worst case is not the wholly-unpriced file, it is nine good
    # disposals plus one unpriced, which would otherwise print a nine-tenths
    # total that no reviewer would query.
    incomplete = bool(report.unpriced) or bool(report.unrecognised_rows)
    if incomplete:
        reasons = []
        if report.unpriced:
            reasons.append(f"{len(report.unpriced)} disposal(s) unpriced")
        if report.unrecognised_rows:
            reasons.append(f"{report.unrecognised_rows} row(s) unrecognised")
        lines.extend([
            f"  NET CAPITAL GAIN:           NOT COMPUTABLE",
            f"  TOTAL ESTIMATED TAX:        NOT COMPUTABLE",
            f"  Reason: {', '.join(reasons)}. See WARNINGS below.",
            "",
            f"  Priced portion only, NOT a filing figure:",
            f"    gains {report.total_gains:,.2f} / losses {report.total_losses:,.2f} "
            f"/ net {report.net_gain:,.2f} NIS",
        ])
        return "\n".join(lines + _report_tail(report))

    lines.extend([
        f"  Total capital gains:        {report.total_gains:>15,.2f} NIS",
        f"  Total capital losses:       {report.total_losses:>15,.2f} NIS",
        f"  Net capital gain:           {report.net_gain:>15,.2f} NIS",
        f"  Loss brought forward used:  {report.loss_carryforward_used:>15,.2f} NIS",
        f"  Tax withheld at source:     {report.tax_withheld_total:>15,.2f} NIS  (credit it in the return)",
        f"  Crypto income at receipt:   {report.total_income:>15,.2f} NIS  (tax NOT included, see WARNINGS)",
        "",
        f"  Capital gains tax (25%):    {report.capital_gains_tax:>15,.2f} NIS",
    ])

    if report.other_income > 0:
        lines.append(f"  (Other income for surtax:   {report.other_income:>15,.2f} NIS)")

    if not report.surtax_computed:
        lines.append(f"  Surtax:                     NOT COMPUTED for {report.year}")
    elif report.surtax > 0:
        lines.append(f"  Surtax 3%, s.121B(a):       {report.surtax_base:>15,.2f} NIS")
        if report.year >= SURTAX_CAPITAL_LIMB_FIRST_YEAR:
            lines.append(f"  Surtax 2%, s.121B(a1):      {report.surtax_capital:>15,.2f} NIS")

    lines.extend([
        f"  -----------------------------------------",
        f"  TOTAL ESTIMATED TAX:        {report.total_tax_estimate:>15,.2f} NIS",
        f"  (capital-gains tax + surtax on the supplied income; income-event tax excluded)",
    ])

    # Inflation-indexation warning: this calculator taxes the WHOLE gain at 25%
    # and does not split out the inflation component (sechum hatzmada) under
    # Sections 88 and 91(c). NOTE: 91(c) taxes the CHARGEABLE inflationary amount
    # at 10%; it comes out nil for crypto only because s.88 confines the chargeable
    # part to gain that would have arisen by 31.12.1993. 91(b)(3) is NOT this rule
    # (it is the non-index-linked bond rate) and must not be cited for it. Acquired
    # after 1.1.1994. For lots held over ~12 months in inflationary periods, the
    # figure above OVERSTATES the real tax. Flag the affected events explicitly.
    long_held_gains = [e for e in report.gain_events
                       if e.is_long_term and e.gain_nis is not None and e.gain_nis > 0]
    if long_held_gains:
        lines.extend([
            "",
            "  ! INFLATION-INDEXATION NOTICE (Sections 88 and 91(c)):",
            f"    {len(long_held_gains)} gain event(s) were held 12+ months. This tool",
            "    taxes the full gain at 25% and does NOT split out the inflationary",
            "    amount, which s.91(c) charges at 10% but which is nil for crypto",
            "    (s.88 confines the chargeable part to gain accrued by 31.12.1993).",
            "    The tax above is therefore an UPPER bound for these lots.",
            "    Apply a manual indexation pass or have a CPA review before filing.",
        ])

    # Remaining positions
    if report.remaining_lots:
        lines.extend([
            "",
            "-" * 70,
            "REMAINING POSITIONS (Cost Basis)",
            "-" * 70,
        ])
        for asset, pos in sorted(report.remaining_lots.items()):
            lines.extend([
                f"  {asset}:",
                f"    Amount:          {pos['amount']:.8f}",
                f"    Total cost:      {pos['total_cost_nis']:,.2f} NIS",
                f"    Avg cost/unit:   {pos['avg_cost_per_unit']:,.2f} NIS",
                f"    Lots:            {pos['num_lots']}",
            ])

    if report.warnings:
        lines.extend([
            "",
            "-" * 70,
            "WARNINGS (read before relying on the figures above)",
            "-" * 70,
        ])
        for w in report.warnings:
            lines.append(f"  ! {w}")

    lines.extend([
        "",
        "=" * 70,
        "DISCLAIMER: This report is for informational purposes only.",
        "Consult a licensed Israeli tax advisor for official tax filing.",
        "Rates and thresholds are based on 2026 regulations (surtax threshold frozen through 2027).",
        "=" * 70,
    ])

    return "\n".join(lines)


def format_disposal_schedule(report: TaxReport) -> str:
    """Disposal schedule in the Form 1399י columns: the working paper behind the filing."""
    lines = [
        "=" * 80,
        f"CAPITAL GAINS DISPOSAL SCHEDULE - TAX YEAR {report.year}",
        "Columns match Form 1399י (הודעה על מכירת נכס). This is NOT an ITA form:",
        "Forms 1322/1325 are ITA securities forms and do not carry a crypto",
        "disposal. Use this as the working paper behind your 1399י notices.",
        "=" * 80,
        "",
        f"{'#':>3} | {'Asset':<8} | {'Acquired':<12} | {'Disposed':<12} | "
        f"{'Cost (NIS)':>14} | {'Proceeds (NIS)':>14} | {'Gain/Loss (NIS)':>16}",
        "-" * 95,
    ]

    for i, event in enumerate(report.gain_events, 1):
        gain_str = (f"{'UNPRICED':>16}" if event.gain_nis is None
                    else f"{event.gain_nis:>16,.2f}")
        acquired = (event.acquisition_date.strftime('%d/%m/%Y')
                    if event.acquisition_date else "UNKNOWN")
        cost = (f"{'UNKNOWN':>14}" if event.acquisition_cost_nis is None
                else f"{event.acquisition_cost_nis:>14,.2f}")
        lines.append(
            f"{i:>3} | {event.asset:<8} | {acquired:<12} | "
            f"{event.disposal_date.strftime('%d/%m/%Y'):<12} | "
            f"{cost} | {event.disposal_proceeds_nis:>14,.2f} | {gain_str}"
        )

    lines.extend([
        "-" * 95,
        f"{'':>3}   {'TOTAL':<8}   {'':12}   {'':12}   "
        f"{'':>14}   {'':>14}   {report.net_gain:>16,.2f}",
        "",
        f"Total capital gains tax (25%, after {report.loss_carryforward_used:,.2f} NIS of "
        f"brought-forward loss): {report.capital_gains_tax:,.2f} NIS",
    ])

    if report.surtax > 0:
        lines.append(f"Surtax (s.121B, on the supplied total income): {report.surtax:,.2f} NIS, "
                     f"settled in the annual return, never in the 30-day advance")
    lines.extend(["", FILING_DISCLAIMER])

    return "\n".join(lines)


def format_advance_payments(report: TaxReport) -> str:
    """Format advance payment schedule."""
    lines = [
        "=" * 70,
        f"ADVANCE PAYMENT SCHEDULE (Mikdamot) - {report.year}",
        "=" * 70,
        "",
        f"{'#':>3} | {'Sale Date':<12} | {'Notice Due':<12} | {'Asset':<8} | "
        f"{'Gain/Loss (NIS)':>15} | {'Loss Offset':>12} | {'Withheld':>10} | {'Advance (NIS)':>14}",
        "-" * 105,
    ]

    total_advance = 0
    for i, payment in enumerate(report.advance_payments, 1):
        lines.append(
            f"{i:>3} | {payment.gain_event_date.strftime('%d/%m/%Y'):<12} | "
            f"{payment.due_date.strftime('%d/%m/%Y'):<12} | {payment.asset:<8} | "
            f"{payment.gain_nis:>15,.2f} | {payment.loss_offset_nis:>12,.2f} | "
            f"{payment.tax_withheld_nis:>10,.2f} | {payment.tax_due_nis:>14,.2f}"
        )
        total_advance += payment.tax_due_nis

    lines.extend([
        "-" * 105,
        f"{'':>3}   {'':12}   {'':12}   {'TOTAL':8}   {'':>15}   {'':>12}   {'':>10}   {total_advance:>14,.2f}",
        "",
        "NOTE: s.91(d)(1) requires a Form 1399yod notice within 30 days of EVERY",
        "sale, a sale at a loss included. The advance is 25% of the gain after",
        "offsetting losses brought forward and losses realised earlier in the same",
        "year, less any tax an Israeli platform withheld on that sale. A later loss",
        "does not refund an earlier advance (that is settled in the annual return).",
        "Virtual currency: transaction code 77 with code 71. One month's trades may",
        "be reported as one transaction with a weighted-average acquisition date",
        "and an attached working paper. Form 1399het is the company equivalent.",
        "The surtax is NOT part of the advance (s.121B(b)). Late payment accrues",
        "interest and linkage differences from day 30.",
        "",
        FILING_DISCLAIMER,
    ])

    return "\n".join(lines)


def format_json(report: TaxReport) -> str:
    """Format report as JSON."""
    data = {
        "tax_year": report.year,
        "summary": {
            "total_gains_nis": round(report.total_gains, 2),
            "total_losses_nis": round(report.total_losses, 2),
            "net_gain_nis": round(report.net_gain, 2),
            "total_income_nis": round(report.total_income, 2),
            "capital_gains_tax_nis": round(report.capital_gains_tax, 2),
            "income_events_tax_included": False,
            "loss_carryforward_used_nis": round(report.loss_carryforward_used, 2),
            "tax_withheld_total_nis": round(report.tax_withheld_total, 2),
            "surtax_nis": round(report.surtax, 2),
            "surtax_3pct_limb_nis": round(report.surtax_base, 2),
            "surtax_2pct_capital_limb_nis": round(report.surtax_capital, 2),
            "surtax_computed": report.surtax_computed,
            "other_income_nis": round(report.other_income, 2),
            "total_tax_estimate_nis": round(report.total_tax_estimate, 2),
        },
        "advance_notices": [
            {
                "sale_date": a.gain_event_date.strftime("%Y-%m-%d"),
                "notice_due": a.due_date.strftime("%Y-%m-%d"),
                "asset": a.asset,
                "gain_nis": round(a.gain_nis, 2),
                "loss_offset_nis": round(a.loss_offset_nis, 2),
                "tax_withheld_nis": round(a.tax_withheld_nis, 2),
                "advance_nis": round(a.tax_due_nis, 2),
            }
            for a in report.advance_payments
        ],
        "warnings": report.warnings,
        "disclaimer": FILING_DISCLAIMER,
        "unpriced_disposals": report.unpriced,
        "unrecognised_rows": report.unrecognised_rows,
        "complete": not report.unpriced and not report.unrecognised_rows,
        "gain_events": [
            {
                "asset": e.asset,
                "amount": e.amount,
                "acquisition_date": (e.acquisition_date.strftime("%Y-%m-%d")
                                     if e.acquisition_date else None),
                "disposal_date": e.disposal_date.strftime("%Y-%m-%d"),
                "acquisition_cost_nis": (None if e.acquisition_cost_nis is None
                                         else round(e.acquisition_cost_nis, 2)),
                "disposal_proceeds_nis": round(e.disposal_proceeds_nis, 2),
                "gain_nis": None if e.gain_nis is None else round(e.gain_nis, 2),
                "holding_days": e.holding_days,
                "is_long_term": e.is_long_term,
            }
            for e in report.gain_events
        ],
        "income_events": [
            {
                "date": e.date.strftime("%Y-%m-%d"),
                "type": e.income_type,
                "asset": e.asset,
                "amount": e.amount,
                "value_nis": round(e.value_nis, 2),
            }
            for e in report.income_events
        ],
        "remaining_positions": {
            asset: {
                "amount": round(pos["amount"], 8),
                "total_cost_nis": round(pos["total_cost_nis"], 2),
                "avg_cost_per_unit_nis": round(pos["avg_cost_per_unit"], 2),
            }
            for asset, pos in report.remaining_lots.items()
        },
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ============================================================
# Demo Data
# ============================================================

DEMO_TRANSACTIONS = [
    Transaction(datetime(2024, 1, 15), "buy", "BTC", 0.5, 75000, 375, "bits-of-gold", "Initial BTC purchase"),
    Transaction(datetime(2024, 2, 1), "buy", "ETH", 5.0, 40000, 200, "bit2c", "ETH investment"),
    Transaction(datetime(2024, 3, 10), "buy", "BTC", 0.3, 48000, 240, "binance", "Additional BTC"),
    Transaction(datetime(2024, 4, 15), "staking", "ETH", 0.25, 2200, 0, "defi-protocol", "Q1 staking rewards"),
    Transaction(datetime(2024, 5, 20), "airdrop", "ARB", 500, 2500, 0, "arbitrum", "Airdrop claim"),
    Transaction(datetime(2024, 6, 1), "sell", "BTC", 0.4, 68000, 340, "bits-of-gold", "Partial BTC sale"),
    Transaction(datetime(2024, 7, 15), "sell", "ETH", 3.0, 30000, 150, "bit2c", "Partial ETH sale"),
    Transaction(datetime(2024, 8, 1), "buy", "SOL", 20, 4000, 20, "binance", "SOL purchase"),
    Transaction(datetime(2024, 9, 10), "sell", "ARB", 300, 1800, 9, "binance", "Partial airdrop sale"),
    Transaction(datetime(2024, 10, 1), "staking", "ETH", 0.15, 1500, 0, "defi-protocol", "Q3 staking rewards"),
    Transaction(datetime(2024, 11, 15), "sell", "SOL", 10, 3000, 15, "binance", "Partial SOL sale"),
]


def run_demo():
    """Run a demo with sample transactions."""
    print("Running demo with sample Israeli crypto transactions...")
    print(f"Processing {len(DEMO_TRANSACTIONS)} transactions for 2024\n")

    report = process_transactions(DEMO_TRANSACTIONS, 2024)
    print(format_report(report))
    print()
    print(format_disposal_schedule(report))
    print()
    print(format_advance_payments(report))


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Israeli Crypto Capital Gains Calculator (FIFO)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format:
  date,type,asset,amount,price_nis,fee_nis,exchange,notes
  2024-01-15,buy,BTC,0.5,75000,375,bits-of-gold,Initial purchase
  2024-08-20,sell,BTC,0.3,51000,255,bits-of-gold,Partial sale

Transaction types:
  buy         Purchase of crypto with fiat
  sell        Sale of crypto for fiat
  trade_buy   Crypto received in a crypto-to-crypto trade
  trade_sell  Crypto given in a crypto-to-crypto trade
  staking     Staking reward received
  airdrop     Airdrop tokens received
  mining      Mining reward received
  interest    Lending interest received
  fork        Hard fork tokens received (zero cost basis)
  transfer    Wallet/exchange transfer (not taxable, tracking only)
  deposit     Same as transfer
  withdrawal  Same as transfer

price_nis and fee_nis must already be in SHEKELS. Convert USD/USDT legs first.
Dates are YYYY-MM-DD; numbers carry no thousands separator. A row that cannot
be parsed stops the run. Optional column tax_withheld_nis: tax an Israeli
platform withheld on that sale. Rows have no time: within one day the tool
processes acquisitions before disposals, and otherwise keeps file order, so put
same-day rows in the order executed.

Examples:
  %(prog)s --input trades.csv --year 2024
  %(prog)s --input trades.csv --year 2024 --schedule
  %(prog)s --input trades.csv --year 2024 --advance-payments
  %(prog)s --input trades.csv --year 2024 --json
  %(prog)s --demo
        """,
    )

    parser.add_argument("--input", "-i", help="Path to CSV file with transactions")
    parser.add_argument("--year", "-y", type=int, help="Tax year to report on")
    parser.add_argument("--schedule", "--form-1325", dest="schedule",
                        action="store_true",
                        help="Print the capital-gains disposal schedule (columns "
                             "match Form 1399י). --form-1325 is kept as a "
                             "deprecated alias; the output is NOT an ITA form 1325.")
    parser.add_argument("--advance-payments", action="store_true", help="Generate advance payment schedule")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--ignore-data-errors", action="store_true",
                        help="Compute anyway despite data-quality problems "
                             "(negative or zero amounts, impossible dates). The "
                             "problems are carried into the report warnings and "
                             "the exit code is still non-zero.")
    parser.add_argument("--other-income", type=float, default=0.0,
                        help="Non-crypto taxable income for the year (salary, business). "
                             "Required for an accurate surtax (mas yesafim) assessment, "
                             "since the threshold applies to TOTAL taxable income.")
    parser.add_argument("--loss-carryforward", type=float, default=0.0,
                        help="Capital loss brought forward from earlier years (Form 1344). "
                             "Only usable if a return was filed for the loss year (s.92(b)).")
    parser.add_argument("--other-capital-income", type=float, default=0.0,
                        help="The part of --other-income that is capital-source "
                             "(dividends, interest, rent, non-crypto capital gains). "
                             "Counts toward the s.121B(a1) 2%% limb.")

    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if not args.input or not args.year:
        parser.error("--input and --year are required (or use --demo)")

    transactions, row_errors = parse_csv(args.input)
    if not transactions and not row_errors:
        print("No valid transactions found in the input file.", file=sys.stderr)
        sys.exit(1)

    problems = row_errors + validate_transactions(transactions)
    if problems and not args.ignore_data_errors:
        print("Refusing to compute: the input has data-quality problems that would "
              "produce a confident wrong answer.", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("Fix the input, or re-run with --ignore-data-errors to compute anyway "
              "(the problems are then carried into the report's warnings).",
              file=sys.stderr)
        sys.exit(2)

    print(f"Loaded {len(transactions)} transactions.", file=sys.stderr)

    if args.other_income < 0 or args.other_capital_income < 0 or args.loss_carryforward < 0:
        parser.error("--other-income, --other-capital-income and --loss-carryforward cannot be negative")
    if args.other_capital_income > args.other_income:
        parser.error("--other-capital-income is a PART of --other-income and cannot exceed it")
    report = process_transactions(transactions, args.year, other_income=args.other_income,
                                  other_capital_income=args.other_capital_income,
                                  loss_carryforward=args.loss_carryforward)
    for p in problems:
        report.warnings.append(f"DATA QUALITY (overridden): {p}")
    # A row that could not be parsed contributes nothing to any figure, so the
    # report is incomplete exactly like an unrecognised row.
    report.unrecognised_rows += len(row_errors)

    in_year = [t for t in transactions if t.date.year == args.year]
    if not in_year:
        report.warnings.append(
            f"No transaction in the file falls in tax year {args.year}. The file "
            f"spans {min(t.date for t in transactions):%Y-%m-%d} to "
            f"{max(t.date for t in transactions):%Y-%m-%d}. A zero result here means "
            f"'nothing in this year', not 'no tax due'.")

    if args.json:
        print(format_json(report))
    elif (args.schedule or args.advance_payments) and (report.unpriced or report.unrecognised_rows):
        print("Refusing to emit a filing artefact from an incomplete report.",
              file=sys.stderr)
        for w in report.warnings:
            print(f"  ! {w}", file=sys.stderr)
        print("Resolve the above, then re-run. The full report (no flags) still "
              "prints the per-event schedule for inspection.", file=sys.stderr)
    elif args.schedule or args.advance_payments:
        # Compose rather than shadow. An earlier version's elif chain silently
        # dropped the advance schedule whenever --form-1325 was also passed, and
        # the suppressed output was the time-critical one (the 30-day notice).
        if args.schedule:
            print(format_disposal_schedule(report))
        if args.advance_payments:
            print(format_advance_payments(report))
        if report.warnings:
            print("\n" + "-" * 70)
            print("WARNINGS")
            print("-" * 70)
            for w in report.warnings:
                print(f"  ! {w}")
    else:
        print(format_report(report))

    # A report that excludes unpriced disposals, or that was computed over
    # overridden data errors, is NOT a clean run. Exit non-zero so a calling
    # agent cannot mistake it for one.
    if (report.unpriced or report.unrecognised_rows
            or (problems and args.ignore_data_errors) or not in_year):
        sys.exit(3)


if __name__ == "__main__":
    main()
