---
name: israeli-export-shipping-kit
description: "Generate the full export document set for Israeli exporters: commercial invoice (HE+EN), packing list, bill of lading / AWB / CMR, proforma, and origin documents (EUR.1, invoice origin declaration, US-Israel exporter origin statement, CIFTA Form B239). Use when user asks about exporting from Israel, Incoterms (FOB, CIF, DDP, EXW), EUR.1 certificate, approved exporter status, US-Israel FTA certificate of origin, commercial invoice template, or packing list. Do NOT use for import calculations (use israeli-customs-duty-calculator) or domestic VAT bookkeeping (use il-invoice-organizer)."
license: MIT
compatibility: "Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, Antigravity, Gemini CLI. Python 3.8+ for helper scripts."
---

# Israeli Export Shipping Kit

## Legal notice

This is a free information tool operated by an AI model. It explains customs and import rules and helps you organise your own figures. It explains export documentation, origin rules and the VAT zero rate on exports, and produces draft commercial invoices, packing lists and origin-declaration wording from the figures you supply. All of its outputs are produced automatically by an AI model, with no involvement, review, or approval by a customs agent or tax adviser. The output is not a filed customs declaration and not a professional opinion, but an explanation and a draft only. An AI model may err, omit data, or present a wrong conclusion.

A declaration to the customs authority is a legal document, and a false declaration carries liability. Any text this tool produces is therefore an automatic draft for your personal preparation only, to be checked with a customs agent or with the Tax Authority before filing. This tool is not a substitute for advice that takes account of the particular circumstances and needs of each person, and all use of its output is the user's sole responsibility. Responsibility for reporting and paying the tax is yours, the binding computation is the Tax Authority's, and representation before the Tax Authority is reserved to those permitted by law.


## Problem

Shipping a product out of Israel triggers a paperwork chain: commercial invoice, packing list, transport document (B/L, AWB or CMR), and an origin proof matched to the destination's FTA (EUR.1 for EU/UK, an exporter origin statement backing the US importer's FTA claim, Form B239 for Canada). Getting any of these wrong delays clearance or denies preferential duty. Exporters also routinely pick the wrong Incoterm and end up absorbing freight or insurance they meant the buyer to pay.

## Instructions

### Step 1: Choose the Incoterm

Incoterms 2020 (ICC) defines 11 three-letter trade terms. Pick once and write it on every document alongside the named place.

| Mode | Code | Name | Seller delivers until... |
|------|------|------|--------------------------|
| Any | EXW | Ex Works | Buyer collects at seller's premises |
| Any | FCA | Free Carrier | Seller hands goods to buyer's carrier |
| Any | CPT | Carriage Paid To | Seller pays freight to named destination |
| Any | CIP | Carriage and Insurance Paid To | Like CPT, seller also buys insurance |
| Any | DAP | Delivered at Place | Seller delivers, buyer unloads |
| Any | DPU | Delivered at Place Unloaded | Seller delivers AND unloads (replaced DAT) |
| Any | DDP | Delivered Duty Paid | Seller pays import duty and clears |
| Sea | FAS | Free Alongside Ship | Alongside the vessel at named port |
| Sea | FOB | Free on Board | On board the vessel |
| Sea | CFR | Cost and Freight | Seller pays sea freight, risk transfers at loading |
| Sea | CIF | Cost Insurance and Freight | CFR plus marine insurance |

Rule of thumb:
- FOB/CFR/CIF are for bulk sea cargo only. Do not use them for containers or air freight; use FCA/CPT/CIP.
- Avoid EXW with international buyers unless the buyer explicitly handles export clearance from Israel.
- DDP is risky for small exporters: you become responsible for Israeli export formalities AND foreign import clearance.

### Step 2: Draft the commercial invoice

Required fields (bilingual HE + EN is recommended for Israeli customs):

- Exporter (shipper): Israeli business name, address, VAT ID, phone, email
- Consignee (buyer): full name, address, country, tax/VAT ID
- Invoice number and date
- Purchase order / buyer reference
- Incoterm + named place (e.g. "FOB Haifa" or "DAP Berlin")
- Country of origin (Israel, for goods wholly or substantially produced in Israel)
- Item lines: description (HE + EN), HS code (look it up in the Israeli customs tariff book, תעריף המכס), quantity, unit price, total
- Currency (USD, EUR, GBP or ILS)
- Totals: subtotal, freight, insurance, total invoice value
- Declaration of origin (when claiming FTA preference, see Step 4)
- Exporter signature, stamp, printed name

Israeli exports are zero-rated for VAT: the standard rate is 18 percent, but exports carry a 0 percent rate. The invoice must still show the VAT line explicitly as 0 for the Tax Authority. The 0 percent rate under Section 30(a)(1) of the VAT Law is CONDITIONAL: it applies (precious stones aside, which have their own regime) to goods for which an export declaration (הצהרת ייצוא), or another document the Director has approved for this purpose, was filed AND customs release (התרה) was given. Keep that document and the transport documents on file. Everyone in the trade calls the export declaration a רשימון יצוא, and your customs broker will use that name, but it is the same document. A courier waybill or a post-office receipt on its own is not the document the section names, so on a courier or postal shipment ask the carrier which export declaration covers your parcel before you zero-rate the invoice. Without that proof the Tax Authority can deny the 0 percent and assess VAT at 18 percent.

Invoice in the currency you actually contracted in, and do not convert the item lines to
shekels on the invoice itself. For the VAT return and the books, your accountant
translates the transaction to shekels by the representative rate for the tax point (confirm
the exact rule they apply), not by the rate on the day you get paid. For goods the tax point is delivery under section 22(a), so a shipment delivered in
December and paid in February belongs to the December reporting period. Check which basis
applies to you before relying on that: section 22(b) puts a dealer whose turnover does not
exceed 2 million NIS (and certain other categories) on a CASH basis, where the tax point is
receipt of payment instead. Getting this backwards misdates the whole reporting period. Record the rate you used next to the entry.

### Step 3: Build the packing list

- Same header as the invoice (exporter, consignee, invoice number)
- Per-package: package number, dimensions, gross weight, net weight
- Per-item per-package: quantity, description, HS code
- Marks and numbers (visible on the cartons)
- Total number of packages, total gross weight, total net weight

### Step 4: Produce the origin document matched to the destination

| Destination | Document | Who signs | Notes |
|-------------|----------|-----------|-------|
| EU (27) | EUR.1 movement certificate | Israeli Customs endorses it | Issued on paper or electronically: Israeli Customs has issued EUR.1 certificates through Sha'ar Olami (Global Gate) since 1 April 2024, with an online authenticity check. EU-Israel trade runs on the REVISED PEM rules since 1 January 2026, so the proof is valid 10 months. For shipments up to 6000 euros an invoice declaration by any exporter is accepted. Box 7 and every invoice declaration MUST state the place + postal code where origin processing happened (see Gotchas) |
| EU (27), repeat shipper | Invoice declaration (any value) | Approved exporter | Approved-exporter status granted by Israeli Customs |
| United Kingdom | EUR.1 movement certificate (or invoice declaration up to 6000 euros) | Israeli Customs / exporter | UK-Israel Trade and Partnership Agreement, in force 1 January 2021 |
| United States | No mandatory exporter document; an exporter origin statement is good practice | Importer claims; exporter supports | For imports FROM Israel, CBP dropped the Form A on 20 May 1994 and instead may ask the US IMPORTER for a signed affidavit that the goods meet the FTA origin and shipping rules. Nothing is filed by you, but your buyer needs your facts to sign that affidavit, so put a signed origin statement on or with the invoice and keep the 35 percent calculation on file (wording in `references/origin-declaration-template.md`). The 'U.S. Origin Invoice Declaration' trade.gov describes is for the opposite direction, US exporters shipping to Israel. The FTA no longer means zero duty: since 24 July 2026 the US adds a 12.5 percent Section 301 duty on products of Israel on top of the normal rate, applied in the FTA ('Special') column as well, with listed exemptions (see Gotchas) |
| Canada | Form B239 (CIFTA CO) | Exporter | Modernized CIFTA in force September 1, 2019; certificate valid 4 years. No proof of origin is needed at all for commercial goods whose value for duty is CAD 3,300 or less. If the goods were minorly processed outside Israel or Canada on the way, add Form E669 |
| EFTA (Switzerland, Liechtenstein, Norway, Iceland) | EUR.1 movement certificate | Israeli Customs | Same EUR.1 form, but EFTA-Israel is still on the OLD 2012 PEM rules: the proof is valid only 4 months, and EUR-MED still exists on this route |
| Ukraine | EUR.1 movement certificate | Israeli Customs | Per the Israel-Ukraine FTA protocol |
| Turkey | **Do not plan a shipment here without checking first** | n/a | The Israel-Turkey FTA has not been terminated, but Turkey's trade ban on Israel (May 2024) is still in force and was tightened in February 2026, when Turkey stopped issuing EUR-MED certificates for Israel-bound goods even when routed through a third country. Treat Turkey as blocked in practice and confirm with your forwarder before quoting a customer |
| Mercosur (Brazil, Argentina, Uruguay, Paraguay) | Mercosur-Israel certificate of origin | Israeli Customs | NOT the EUR.1 form and NOT an invoice declaration: this agreement has its own certificate. Request it through Israeli Customs before shipping |
| UAE | Origin proof per the CEPA protocol (not a PEM agreement, so do not assume EUR.1) | Per the agreement | UAE-Israel CEPA in force 1 April 2023 |
| South Korea | Origin declaration per the KIFTA protocol | Exporter | Korea-Israel FTA (KIFTA) in force 1 December 2022 |
| Vietnam | Origin proof per the VIFTA protocol | Exporter / Israeli Customs | Vietnam-Israel FTA (VIFTA) in force 17 November 2024 |
| Guatemala, Panama, Colombia, Mexico, Jordan | Origin proof per each bilateral protocol | Per the agreement | Israel also has in-force FTAs with these countries (Guatemala 1 March 2024) |

Israel has free trade agreements in force with the EU, USA, EFTA, Canada (CIFTA), Mercosur, UK, Turkey, Ukraine, Jordan, Mexico, Panama, Colombia, Guatemala, South Korea (KIFTA, in force 1 December 2022), the UAE (CEPA) and Vietnam (VIFTA). Check the exact origin-document type and rules of origin in the specific agreement before shipping; the table above lists the most common ones.

**A note on the EU route: preferential access is in force.** The Commission's August 2026
PEM notice still lists EU-Israel origin rules as operating (on the revised rules from
1 January 2026). The Commission proposed suspending certain trade-related provisions of the
EU-Israel Association Agreement in September 2025, but that needs a Council decision, and
none had been adopted when this skill was last checked (October 2026). So quote EU customers
on the preferential basis today, and re-check before a long-dated quote. The reason to track it
is that a suspension would move Israeli goods to the EU's third-country MFN duty rates
overnight, which is a real pricing exposure on a long-dated contract. If you are quoting
delivered-duty terms months ahead, say who bears a duty change in the contract rather than
assuming today's rate holds. Note separately that the long-standing exclusion of goods from
Israeli settlements in territories administered since 1967 is unrelated to any of this and
has applied throughout.

**If the destination has no FTA with Israel, you need a non-preferential certificate of origin** issued by an Israeli chamber of commerce, not a EUR.1 or invoice declaration. A letter of credit may also call for one even where an FTA exists. See `references/non-preferential-origin.md`.

See `references/eur1-application-guide.md` for the EUR.1 fields and pitfalls, and `references/origin-declaration-template.md` for invoice declaration wording.

### Step 5: Attach the transport document

| Transport mode | Document |
|----------------|----------|
| Sea | Bill of Lading (B/L) - issued by the carrier or NVOCC |
| Air | Air Waybill (AWB) - issued by the airline or freight forwarder |
| Road (to a neighboring country or via a land border) | CMR consignment note per the CMR Convention |
| Courier (DHL, UPS, FedEx) | Waybill issued by the courier |

The transport document must match the Incoterm: under FOB the buyer chooses the carrier and receives the B/L, under CIF the seller buys the freight and may be on the B/L as shipper.

The export entry itself is filed electronically with Israeli Customs through the "Sha'ar Olami" (שער עולמי) system. In practice the freight forwarder or customs broker submits this declaration on the exporter's behalf, drawing on the commercial invoice, packing list, and origin document the exporter provides.


**Two counterparty details to confirm before the goods move, because both stall a shipment at the far end rather than at yours.**

- **The EU or UK consignee needs an EORI number.** Customs in the destination country will not clear an import without one, and it is the consignee's to obtain, not the Israeli exporter's. Ask for it early and put it on the invoice: chasing it after the container lands is how demurrage starts. An Israeli exporter does not need an EORI of their own unless they are acting as importer of record in the EU.
- **Your customs broker needs a power of attorney (ייפוי כוח לסוכן מכס).** The broker files the export entry in your name, and they cannot do it without that authorisation on file. Sort it once, before the first shipment, rather than per consignment.

### Step 6: Optional documents

- Proforma invoice: sent before shipment, used for advance payment or import license in the destination country.
- Certificate of Inspection (SGS / Bureau Veritas): required by some destination buyers for government tenders.
- Health certificate / phytosanitary certificate: for food, plants, cosmetics.
- Fumigation certificate: for wood pallets under ISPM-15.
- Insurance certificate: for CIF / CIP shipments.

### Step 7: Generate the set with the helper script

`scripts/generate_invoice.py` takes a JSON input (seller, buyer, items, Incoterm) and outputs a bilingual commercial invoice and packing list in markdown, ready for review before you lock the final PDF. A complete working example ships alongside it at `scripts/sample_order.json`; copy that and edit rather than building the JSON from scratch.

The script validates the required fields up front and names anything missing; the full field list is in `references/script-usage.md`.

Two behaviours worth knowing. **Freight and insurance enter the total only when the Incoterm puts them on the seller.** Under EXW, FCA, FAS and FOB the script prints them as "buyer's account" memo lines outside the total, because adding them would overstate the transaction value the importer declares; under the C and D terms they are included. **Line totals use the rounded unit price**, so the printed columns always multiply out.

To print the preferential origin declaration, set `origin_declaration` to `eu`, `uk` or `us`. For the EU and UK route also give `origin_place` and `origin_postcode` (where the originating processing happened, which Israeli origin proofs must state), and `approved_exporter_number` if you hold that status. Without it, above 6,000 EUR the script leaves the declaration out and says a EUR.1 is needed, because a non-approved exporter may not make one there. For the US, `us` prints a voluntary exporter origin statement the buyer can lean on. Add `buyer.eori` to print the consignee's EORI. The ceiling is a euro-equivalent test, so on a foreign-currency invoice the script tells you to convert and check it yourself.

The packing list is NOT produced by default. Pass `--packing-list` to append it, or you
will ship with an invoice and no packing list, which stalls clearance:

```
python3 scripts/generate_invoice.py --input sample_order.json --packing-list --output invoice.md
```

Optional `country_of_origin` (defaults to ISRAEL; set it for re-exports) and `reason_for_export` are explained in `references/script-usage.md`.

## Examples

### Example 1: EU shipment of 12000 euros to Germany

User: "I am shipping 12000 euros of industrial pumps to Germany. What do I need?"

Actions:
1. Incoterm: negotiate CIP Berlin (paid insurance, road/sea via a forwarder).
2. Commercial invoice HE + EN showing origin Israel, HS code per pump, zero VAT.
3. Packing list with per-carton breakdown.
4. EUR.1 movement certificate issued by Israeli Customs (on paper or electronically through Sha'ar Olami). On the EU route it is valid 10 months.
5. Bill of Lading or FCR/AWB from the forwarder.
6. Insurance certificate (required by CIP).
7. Reminder: the value exceeds 6000 euros, so an invoice declaration is NOT enough unless the exporter has approved-exporter status.

### Example 2: US shipment of 3000 USD to California

User: "I am sending 3000 USD of cosmetics to a US distributor."

Actions:
1. Incoterm: DAP Los Angeles (door delivery, buyer imports).
2. Commercial invoice HE + EN, zero VAT, full HS codes.
3. Packing list.
4. No certificate to file. Put a signed exporter origin statement on the invoice and keep the 35 percent calculation, so the US buyer can sign the affidavit CBP may ask for.
5. AWB from the courier.
6. Ensure that Israeli content + direct processing costs meet the 35 percent value-added rule.
7. Duty: the FTA removes the normal US duty, but not the 12.5 percent Section 301 duty on products of Israel in force since 24 July 2026 (check the HTS heading for an exemption). Under DAP the buyer pays it at entry, so tell them before they order. Do not quote DDP without pricing it in.

### Example 3: Small EU shipment under 6000 euros

User: "I am sending 4500 euros of leather goods to Poland."

Actions:
1. Incoterm: DAP Warsaw.
2. Invoice + packing list.
3. Under the 6000 euros threshold, an invoice origin declaration by any exporter is accepted; no EUR.1 needed.
4. Add the declaration wording (see `references/origin-declaration-template.md`).

## Bundled Resources

### Scripts
- `scripts/generate_invoice.py` -- Renders a bilingual commercial invoice and packing list from JSON input (seller, buyer, items, Incoterm). Run: `python3 scripts/generate_invoice.py --help`

### References
- `references/script-usage.md` -- Input fields for the helper script, required and optional.
- `references/incoterms-2020.md` -- Full breakdown of all 11 Incoterms 2020 rules with seller / buyer responsibility tables.
- `references/eur1-application-guide.md` -- Field-by-field guide to filling and stamping an EUR.1 in Israel.
- `references/pem-2026-rules.md` -- Which PEM rule set applies per partner pair (EU-Israel revised from 1 January 2026, EFTA-Israel 2012 rules), electronic EUR.1, cumulation.
- `references/non-preferential-origin.md` -- Chamber-of-commerce certificate for non-FTA destinations and letters of credit.
- `references/origin-declaration-template.md` -- Exact EU, UK and EFTA invoice-declaration wording, a voluntary US exporter statement, and the CIFTA Form B239 rules.

## Recommended MCP Servers

| MCP | Why | URL |
|-----|-----|-----|
| boi-exchange | Converts the Israeli exporter's invoice to USD, EUR or GBP at the Bank of Israel daily rate | https://agentskills.co.il/mcp/boi-exchange |

## Gotchas

- Agents confuse Incoterm letters. FOB is sea-only; use FCA for container shipments. CIF is sea-only; use CIP for air or multimodal.
- Do not apply one PEM rule set to every European destination. EU-Israel trade has used the REVISED PEM rules since 1 January 2026 (proof of origin valid 10 months, single proof type, no EUR-MED), while the EFTA states still apply the OLD 2012 rules with Israel (4 months). Older guides, and earlier versions of this skill, say Israel is entirely on the 2012 rules; that stopped being true for the EU route. When in doubt, check the partner pair in the Commission's PEM matrix (Reference Links).
- An exporter is permanently in a VAT refund position (zero output VAT, real input VAT), so the input side is where the money is, and Israel's allocation-number rule bites there and ONLY there. **The rule runs one way for an exporter, and getting the direction wrong costs money in both.** On the INPUT side, a tax invoice from an Israeli supplier needs a `מספר הקצאה` before you can deduct the VAT on it. These are ordinary domestic taxable supplies, so the zero-rate carve-out does NOT protect them: freight forwarding, customs brokerage, packaging and crating invoices land above the threshold routinely, and the deduction is disallowed without a number. On the OUTPUT side, your own export invoices are zero-rated and are expressly outside the requirement under s.47(א2)(1), which applies only `לעניין חשבונית מס שהוצאה בשל עסקה שהמס שחל לגביה אינו בשיעור אפס`. Never flag your own export invoice for a missing allocation number, however large. Applying the rule symmetrically is the classic exporter error.
  The threshold is keyed to the INVOICE's own date, not today's, so a supplier invoice from an earlier year is tested against its own band: nothing before May 2024, then NIS 25,000 from May 2024, NIS 20,000 from January 2025, NIS 10,000 from January 2026 and NIS 5,000 from June 2026. Two further points from the statute. The loss of YOUR deduction is s.38(א1), which has NO buyer-request condition, so do not wait to see whether anyone demanded a number: `לא יותר ניכוי מס התשומות הכלול בחשבונית מס שסכומה, בלא המס, עולה על 5,000 שקלים חדשים (מינואר 2026 ועד מאי 2026: 10,000 שקלים חדשים) ושאינה כוללת מספר שהקצה לה המנהל`. That demand belongs to the SELLER'S duty under s.47(א2)(1) and has nothing to do with whether you can deduct. And the subsection says `עולה על` (EXCEEDS), so a supplier invoice sitting exactly on a band figure is outside the rule. Check for the allocation number when the invoice arrives, not at the end of the reporting period, because chasing a supplier for it months later is how a refund claim gets cut. The 5,000 step took effect on 1 June 2026 as scheduled, and the Tax Authority's VAT directive 1/2025 confirms the output side: a zero-rated invoice gets no allocation number at all.
- EUR-MED is gone on the EU route: the revised rules keep a single proof (EUR.1 or origin declaration) instead of the double EUR.1 and EUR-MED approach. It survives only where the 2012 rules still apply, such as Israel-EFTA. Diagonal cumulation that mixes the two rule sets (for example EFTA materials into an Israeli product sold to the EU) works only through the permeability routes the Commission lists, so ask Israeli Customs before planning around it.
- EU-Israel Technical Arrangement: to win EU preference, EUR.1 Box 7 and every invoice declaration MUST state the name of the city, village or industrial zone AND the postal code where the origin-conferring processing took place. Goods produced in Israeli settlements in territories brought under Israeli administration since June 1967 are NOT entitled to preferential treatment. Since 16 May 2023 the EU enforces this with import code Y864. A EUR.1 or invoice declaration missing the place + postal code is rejected at the EU border. See `references/eur1-application-guide.md`.
- Do not tell an exporter that an electronically issued EUR.1 is invalid or that only a wet-ink paper form works. Israeli Customs notified the EU that it issues EUR.1 certificates electronically through Global Gate (Sha'ar Olami) from 1 April 2024, with an online authenticity check. Whichever way it is issued, the endorsement must come from Israeli Customs, not from the exporter.
- The 6000 euros threshold for an invoice declaration is stated in the PEM rules as "the total value of the products", so it is the value of the originating goods for the whole consignment, not a per-line figure and not the invoice grand total with freight and insurance stacked on top. A 5999 euros consignment of goods can skip the EUR.1; a 6001 euros one cannot, unless the exporter is approved. The helper script applies it to the goods subtotal for that reason.
- Do not tell an Israeli exporter that US-Israel FTA preference requires a certificate or a mandatory exporter declaration. The US importer claims it and answers CBP. Do not mix up the two directions here: the widely-quoted 10 January 2018 retirement of the Green Form (Form A) applies to US exporters shipping INTO Israel. For your direction, Israel to the US, CBP eliminated Form A on 20 May 1994 and replaced it with a signed affidavit that CBP may request from the importer, and CBP states the 2017 amendment "represents no change in the ILFTA requirements for importations into the United States".
- The US-Israel FTA is no longer a promise of zero duty. Since 24 July 2026 the US charges an additional 12.5 percent Section 301 duty on products of Israel, and the new tariff heading applies it in the FTA ('Special') column too, so it stacks on FTA goods. The notice exempts listed products and categories (for example goods properly entered under HTSUS chapter 98, such as returned US goods), so check the heading for your product. Articles of steel, aluminium or copper, passenger vehicles and their parts, and the other goods listed under heading 9903.05.90 are carved out because they sit under the Section 232 tariff headings, which carry their own duty instead; "exempt from Section 301" does not mean duty-free. Separately, CBP has suspended the 800 USD de minimis exemption indefinitely for every mode, postal and courier alike, so even a small parcel to a US consumer is dutiable. US tariff measures have changed several times since 2025: confirm the current position before quoting DDP or a landed price.
- A small B2C parcel to an EU consumer is a different lane from the B2B paperwork above. Since 1 July 2026 the EU charges a temporary customs duty of 3 euros per item on distance-sale consignments of 150 euros or less, whatever VAT route is used, until 1 July 2028. It is counted per tariff classification, not per unit. The exception that matters for Israeli goods: goods benefiting from a preferential trade agreement are excluded, as long as the VAT was NOT collected through IOSS and the goods are declared on the full (H1) declaration. Ask your courier or marketplace which declaration they file before you price.
- This skill builds shipping paperwork; it does NOT determine whether goods need an export license. Controlled goods are a separate regime: defense and military items fall under the Defense Export Control Agency (אגף הפיקוח על היצוא הביטחוני) at the Ministry of Defense, and civilian dual-use items fall under the Export Control Agency at the Ministry of Economy and Industry. If the product could be military, dual-use, or otherwise controlled, the exporter must check licensing with the relevant agency before shipping. Do not rely on this skill for that determination.

## Reference Links

| Source | URL | What to check |
|--------|-----|---------------|
| ICC Incoterms 2020 | https://iccwbo.org/business-solutions/incoterms-rules/incoterms-2020/ | Authoritative text of the 11 rules |
| US-Israel FTA (Trade.gov) | https://www.trade.gov/us-israel-free-trade-agreement | Origin declaration wording, 35 percent rule |
| US-Israel CBP page | https://www.cbp.gov/trade/free-trade-agreements/israel/certificate-origin-requirements | US importer-side compliance |
| CIFTA rules of origin | https://www.cbsa-asfc.gc.ca/publications/dm-md/d11/d11-4-2-eng.html | Form B239, 4-year validity, modernized 2019 |
| EU-Israel trade page | https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/israel_en | EU-Israel Association Agreement, PEM status |
| EU code Y864 (Access2Markets) | https://trade.ec.europa.eu/access-to-markets/en/news/new-code-y864-goods-imported-eu-preferential-origin-israel-16-may-2023 | EU-Israel Technical Arrangement, place + postal code, 1967 territories, code Y864 |
| Israel FTAs in force (overview) | https://en.wikipedia.org/wiki/Free_trade_agreements_of_Israel | Full list of Israel's FTAs and entry-into-force dates |
| PEM 2012 rules (Access2Markets) | https://trade.ec.europa.eu/access-to-markets/en/content/rules-origin-pan-euro-mediterranean-convention | The old rules Israel still applies with EFTA: EUR.1/EUR-MED, 4-month validity, 6000 euro threshold |
| PEM matrix and notices (EU TAXUD) | https://taxation-customs.ec.europa.eu/customs/international-affairs/pan-euro-mediterranean-cumulation-and-pem-convention_en | Which rule set each partner pair uses (EU-Israel revised from 1 January 2026), electronic EUR.1 issuers |
| USTR Section 301 forced-labor action | https://ustr.gov/sites/default/files/files/Press/Releases/2026/FLIP%20301%20Investigation%20Final%20Action%20FRN%207-23-26%20FINAL.pdf | The 12.5 percent US duty on products of Israel from 24 July 2026 |
| UK-Israel TPA | https://www.gov.uk/guidance/summary-of-the-uk-israel-trade-and-partnership-agreement | Post-Brexit UK preference, EUR.1 acceptance |
| Israel Tax Authority | https://www.gov.il/en/departments/israel_tax_authority | Zero-rated export VAT rules |
| Bank of Israel exchange rates | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | Daily USD/EUR/GBP to ILS rate for invoicing |

## Troubleshooting

### Error: "EUR.1 rejected at the EU border"

Cause: No Israeli Customs endorsement, incorrect box 4 (country / group of countries), no place + postal code in box 7, or a proof presented after its validity ran out (10 months on the EU route, 4 months on routes still on the 2012 rules such as EFTA).

Solution: Ask your customs broker for a fresh EUR.1 from Israeli Customs, or a retrospective one if the goods have already left. For repeat shipments, apply for approved-exporter status with Israeli Customs to switch to invoice declarations.

### Error: "US buyer says the origin declaration is invalid"

Cause: The buyer has nothing to sign the CBP affidavit against: no signed origin statement from you, or no 35 percent calculation behind it.

Solution: Give the buyer a signed exporter origin statement (template in `references/origin-declaration-template.md`) and your value-added calculation. Keep both on file in case CBP asks the importer to verify.

### Error: "Freight forwarder says my Incoterm is impossible"

Cause: FOB or CIF chosen for air freight, or DDP chosen without clearing authority in the destination country.

Solution: For air or multimodal, switch FOB/CFR/CIF to FCA/CPT/CIP. For DDP, confirm with the buyer that you have a local tax registration or a fiscal representative in the destination, otherwise switch to DAP.
