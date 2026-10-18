# Indicative Duty Rates by Category

**This file is not a rate table and must never be quoted as one.** It is a shape-of-the-tariff orientation aid only: it says which categories tend to carry duty or purchase tax at all, so you know what to look up. Every cell that reads "verify", "varies", "moderate" or "0 to moderate" means exactly that: the number is not here and cannot be inferred from here. The only figures given are the alcohol and cigarette purchase-tax rates read off Shaar Olami on 18 October 2026, as examples of a specific and a compound rate. Nothing in this file binds; only the Tax Authority's classification of your tariff item does.

Always verify the exact rate for your Israeli tariff item in Shaar Olami (`https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/en/CustomsBook/Import/Doubt`). VAT at 18 percent applies in addition on the post-duty CIF value. CIF here is already converted at the Bank of Israel representative rate plus 0.5 percent, per SKILL.md Step 5; the uplift is applied once, at conversion, and nowhere else.

## Electronics

| Category | Typical duty | Purchase tax |
|----------|--------------|--------------|
| Phones, computers, cameras | verify | verify |
| TVs, monitors | verify | carries purchase tax on personal imports (Kol Zchut example) |
| Home appliances | verify | verify |

## Apparel and footwear

| Category | Typical duty | Purchase tax |
|----------|--------------|--------------|
| Cotton clothing | 0 to moderate | verify |
| Synthetic clothing | moderate to higher | verify |
| Leather footwear | moderate | verify |

## Food and beverages

| Category | Typical duty | Notes |
|----------|--------------|-------|
| Unprocessed food | varies, some quotas | check TRQ (tariff rate quota) |
| Alcoholic beverages | verify | specific purchase tax, e.g. 100.24 NIS per litre of alcohol on whiskies from 1 January 2026 |
| Tobacco | verify | compound purchase tax, e.g. cigarettes 270 percent plus 555.28 NIS per 1,000, minimum 984.57 NIS per 1,000, from 1 January 2026 |

## Vehicles and parts

| Category | Duty | Purchase tax |
|----------|------|--------------|
| Passenger cars | verify | verify |
| Spare parts | verify | carries purchase tax on personal imports (Kol Zchut example); verify the tariff item |

## Cosmetics and luxury

| Category | Typical duty | Purchase tax |
|----------|--------------|--------------|
| Cosmetics, skin care | 0 to moderate | varies |
| Perfumes | verify | verify |
| Jewelry | varies, verify in Shaar Olami | varies, verify in Shaar Olami |

## Industrial goods

Read each item off Shaar Olami; this file does not characterise industrial rates.

## The calculation sequence

```
CIF = (product_price + freight + insurance)
duty        = CIF * duty_rate
base_after_duty = CIF + duty
purchase_tax = base_after_duty * purchase_tax_rate   # FLOOR ONLY, see caveat below
base_for_vat = base_after_duty + purchase_tax
vat         = base_for_vat * 0.18
landed      = goods_and_freight_at_representative_rate + duty + purchase_tax + vat + broker_fees
```

For personal imports, if the product value (excluding shipping and insurance, when itemized separately) is at or below the current threshold (USD 75, re-verified 18 October 2026, after the Knesset revoked the USD 130 order at the start of June 2026), no taxes apply at all. Between USD 75 and USD 500 only VAT applies, customs duty is waived under the personal-import regime, and purchase tax can still apply on specific items. Above USD 500 VAT applies and some goods also owe duty and purchase tax, depending on the HS classification. Above USD 1,000 the shipment is treated as commercial for tax purposes, and carriers in practice require a broker. Tobacco products and alcoholic beverages are excluded from the personal-import exemption regardless of value.

**Caveat on the purchase-tax line above, same as SKILL.md Step 6.** Purchase tax is levied on a reconstructed wholesale price, not on CIF plus duty, so the line above is a floor rather than the charge, and so are the VAT and total built on it. The uplift that reconstructs it varies by tariff item and is not verified in this skill. On alcohol and tobacco the tariff is specific or compound rather than a percentage, and the formula cannot express it at all. Take the all-in percentage for the specific item off the Tax Authority personal-import calculator and apply it once to CIF: it already includes VAT, so never add 18 percent on top of it.
