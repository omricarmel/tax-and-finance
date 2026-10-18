---
name: israeli-customs-duty-calculator
description: "Not customs advice. Classify products into Israeli customs tariff (HS) codes and calculate full landed cost for imports to Israel: customs duty, VAT 18%, and purchase tax (mas kniya). Use when user asks about Israel import tax, personal import threshold, customs duty on an online order from Amazon/AliExpress, FTA preferences from US/EU/UK/Canada, Shaar Olami tariff lookup, getting import tax back on a returned or defective item, or the cost of bringing goods into Israel. Do NOT use for domestic VAT bookkeeping (use israeli-vat-reporting) or for export documentation (use israeli-export-shipping-kit)."
license: MIT
compatibility: "Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Antigravity, Gemini CLI. Python 3.8+ for helper scripts."
---

# Israeli Customs Duty Calculator

## Legal notice

This is a free information tool operated by an AI model. It explains the rules and calculates from the figures you enter, but it does not examine your full circumstances and does not constitute customs or tax advice. All of its outputs are produced automatically, with no involvement, review, or approval by a customs agent or tax adviser, and an AI model may err, omit data, or present a wrong conclusion. The binding classification and charge are determined by the Tax Authority at import. This tool is not a substitute for advice that takes account of the particular circumstances and needs of each person, and all use of its output is the user's sole responsibility.


## Problem

Importing goods into Israel (whether a single Amazon order or a commercial shipment) triggers up to three separate taxes: customs duty, VAT, and purchase tax (mas kniya). Thresholds shift (the personal exemption moved four times between December 2025 and June 2026 and is back at $75; see Step 2), duty depends on an Israeli tariff item code that is not the same as the US or EU code, and free-trade preferences only help when you produce the right origin proof. Buyers constantly over- or under-estimate the landed cost.

## Instructions

### Step 1: Identify the import type

| Type | Typical user | Tax treatment |
|------|--------------|---------------|
| Personal import, small parcel | Consumer ordering online | Exemption threshold applies (see Step 2) |
| Personal import, high-value | Consumer buying jewelry, electronics | VAT applies; some goods also owe duty and purchase tax depending on the HS code (see Step 2) |
| Commercial import (B2B) | Osek Murshe importing stock | Full duty + VAT, no threshold exemption. Import VAT is recoverable as input tax, but only against a rashimon that identifies the importer as the taxable person; check with your bookkeeper how the rashimon is made out before assuming recovery. This skill does not verify the input-tax rule |
| Gift | Individual sending to an Israeli | Treated as personal import, no special exemption |
| Aliyah, oleh hadash or toshav chozer belongings | New immigrant or returning resident | A separate personal-effects exemption this skill does not compute. For an oleh's duty-free shipments use the `israeli-aliyah-customs-shipment-planner` skill; otherwise take it to a licensed customs agent (customs broker) or the customs house. Do not use the commercial row |

**This table is not exhaustive.** Israeli customs law carries several further regimes this skill does not cover and cannot compute: temporary import under an ATA carnet or a customs deposit (trade-fair goods, professional equipment, demo units), goods exported for repair or warranty service and re-imported, returning resident (toshav chozer), and diplomatic or international-organisation entry. If the shipment is any of those, **do not route it through the commercial row**: the tax base is different and following this skill will overstate the charge, sometimes by the whole value of the goods. Take those to a licensed customs agent (customs broker) or to the customs house directly. See `references/domain-checklist.md`.

**Courier vs postal parcels:** how the parcel arrives changes how the tax is paid, not how much it is. On an ordinary Israel Post parcel the tax is paid at the post office on collection, in cash only, or beforehand by credit card through the tax-payment app with a reference number. On EMS and courier parcels the courier company pays the tax and collects it from the buyer at delivery; most couriers send an SMS or email first and let you pay ahead. In exceptional cases, for example when customs needs more detail on the goods, the recipient has to release the parcel at the customs house in person. Both Israel Post and the couriers charge their own clearance commission on top of shipping.

### Step 2: Check the personal import threshold

As of 18 October 2026, re-verified against the source on that date, the personal import exemption is USD 75 (cost of goods, excluding shipping and insurance). This figure is exceptionally unstable. It was raised from USD 75 to USD 150 by a Finance Ministry order in December 2025; the Knesset revoked that order on 24 February 2026, reverting to USD 75; the Finance Minister signed a fresh order setting it to USD 130 effective midnight 24-25 February 2026; and the Knesset revoked that USD 130 order as well at the start of June 2026 (59 votes to 23), returning the threshold to USD 75. Kol Zchut dates the USD 130 window 25 February to 1 June 2026. No later order has been found as of 18 October 2026. Treat any value quoted here as provisional and confirm it against the live official calculator.

- Up to and including USD 75: no customs, no VAT, no purchase tax (full exemption). The source rule is "up to 75 dollars", so a parcel of exactly USD 75.00 is exempt. `scripts/calculate_duty.py` implements it inclusively
- USD 75 to USD 500: customs duty is waived under the personal-import regime, but VAT of 18 percent applies, and purchase tax still applies to goods that carry it (televisions and vehicle spare parts are the common examples). Note the two different bases: the THRESHOLD is tested on the goods value alone, excluding shipping and insurance, but the TAX is computed on the CIF value (goods plus insurance plus freight) plus any duty and purchase tax
- Above USD 500: VAT applies, and SOME goods also owe customs duty and purchase tax. It is not automatic that all three apply: the rate depends on the HS classification, so look the code up rather than assuming the full stack.
- Above USD 1,000: the shipment is treated as commercial for tax purposes. In practice carriers will usually require a licensed customs agent (customs broker) and a full import declaration (rashimon) at this point, though that is a commercial practice rather than a stated legal threshold, so confirm with the carrier.

**Important carve-out**: the exemption does NOT apply to tobacco products or alcoholic beverages. Those are taxed in full from the first shekel, regardless of value. (The exemption text quoted by the rights guides names tobacco and alcoholic beverages only. E-cigarettes are commonly assumed to be treated the same way, but that is not what the quoted text says, so check the current rule before telling a user their vape shipment is or is not excluded.)

**Groups that may get relief:** Kol Zchut names lone soldiers and officers, new immigrants (olim), and returning students or returning residents as populations that may be entitled to personal-import relief. This skill does not compute those reliefs; for olim see Step 1, and the others should check their entitlement with the customs house before paying.

**Anti-splitting rule**: two or more parcels sent from the same supplier to the same customer within 72 hours of each other are treated as one split shipment, and import taxes are computed on their combined value. Ordering below the threshold repeatedly in the same window does not work.

Confirm the current threshold via the official Personal Import Tax calculator at `https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/PersonalImportTax` or the gov.il service page at `https://www.gov.il/en/service/customs-tax-calculation-import-by-israelis` before quoting a number to the user. The personal-import threshold has changed four times in seven months.

### Step 3: Classify the product into its Israeli tariff item

Israel's tariff (the Customs and Purchase Tax Tariff) is built on the international Harmonized System. The first 6 digits are the international HS code; the digits after them are Israeli subdivisions that decide the duty, the purchase tax and the import conditions. Shaar Olami displays an item as a 10-digit code followed by a check digit, for example `2208300000/4` for whiskies or `8708999000/3` for one line of vehicle parts. Work with the full code exactly as Shaar Olami shows it.

1. Describe the product: material, function, packaging form, use, brand, model.
2. Start from the 2- or 4-digit HS chapter (e.g. chapter 85 for electrical equipment, chapter 22 for beverages and spirits).
3. Look up the full Israeli tariff item in Shaar Olami: `https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/en/CustomsBook/Import/Doubt`.
4. Do not guess the digits after the sixth. If unsure, ask Israeli Customs for an advance classification decision. Confirm its cost and the extent to which it binds directly with the customs house; this skill does not verify either.

### Step 4: Look up the duty rate, VAT rate, and purchase tax

From the Shaar Olami entry for the HS code, read:
- **Ad-valorem only.** This skill and its script price rates expressed as a percentage of value. The Israeli tariff also uses specific rates (NIS per kg, per litre, per unit) and compound rates of the form "X percent but not less than Y NIS per kg". Those are common on food, beverages, alcohol, tobacco, and some textiles and footwear. Read the rate cell in Shaar Olami literally: if it is not a bare percentage, this calculator cannot price it and the figure has to be worked out by hand.
- Customs duty rate. Read it off Shaar Olami for the specific tariff item. Do not quote a typical range: a great many Israeli tariff lines carry a zero applied rate and others do not, and the only rate that matters is the one on the code
- VAT rate: 18 percent standard since 1 January 2025
- Purchase tax: only on specific items. Kol Zchut gives televisions and vehicle spare parts as examples of personal-import goods that carry it. On alcohol and tobacco it is a specific or compound rate, not a percentage: Shaar Olami shows 100.24 NIS per litre of alcohol for whiskies (`2208300000`) and, for cigarettes (`2402200000`), 270 percent plus 555.28 NIS per 1,000 cigarettes but no less than 984.57 NIS per 1,000, both valid from 1 January 2026.

**The Tax Authority calculator gives ONE all-in percentage, VAT included.** For a personal import, the Tax Authority personal-import calculator shows a single tax percentage per item, and that percentage is applied once to goods plus shipping plus insurance. For an ordinary VAT-only item it is 18 percent. Kol Zchut's worked example is a car accessory at USD 520 plus USD 20 shipping with a calculator rate of 40.66 percent: the tax is 40.66 percent of USD 540. **Never feed that percentage into the cascade below as a purchase-tax rate**: it already contains the VAT, and adding 18 percent on top overstates the bill by well over half. The percentage is set by the value of the goods, so read it for this parcel's own value and never reuse a rate quoted for a different price. For a personal import between USD 75 and USD 500 the customs duty itself is waived, so any duty share in that percentage should not apply in this band: check that the official calculator's rate already reflects the waiver, or use the cascade route (`--duty-rate` with `--purchase-tax-rate`) for an estimate with the duty removed (a floor where purchase tax applies, see Step 6). In the script, pass it as `--combined-rate`.

### Step 4.5: Check the order confirmation before computing anything

Some sellers and some courier services collect Israeli import tax at checkout or ship on a delivered-duty-paid basis. Read the order confirmation and the shipping terms for a tax or duties line that has already been charged BEFORE running the cascade below, because the skill computes the charge from scratch and will otherwise hand the user a second bill for money already paid. If tax was collected at checkout and a courier still demands payment at the door, that is a dispute to raise with the seller and the carrier with the checkout receipt in hand, not a second liability to settle.

### Step 5: Calculate the CIF value

Israel Customs values goods at CIF: cost + insurance + freight.

**The conversion rate is not the plain Bank of Israel rate.** For goods priced in foreign currency, customs converts at the Bank of Israel representative rate **plus 0.5 percent**. Apply the uplift once, here, to the TAX BASE, and nowhere else in the calculation:

```
customs_rate = BOI_representative_rate * 1.005
CIF_ILS      = (product_price + shipping + insurance) * customs_rate
```

The `boi-exchange` MCP returns the representative rate; the 0.5 percent uplift is yours to add. `scripts/calculate_duty.py` takes the representative rate in `--fx` and applies the uplift internally, so do not pre-multiply before passing it in. Ignoring the uplift understates the tax base, and therefore every tax computed on it, by 0.5 percent (on a VAT-only parcel that is about 0.09 percent of CIF). The uplift is a rule for valuing the goods for tax; it does not change what you paid the seller, so the goods themselves enter the landed total at the plain representative rate. An invoice already priced in shekels is not converted and gets no uplift.

### Step 6: Compute the full landed cost

The three taxes are calculated on a cascading base. Use `scripts/calculate_duty.py` to avoid arithmetic mistakes.

```
duty       = CIF * duty_rate
base_after_duty = CIF + duty
purchase_tax = base_after_duty * purchase_tax_rate
base_for_vat = base_after_duty + purchase_tax
vat        = base_for_vat * 0.18
landed_cost = goods_and_freight_at_representative_rate + duty + purchase_tax + vat + broker_fees + handling
```

With the calculator's all-in percentage instead: `tax = CIF * combined_rate`, and `landed_cost = goods_and_freight_at_representative_rate + tax + fees`. Use one route or the other, never both.

**Known limit on the purchase-tax line.** Purchase tax under the Purchase Tax (Goods and Services) Law is a percentage of the WHOLESALE price, not of CIF plus duty. On an import that wholesale price is reconstructed rather than observed, by an uplift on top of CIF plus duty that varies by tariff item and is commonly called TAMA. **The uplift's rates, and the exact mechanism, are not verified in this skill.** The formula above omits it entirely, so on any item that actually carries purchase tax the purchase-tax figure it produces is a FLOOR, not the charge, and so are the VAT and the total built on it. Do not present such a number as final: read the all-in percentage for the specific item off the Tax Authority personal-import calculator and apply it once to CIF, as described in Step 4.

### Step 7: Check for FTA preference

A valid origin proof can eliminate the duty (but not VAT or purchase tax).

| Origin | Agreement | Origin proof |
|--------|-----------|--------------|
| United States | US-Israel FTA (1985) | US Origin Invoice Declaration on the commercial invoice |
| European Union | EU-Israel Association Agreement. The revised PEM Convention (established 2011) is the ONLY set of origin rules applying from 1 January 2026; the transitional two-set regime ended 31 December 2025. Israel signed the Regional Convention on 10 October 2013 and has ratified it | EUR.1 movement certificate, or an origin declaration on the invoice: any exporter up to EUR 6,000 per consignment, an approved exporter above that |
| United Kingdom | UK-Israel Trade and Partnership Agreement (2019) | EUR.1 movement certificate, or an invoice declaration under a value ceiling not verified here |
| Canada | CIFTA, in its modernized form | CBSA form B239 certificate of origin (blanket-period field, no fixed validity) |
| EFTA (CH, NO, IS, LI) | EFTA-Israel Free Trade Agreement | EUR.1 movement certificate. Not verified in this skill; confirm with the exporter before relying on it |
| Mercosur (BR, AR, UY, PY) | Mercosur-Israel FTA | Mercosur-Israel certificate of origin. Not verified in this skill; confirm with the exporter before relying on it |

See `references/fta-preferences.md` for details and pitfalls.

### Step 8: Check whether the item needs an import approval before it needs a tax figure

Tax is not the only thing that stops a parcel, and for several product classes it is not the first thing. Any person may import personally provided the goods are not on the prohibited-import list and, where a competent authority sets criteria for that class, its approval or import licence has been obtained. Check this BEFORE quoting a landed cost, because a parcel that cannot be released does not have one.

| Product class | Competent authority | Note |
|---|---|---|
| Communications products, baby monitors, remote controls, smartphones when the shipment is 4 devices or more | Ministry of Communications | The 4-device count is what moves a phone shipment from personal to approval-requiring |
| Vehicle spare parts | Ministry of Transport and Road Safety | Also a common purchase-tax class |
| Food and food supplements | Ministry of Health, National Food Service | |
| Plants and seeds | Ministry of Agriculture, plant-protection services | |
| Helmets, gas-fired barbecues | Standards Institute of Israel | A helmet needs no approval if it already carries European or American certification |

The classes and criteria change; confirm with the authority itself, and with the Ministry of Economy for anything not listed. Whether a product needs Standards Institution approval under an official standard is the subject of the `israeli-standards-import-checker` skill.

### Step 9: If the assessment looks wrong, appeal it, and know which route

Two different objections go to two different places, and conflating them loses the user weeks.

- **Against the carrier's clearance commission**: to that carrier's own customer service. Customs has nothing to do with it.
- **Against the amount of tax assessed**: an online application through the personal area of the National Identification System (maarechet ha-hizdahut ha-leumit), which needs a one-time registration first. Attach proof of the payment transferred to the supplier and evidence of the actual transaction value. The service is free. For help, the claims, deposits and arrears unit (tafag) at the relevant customs house.

Refund claims (Step 10) go through the same personal-area route and the same tafag unit.

**Eilat residents** can claim back the VAT on a personal import the same way, free of charge, attaching: a copy of the identity card or a valid Eilat resident certificate, a cheque copy or bank-account confirmation, the import declaration or its number, the completed online request form, and an authorised signatory's or representative's confirmation. Quote an Eilat resident the VAT as refundable, not as a final cost.

### Step 10: If the goods are returned or exchanged, claim the tax back

Someone who paid the import taxes and then returns or exchanges the goods because they are defective or not as described is entitled to a refund. File online through the Tax Authority site; where the parcel came via an international shipping company, file with the claims, deposits and arrears department (tafag) at the Ben Gurion customs house.

Four conditions all have to hold:

- the goods were not imported in bulk
- they were not used, beyond any use that was necessary to discover the defect
- they were returned no later than 6 months after import, provably on time
- the goods exported are shown to be the same goods that were imported

Attach the tax receipt quoting the import-declaration number, the correspondence with the supplier, proof of the credit or the replacement, and a cheque copy or bank-account confirmation. **Above USD 250 of returned or exchanged goods** a customs export-inspection request form is also required, and the shipper or post office must have recorded on the export declaration that a refund claim is intended and have performed a physical check. Getting that recorded at the moment of export is the step people miss; it cannot be added afterwards.

## Examples

### Example 1: Amazon order under the threshold

User says: "I'm ordering a 60 dollar keyboard from Amazon US. Will I pay tax?"

Actions:
1. Personal import, product value below the USD 75 threshold (re-verified 18 October 2026).
2. No customs duty, no VAT, no purchase tax.
3. Warn that shipping charges are NOT counted toward the threshold as long as they are itemized separately on the invoice. If shipping is bundled into the product price, the combined figure is tested.
4. Note: the same keyboard at 120 dollars would NOT be exempt today. It exceeds the USD 75 threshold and would owe about 18 percent VAT (the USD 130 order that once covered it was revoked by the Knesset at the start of June 2026). The threshold has changed four times in seven months, so verify via the official calculator before quoting.

Result: No import tax at 60 dollars. Landed cost is the US price plus shipping, plus any clearance commission Israel Post or the courier charges.

### Example 2: 200 dollar camera above the threshold

User says: "How much will I pay in import tax for a 200 dollar camera from Amazon?"

Actions:
1. Personal import, product value above USD 75 but under USD 500. VAT applies, customs duty is waived under the personal-import regime.
2. Classify camera: HS chapter 85 (electrical machinery), likely 8525.89.xx range. Look up the exact Israeli tariff item in Shaar Olami.
3. Apply 18 percent VAT on the CIF value (product + shipping + insurance, converted to ILS at the Bank of Israel representative rate plus 0.5 percent). For a personal import the CIF is typically just the product value plus itemized shipping.
4. Customs duty: 0 percent under the personal-import waiver for values up to USD 500. Above USD 500 the waiver stops applying and the rate is whatever the tariff item says, so look it up rather than assuming cameras are duty-free.
5. Purchase tax: generally none for cameras (check Shaar Olami for the specific tariff item).
6. Run `python3 scripts/calculate_duty.py --value 200 --shipping 20 --duty-rate 0 --purchase-tax-rate 0 --fx 3.65 --personal`.

Result: Approximate tax of 18 percent of (200 + 20) USD converted to ILS at the representative rate plus 0.5 percent. The script prints the CIF tax base (at the customs rate), the VAT on it, and a total in which the goods and shipping are converted at the plain representative rate, plus a courier or postal handling and clearance commission charged on top (the amount varies by carrier, and any dispute about it goes to the carrier, not to customs). Confirm via the official calculator.

### Example 3: Commercial EU import with EUR.1

User says: "I'm importing 50 units of Italian leather bags, CIF 12000 euros, HS 4202.21.xx. What paperwork do I need?"

Actions:
1. Commercial import; no personal exemption applies.
2. Classify to the full Israeli tariff item via Shaar Olami and read the duty rate off that entry. Do not assume a range; this skill does not carry rates.
3. At this value, ask the Italian exporter for a EUR.1 movement certificate stamped by Italian customs, or an origin declaration on the invoice from an exporter holding approved-exporter status. Under the revised PEM Convention any exporter may make out an origin declaration only for a consignment worth up to EUR 6,000; above that the exporter must be an approved exporter and quote its authorisation number (French customs FAQ on the revised Convention). EUR 12,000 is over the ceiling, so a plain invoice declaration from a non-approved exporter will not carry the preference.
4. Duty is waived under the EU-Israel agreement provided the EUR.1 is valid.
5. VAT at 18 percent on (CIF + duty) is still due.
6. Israel does NOT accept electronic signatures on EUR.1; the supplier must post the original.
7. Origin proof and tax are only part of a commercial clearance. Filing the import declaration (commonly done through a licensed customs agent), the commercial documents, any Free Import Order approval or standard the goods need, and labelling for resale are outside this skill; Shaar Olami lists the import conditions for each tariff item next to its rates.

Result: Origin-preferred landed cost is CIF plus 18 percent VAT plus broker fees. Without a valid EUR.1, full duty applies.

## Bundled Resources

### Scripts
- `scripts/calculate_duty.py` -- Calculates cascading duty + purchase tax + VAT 18 percent on a CIF value. Supports USD/EUR input and prints a full breakdown. Run: `python3 scripts/calculate_duty.py --help`

### References
- `references/hs-codes-guide.md` -- How Israeli tariff classification works, how to use Shaar Olami, binding pre-rulings.
- `references/fta-preferences.md` -- All Israeli FTAs, which origin proof each requires, common traps.
- `references/duty-rates-by-category.md` -- Indicative duty and purchase-tax rates by product category with examples. Always verify the exact rate for your tariff item in Shaar Olami.

## Recommended MCP Servers

| MCP | Why | URL |
|-----|-----|-----|
| boi-exchange | Returns the Bank of Israel daily representative rate for USD, EUR, GBP. Customs valuation adds 0.5 percent on top of that rate, which the MCP does not do for you | https://agentskills.co.il/mcp/boi-exchange |

## Gotchas

- The exemption does NOT cover tobacco products or alcoholic beverages. Those pay VAT and purchase tax from the first shekel regardless of value. E-cigarettes are not named in the exemption text the rights guides quote, so verify rather than asserting.
- Only the first 6 digits of an Israeli tariff item are international; the digits after them are Israeli. A US HTS code or an EU CN code does not translate directly; confirm the Israeli code in Shaar Olami.
- FTA preference removes the customs duty only. VAT 18 percent and purchase tax (where applicable) still apply regardless of origin.
- EUR.1 must carry a wet-ink (original) signature. Israel does not accept electronically signed EUR.1 certificates. Plan courier time for the original to arrive.
- Purchase tax is NOT a small rounding item. On alcohol and tobacco the tariff is specific or compound, not a percentage (100.24 NIS per litre of alcohol on whiskies; 270 percent plus 555.28 NIS per 1,000 cigarettes, minimum 984.57 NIS per 1,000, from 1 January 2026), so this skill and its script cannot price them at all. Do not assume only VAT applies. Its base is also not CIF plus duty but a reconstructed wholesale price, so the script's purchase-tax line is a floor rather than the charge; take the all-in percentage off the official calculator instead and apply it once to CIF, never on top of VAT.
- Packages above USD 1,000 are treated as commercial for tax purposes. Carriers will usually require a licensed customs agent (customs broker) and a full import declaration (rashimon) at that point, but that is commercial practice rather than a stated legal threshold, so confirm with the carrier.
- The conversion rate is the Bank of Israel representative rate plus 0.5 percent, not the representative rate itself. Taxes computed on the bare rate are low by 0.5 percent of the tax. The uplift values the goods for tax only; it is not added to the price you paid.
- Israel Post and the courier companies charge their own commission for the clearance service, on top of the shipping cost, and it is not a tax. Objections and appeals about the commission go to the carrier's customer service, not to customs, which is a different route from an appeal against the tax itself.
- Customs may inspect the declared value and reject it, substituting a value of its own under part 2.5 of the personal-import valuation procedure. A supplier invoice is a starting point, not a ceiling.
- A false declaration or label lets customs seize the parcel or impose a fine as a condition of release, **and that applies even when the buyer did not know the declaration was wrong**. Confirm with an online seller that the declared contents and price on the package match what was actually bought.
- A parcel holding items with different tax treatments (clothing plus alcohol, say) is assessed item by item, not on one blended rate for the box.

## Reference Links

| Source | URL | What to check |
|--------|-----|---------------|
| Israel Tax Authority | https://www.gov.il/en/departments/israel_tax_authority | Current VAT rate, customs policy updates |
| Personal Import Tax calculator (Shaar Olami) | https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/PersonalImportTax | Live personal-import calculator with the current threshold baked in |
| Personal import calculator (gov.il) | https://www.gov.il/en/service/customs-tax-calculation-import-by-israelis | Alternative live calculator with current thresholds |
| Shaar Olami tariff query | https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/en/CustomsBook/Import/Doubt | Israeli tariff item, duty rate, purchase tax rate, import conditions |
| EU-Israel trade relationship | https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/israel_en | EUR.1, association agreement, PEM status |
| US-Israel FTA | https://www.trade.gov/us-israel-free-trade-agreement | Origin invoice declaration, 35 percent value-added rule |
| CIFTA certificate form B239 | https://www.cbsa-asfc.gc.ca/publications/forms-formulaires/b239-eng.html | The certificate itself, its fields and its blanket period |
| CIFTA rules of origin (CBSA index page) | https://www.cbsa-asfc.gc.ca/publications/dm-md/d11/d11-5-6-eng.html | Link page only. It points at the CIFTA Rules of Origin Regulations and does NOT state the certificate form number or any validity period, so do not cite it for either |
| Personal import rights guide (Kol Zchut) | https://www.kolzchut.org.il/he/%D7%96%D7%9B%D7%95%D7%AA%D7%95%D7%9F_%D7%91%D7%A0%D7%95%D7%A9%D7%90_%D7%99%D7%91%D7%95%D7%90_%D7%90%D7%99%D7%A9%D7%99_(%D7%97%D7%91%D7%99%D7%9C%D7%95%D7%AA_%D7%9E%D7%97%D7%95%22%D7%9C) | Current threshold, band table, the 0.5 percent FX uplift, approval authorities, refund conditions |
| Bank of Israel exchange rates | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | Daily USD/EUR/GBP to ILS rate for customs valuation |

## Troubleshooting

### Error: "My landed cost estimate is way off"

Cause: Forgetting that VAT is calculated on CIF + duty + purchase tax, not on the product price alone.

Solution: Recompute using the cascading formula in Step 6, or run `scripts/calculate_duty.py`. Add courier or broker handling and clearance fees separately; these vary by carrier and are charged on top of duty and VAT.

### Error: "Customs rejected my EUR.1"

Cause: electronic signature, missing supplier declaration, or a consignment above EUR 6,000 accompanied only by an invoice declaration from an exporter without approved-exporter status.

Solution: Request an original wet-ink EUR.1 from the EU exporter's customs authority. For repeat shipments, the exporter should apply for approved-exporter status so invoice declarations cover any value.

### Error: "HS code I used gives a different duty in the US"

Cause: US HTS and the Israeli customs tariff share only the first 6 digits; everything after them differs.

Solution: re-look the product up in Shaar Olami. If you need certainty, request an advance classification decision from Israeli Customs with a product description and catalog, and ask them what it costs and how far it binds.
