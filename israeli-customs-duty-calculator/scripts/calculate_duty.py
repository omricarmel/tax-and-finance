#!/usr/bin/env python3
"""
calculate_duty.py - Israeli landed-cost calculator.

Computes the cascading tax sequence used by Israeli Customs:
  CIF -> customs duty -> purchase tax -> VAT -> landed cost.

Constants:
  - Israel VAT rate: 18% (since January 1, 2025).
  - Personal import threshold: USD 75 (re-verified 18 October 2026). The threshold
    moved 75 -> 150 in December 2025, was revoked back to 75 by the
    Knesset on 24 February 2026, was reset to 130 by a new Finance
    Ministry order effective 25 February 2026, and reverted to 75 when
    the Knesset revoked that order too at the start of June 2026. It has moved four times
    in seven months; confirm via the official calculator before quoting.
  - Two different bases: the exemption THRESHOLD is tested on the goods
    value alone (excluding shipping and insurance), while the TAX is computed
    on the CIF value plus any duty and purchase tax.
  - FX: customs converts foreign-currency prices at the Bank of Israel
    REPRESENTATIVE rate plus 0.5%. Pass the representative rate in --fx; this
    script applies the 0.5% uplift itself and prints both rates. Do not
    pre-multiply, or the uplift is counted twice.
  - Purchase tax is levied on a reconstructed WHOLESALE price, which adds a
    statutory per-tariff-item uplift (TAMA) on top of CIF plus duty. That
    uplift is NOT modelled here and its rates are not published in a form this
    script can consume, so the purchase-tax line is a FLOOR, not the charge.
    Whenever --purchase-tax-rate is non-zero the output says so.
  - Two conversions: the TAX BASE (CIF) uses the customs rate, the representative
    rate x 1.005; the goods and freight in the landed total use the plain
    representative rate, since that is closer to what the buyer pays the seller.
    An ILS-priced invoice is not converted and gets no uplift.
  - --combined-rate takes the single all-in percentage shown by the Tax Authority
    personal-import calculator. It already includes VAT (and duty and purchase
    tax where they apply) and is applied once to goods + shipping + insurance.
  - With --personal, the USD 75-500 duty waiver IS enforced (cascade route only): a non-zero
    --duty-rate is set to 0 in that band and the output says so.
  - Tobacco products and alcoholic beverages are EXCLUDED
    from the personal-import exemption regardless of value. The script
    cannot recognise them from the inputs: pass --excluded-goods, which
    skips the exemption and the duty waiver.

Sources for each constant are cited in the skill's evidence.json.

Usage:
  python3 calculate_duty.py --value 200 --shipping 20 --insurance 5 \\
      --currency USD --fx 3.65 \\
      --duty-rate 0 --purchase-tax-rate 0 \\
      --personal

Exit 0 on success.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

# Constants grounded in evidence.json
PERSONAL_IMPORT_DUTY_WAIVER_CEILING_USD = Decimal("500")
VAT_RATE = Decimal("0.18")
PERSONAL_IMPORT_THRESHOLD_USD = Decimal("75")
# Customs converts at the BoI representative rate plus 0.5%.
CUSTOMS_FX_UPLIFT = Decimal("1.005")


def decimal_arg(raw: str) -> Decimal:
    """argparse type that rejects non-numeric input with a readable message."""
    try:
        return Decimal(raw)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"{raw!r} is not a number")


def money(x: Decimal) -> Decimal:
    """Round to 2 decimal places, banker's rounding is avoided for clarity."""
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_landed_cost(
    product_value: Decimal,
    shipping: Decimal,
    insurance: Decimal,
    fx_rate: Decimal,
    duty_rate: Decimal,
    purchase_tax_rate: Decimal,
    broker_fees_ils: Decimal,
    currency: str,
    personal_import: bool,
    usd_value: Decimal = None,
    excluded_goods: bool = False,
    combined_rate: Optional[Decimal] = None,
) -> dict:
    """Compute full landed cost breakdown. All outputs are in ILS."""
    # The uplift is applied HERE and nowhere else. fx_rate is the Bank of
    # Israel representative rate as published; customs_fx is what customs uses.
    # An invoice already priced in ILS is not converted, so there is no uplift.
    boi_rate = fx_rate
    customs_fx = fx_rate if currency.upper() == "ILS" else fx_rate * CUSTOMS_FX_UPLIFT
    # Personal-import threshold check. The threshold is denominated in USD and
    # tested on the goods value alone, excluding shipping and insurance. For a
    # non-USD invoice the caller must supply the USD equivalent, otherwise the
    # exemption cannot be evaluated and the goods would be silently taxed.
    goods_usd = product_value if currency.upper() == "USD" else usd_value
    duty_waived = False
    if personal_import and goods_usd is None and not excluded_goods:
        raise ValueError(
            f"--personal with a {currency.upper()} invoice requires --usd-value: "
            "the exemption threshold is denominated in USD and cannot be applied "
            "without the USD equivalent of the goods value."
        )
    if personal_import and excluded_goods:
        pass  # tobacco and alcohol never qualify; fall through to the taxed path
    elif personal_import and goods_usd is not None:
        # "up to 75 dollars" is inclusive of 75.
        if goods_usd <= PERSONAL_IMPORT_THRESHOLD_USD:
            return {
                "exempt": True,
                "reason": f"Goods value {goods_usd} USD is at or below the personal import threshold of {PERSONAL_IMPORT_THRESHOLD_USD} USD.",
                "cif_ils": money((product_value + shipping + insurance) * boi_rate),
                "duty_ils": Decimal("0.00"),
                "purchase_tax_ils": Decimal("0.00"),
                "vat_ils": Decimal("0.00"),
                "broker_fees_ils": money(broker_fees_ils),
                "landed_cost_ils": money((product_value + shipping + insurance) * boi_rate + broker_fees_ils),
            }

    # Under the personal-import regime customs duty is waived between the
    # threshold and USD 500; only VAT (and purchase tax where the goods carry
    # it) applies. Enforce it rather than trusting the caller to pass 0.
    if (
        personal_import
        and not excluded_goods
        and goods_usd is not None
        and goods_usd <= PERSONAL_IMPORT_DUTY_WAIVER_CEILING_USD
        and duty_rate > 0
    ):
        duty_rate = Decimal("0")
        duty_waived = True

    # CIF in ILS. cif_ils (customs rate) is the TAX BASE only. What the buyer
    # actually pays for the goods and freight is converted at the plain
    # representative rate; putting the uplift on the goods themselves would
    # overstate every total by 0.5 percent of CIF.
    cif_foreign = product_value + shipping + insurance
    cif_ils = cif_foreign * customs_fx
    goods_outlay_ils = cif_foreign * boi_rate

    if combined_rate is not None:
        # The Tax Authority personal-import calculator publishes ONE all-in
        # percentage per item (VAT included, plus duty and purchase tax where
        # they apply). It is applied once to goods + shipping + insurance.
        duty = Decimal("0")
        purchase_tax = Decimal("0")
        vat = Decimal("0")
        combined_tax = cif_ils * combined_rate
    else:
        # Cascading calculation
        duty = cif_ils * duty_rate
        base_after_duty = cif_ils + duty
        purchase_tax = base_after_duty * purchase_tax_rate
        base_for_vat = base_after_duty + purchase_tax
        vat = base_for_vat * VAT_RATE
        combined_tax = None

    total_tax = combined_tax if combined_tax is not None else duty + purchase_tax + vat
    landed = goods_outlay_ils + total_tax + broker_fees_ils

    return {
        "exempt": False,
        "duty_waived_personal_import": duty_waived,
        "cif_ils": money(cif_ils),
        "goods_outlay_ils": money(goods_outlay_ils),
        "duty_ils": money(duty),
        "purchase_tax_ils": money(purchase_tax),
        "vat_ils": money(vat),
        "combined_tax_ils": money(combined_tax) if combined_tax is not None else None,
        "total_tax_ils": money(total_tax),
        "broker_fees_ils": money(broker_fees_ils),
        "landed_cost_ils": money(landed),
        "purchase_tax_is_floor": combined_rate is None and purchase_tax_rate > 0,
        "combined_in_duty_waiver_band": bool(
            combined_rate is not None and personal_import and not excluded_goods
            and goods_usd is not None
            and PERSONAL_IMPORT_THRESHOLD_USD < goods_usd <= PERSONAL_IMPORT_DUTY_WAIVER_CEILING_USD
        ),
        "inputs": {
            "product_value_foreign": str(product_value),
            "shipping_foreign": str(shipping),
            "insurance_foreign": str(insurance),
            "currency": currency.upper(),
            "boi_representative_rate": str(boi_rate),
            "customs_fx_rate": str(customs_fx),
            "combined_rate": str(combined_rate) if combined_rate is not None else None,
            "duty_rate": str(duty_rate),
            "purchase_tax_rate": str(purchase_tax_rate),
            "vat_rate": str(VAT_RATE),
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Israeli landed-cost calculator (customs + purchase tax + VAT).",
    )
    p.add_argument("--value", type=decimal_arg, required=True, help="Product value in the invoice currency.")
    p.add_argument("--shipping", type=decimal_arg, default=Decimal("0"), help="Freight cost in invoice currency.")
    p.add_argument("--insurance", type=decimal_arg, default=Decimal("0"), help="Insurance cost in invoice currency.")
    p.add_argument("--currency", type=str, default="USD", help="Invoice currency (USD, EUR, GBP, etc.).")
    p.add_argument("--fx", type=decimal_arg, required=True, help="Bank of Israel REPRESENTATIVE rate, foreign currency to ILS. The script adds the 0.5 percent customs uplift itself; do not pre-multiply.")
    p.add_argument("--duty-rate", type=decimal_arg, default=Decimal("0"), help="Customs duty rate as decimal (0.08 = 8 percent).")
    p.add_argument("--purchase-tax-rate", type=decimal_arg, default=Decimal("0"), help="Purchase tax rate as decimal. Ad valorem only. Alcohol, tobacco and much food, textile and footwear are on specific or compound rates this script cannot price. The resulting line also omits the wholesale-price uplift and is therefore a floor.")
    p.add_argument("--combined-rate", type=decimal_arg, default=None, help="The single all-in percentage the Tax Authority personal-import calculator shows for the item, as a decimal (0.4066 = 40.66 percent). It already INCLUDES VAT, and duty and purchase tax where they apply, and is applied once to goods + shipping + insurance. Use it instead of --duty-rate and --purchase-tax-rate, never together with them.")
    p.add_argument("--broker-fees-ils", type=decimal_arg, default=Decimal("0"), help="Broker and handling fees in ILS.")
    p.add_argument("--personal", action="store_true", help="Personal import (applies the USD threshold exemption).")
    p.add_argument("--usd-value", type=decimal_arg, default=None, help="Goods value in USD. Required with --personal when the invoice is not in USD.")
    p.add_argument("--excluded-goods", action="store_true", help="Tobacco, cigarettes or alcoholic beverages: never exempt, taxed from the first shekel.")
    p.add_argument("--json", action="store_true", help="Output as JSON.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.fx <= 0:
        print("Error: --fx must be greater than 0.", file=sys.stderr)
        return 1
    for name, val in (("--value", args.value), ("--shipping", args.shipping),
                      ("--insurance", args.insurance), ("--broker-fees-ils", args.broker_fees_ils)):
        if val < 0:
            print(f"Error: {name} cannot be negative.", file=sys.stderr)
            return 1
    if args.usd_value is not None and args.usd_value < 0:
        print("Error: --usd-value cannot be negative.", file=sys.stderr)
        return 1
    if args.currency.upper() == "ILS" and args.fx != 1:
        print("Error: an ILS invoice needs no conversion; pass --fx 1.", file=sys.stderr)
        return 1
    for name, val in (("--duty-rate", args.duty_rate), ("--purchase-tax-rate", args.purchase_tax_rate)):
        if val < 0:
            print(f"Error: {name} cannot be negative.", file=sys.stderr)
            return 1
        if val > 1:
            print(f"Error: {name} is a decimal fraction (0.12 = 12 percent), got {val}.", file=sys.stderr)
            return 1
    if args.combined_rate is not None:
        if args.duty_rate > 0 or args.purchase_tax_rate > 0:
            print("Error: --combined-rate already includes VAT, duty and purchase tax.", file=sys.stderr)
            print("  Do not also pass --duty-rate or --purchase-tax-rate, or the tax is counted twice.", file=sys.stderr)
            return 1
        if args.combined_rate < 0 or args.combined_rate > 5:
            print(f"Error: --combined-rate is a decimal fraction (0.4066 = 40.66 percent), got {args.combined_rate}.", file=sys.stderr)
            return 1
        if args.excluded_goods:
            print("Error: --combined-rate cannot be used with --excluded-goods; alcohol and tobacco", file=sys.stderr)
            print("  are on specific or compound rates. Use the Tax Authority's consolidated table.", file=sys.stderr)
            return 1
    if args.excluded_goods and args.purchase_tax_rate > 0:
        print("Error: --excluded-goods with an ad-valorem --purchase-tax-rate.", file=sys.stderr)
        print("  Alcohol and tobacco are taxed on SPECIFIC or COMPOUND rates (NIS per litre", file=sys.stderr)
        print("  of pure alcohol, NIS per unit), which this script cannot express. Any", file=sys.stderr)
        print("  percentage you supply here is invented. Use the Tax Authority's", file=sys.stderr)
        print("  consolidated import-tax table for alcoholic beverages, cigarettes and tobacco.", file=sys.stderr)
        return 1
    try:
        result = calculate_landed_cost(
            product_value=args.value,
            shipping=args.shipping,
            insurance=args.insurance,
            fx_rate=args.fx,
            duty_rate=args.duty_rate,
            purchase_tax_rate=args.purchase_tax_rate,
            broker_fees_ils=args.broker_fees_ils,
            currency=args.currency,
            personal_import=args.personal,
            usd_value=args.usd_value,
            excluded_goods=args.excluded_goods,
            combined_rate=args.combined_rate,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({k: str(v) if isinstance(v, Decimal) else v for k, v in result.items()}, indent=2, ensure_ascii=False, default=str))
        return 0

    if result.get("exempt"):
        print(f"EXEMPT: {result['reason']}")
        print(f"Estimated delivered cost (no import taxes): {result['landed_cost_ils']} ILS")
        print("  Converted at the plain Bank of Israel representative rate: the customs")
        print("  +0.5 percent uplift belongs to a tax base, and there is no tax here.")
        print("  NOTE: excludes the carrier's or Israel Post's clearance commission,")
        print("        which is charged on top of shipping and is not a tax.")
        print("  CHECK THE GOODS CLASS: tobacco products and alcoholic beverages NEVER")
        print("  qualify for this exemption at any value. If the parcel contains either,")
        print("  this EXEMPT result is wrong. Re-run with --excluded-goods.")
        return 0

    print("Israeli landed-cost breakdown")
    print(f"  FX (BoI rep.):    {result['inputs']['boi_representative_rate']}")
    print(f"  FX (customs):     {result['inputs']['customs_fx_rate']}  (representative rate x 1.005; no uplift on an ILS invoice)")
    print(f"  Goods + freight:  {result['goods_outlay_ils']} ILS  (at the representative rate: what you pay the seller)")
    print(f"  CIF tax base:     {result['cif_ils']} ILS  (at the customs rate: what the taxes are computed on)")
    if result.get("combined_tax_ils") is not None:
        print(f"  Import taxes:     {result['combined_tax_ils']} ILS  (combined rate {result['inputs']['combined_rate']} x CIF; VAT included)")
        if result.get("combined_in_duty_waiver_band"):
            print("  NOTE: goods between USD 75 and 500 on a personal import: customs DUTY is waived")
            print("        in this band. If the combined rate includes a duty share, it should not apply.")
            print("        Check that the official calculator's rate already reflects the waiver, or use")
            print("        --duty-rate/--purchase-tax-rate (the cascade route) for an estimate without")
            print("        the duty (a floor where purchase tax applies).")
        if args.personal:
            print("  NOTE: the calculator's percentage depends on the goods value. Use the rate it")
            print("        shows for THIS parcel's value; a rate quoted for another price is wrong here.")
        if not args.personal:
            print("  NOTE: the all-in percentage comes from the PERSONAL-import calculator. A")
            print("        commercial import is priced per tariff item (duty, purchase tax, VAT).")
    else:
        print(f"  Customs duty:     {result['duty_ils']} ILS")
        print(f"  Purchase tax:     {result['purchase_tax_ils']} ILS")
        print(f"  VAT:              {result['vat_ils']} ILS")
    print(f"  Broker fees:      {result['broker_fees_ils']} ILS")
    print(f"  Total landed:     {result['landed_cost_ils']} ILS")
    if result.get("duty_waived_personal_import"):
        print("  NOTE: customs duty set to 0. Under the personal-import regime duty is")
        print("        waived for goods valued above the exemption and up to USD 500;")
        print("        only VAT, and purchase tax where the goods carry it, apply.")
    if args.excluded_goods:
        print("  WARNING: alcohol and tobacco are taxed on SPECIFIC or COMPOUND rates")
        print("           (NIS per litre of pure alcohol, NIS per unit), not on a percentage.")
        print("           This script prices ad-valorem rates only, so the figures above")
        print("           are NOT the charge on these goods. Use the Tax Authority's")
        print("           consolidated import-tax table for alcohol, cigarettes and tobacco.")
    if result.get("purchase_tax_is_floor"):
        print("  NOTE: the purchase-tax line omits the statutory wholesale-price uplift (TAMA),")
        print("        so it is a FLOOR, and so are the VAT and the total built on it. Prefer")
        print("        --combined-rate with the all-in rate from the Tax Authority calculator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
