---
name: shekel-currency-converter
description: Not tax advice and not a filed return. Convert currencies to/from Israeli New Shekel (NIS/ILS) using Bank of Israel official representative rates (shaar yatzig). Use when user asks to convert shekels, NIS, ILS, asks about exchange rates, "shaar yatzig" (representative rate), or needs currency conversion for Israeli tax or business purposes, including which date's rate applies to foreign-currency income, to VAT on a payment from a foreign client, or as the customs rate for import VAT. Covers the official Bank of Israel published currencies (14 currencies) with current and historical (tax-date) rates. Do NOT use for cryptocurrency or unofficial money exchange rates.
license: MIT
allowed-tools: Bash(python:*) WebFetch
compatibility: Requires a shell with Python and network access to the Bank of Israel API. Works with shell-capable agents such as Claude Code, Cursor, Windsurf, OpenCode and Gemini CLI.
---

# Shekel Currency Converter

## Legal notice

This is a free information tool operated by an AI model. It retrieves the representative exchange rates the Bank of Israel publishes, converts amounts at them, and explains which date's rate the published rules point to. It does all of this without the involvement, review, or approval of a tax adviser or accountant. The output is not tax advice, not a filed return, and not a professional opinion, but published reference data and a general explanation only: it does not examine your books, your accounting basis, your VAT status or the full facts of your transaction. An AI model may err, omit data, or present a wrong conclusion.

Any figure or text this tool produces is for your personal preparation only. Responsibility for reporting and for paying the tax is yours, the binding computation is the Tax Authority's, and representation before the Tax Authority is reserved to those permitted by law. This tool is not a substitute for advice that takes account of the particular circumstances and needs of each person. Confirm with a tax adviser or accountant which date and rate apply to your transaction before filing or paying. All use of its output is the user's sole responsibility.

## Instructions

### Step 1: Identify Conversion Request
Parse the user's request for:
- **Source currency** and **target currency** (at least one should be NIS/ILS)
- **Amount** to convert
- **Date** (current or specific historical date, important for tax conversions)
- **Purpose** (general info vs. tax-relevant representative rate)

Common currency codes:
| Code | Currency | Hebrew |
|------|----------|--------|
| ILS | Israeli New Shekel | shekel chadash |
| USD | US Dollar | dolar |
| EUR | Euro | euro |
| GBP | British Pound | lira sterling |
| JPY | Japanese Yen | yen |
| CHF | Swiss Franc | frank shveitzi |

### Step 2: Fetch Exchange Rate

**Current rate (live JSON endpoint):**
The legacy XML feed at `currency.xml` is gone (it now redirects to the JSON API), so do NOT parse XML. Fetch the JSON endpoint and read the `exchangeRates` array.
```
Fetch: https://www.boi.org.il/PublicApi/GetExchangeRates
Parse JSON: response.exchangeRates is an array of objects.
Each object: key (currency code), currentExchangeRate (NIS per "unit"),
             unit (1, 10, or 100), currentChange (percent move vs. previous
             publication), lastUpdate (ISO timestamp).
```
Example object (the 2026-10-16 publication, a Friday, stamped 12:22 Israel time): `{"key":"USD","currentExchangeRate":3.089,"currentChange":-0.4511762810183693200128907500,"unit":1,"lastUpdate":"2026-10-16T09:22:04.9223221Z"}`. Here `currentChange` is a percentage daily move, not an absolute NIS delta, and it is NOT used in conversion math.

**Take the rate's date from `lastUpdate`, never from the system clock.** "Most recently published" is not the same as "today". The endpoint keeps serving the previous publication until the next one lands, so any call made before the day's publication returns the PREVIOUS business day's rate. Because the shaar yatzig is date-attributed for tax, stamping it with today's date misstates which day's rate was used, which is exactly the error a tax conversion cannot afford. If a response carries no `lastUpdate`, do not report a date at all: say the publication date could not be established.

**Historical / tax-date rate (SDMX series):**
The JSON endpoint's `?date=` parameter is IGNORED, it always returns the most recently published rate. For a specific past date (the rate that matters for tax), use the Bank of Israel SDMX EXR series instead:
```
Fetch: https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_<CUR>_ILS?startPeriod=YYYY-MM-DD&endPeriod=YYYY-MM-DD&format=csv
Replace <CUR> with the currency code (e.g., RER_USD_ILS, RER_EUR_ILS).
Parse CSV: read OBS_VALUE keyed by TIME_PERIOD.
```
The series omits non-publication days. The Bank of Israel's explanatory notes list them as Saturdays, Sundays, Israeli holidays, Christmas Day, New Year's Day and Easter, and add that the Bank has no obligation to publish on any specific date. If there is no row for the exact requested date, walk back to the most recent published date before it, and tell the user which date's rate you used. For foreign-source income this walk-back is the statutory rule: the Conversion Rules define the representative rate for a day with no publication as the last rate published before that day. A future date has no rate at all, and neither does TODAY before its publication lands (or before the SDMX series catches up with it): say the rate is not published yet rather than walking back and calling today a non-publication day. Judge "today" by the Israel date, not the machine's clock.

The series runs back before the September 4, 1985 currency reform, when one new shekel replaced 1,000 old shekels. Pre-reform observations are expressed in new-shekel terms (USD on 1984-06-01 reads 0.2028), not as the old-shekel figure quoted at the time, and before February 24, 1980 the currency of the day was the Israeli pound (lira), not the shekel at all. Label any such rate accordingly.

### Step 3: Calculate Conversion
```
If converting FROM NIS:
  result = amount / rate * unit

If converting TO NIS:
  result = amount * rate / unit

If converting between two foreign currencies:
  nis_amount = amount * rate_source / unit_source
  result = nis_amount / rate_target * unit_target
```

**Converting between two FOREIGN currencies is a derived number, not a published rate.** The Bank of Israel publishes a shekel rate per currency and nothing else, so a USD/EUR figure obtained by dividing two shekel rates was never set, published or date-attributed by the Bank of Israel. Label it as derived, never as the shaar yatzig, and for a tax figure translate each foreign amount into shekels against its own representative rate instead of cross-converting. If a dated cross conversion would draw its two legs from different publication days, do not stamp one date on it: quote each leg separately.

Some low-value currencies are published at very coarse precision. The Lebanese pound is published as 0.0003 per 10 units, a single significant figure, which bounds any converted total to roughly plus or minus 17 percent. That published figure is the official representative rate, so it is not wrong to use it, but do not present the converted total as precise to the agora.

Note: Bank of Israel rates express how many NIS per unit(s) of foreign currency.
Example (illustrative; fetch the live/dated rate): USD rate around 2.97, unit = 1 means 1 USD is about 2.97 NIS.
Example (illustrative): JPY rate around 1.87, unit = 100 means 100 JPY is about 1.87 NIS.
Watch the precision on a small-unit currency: the Lebanese pound prints as 0.0000 NIS at four decimal places even though the converted total is correct, so widen the precision rather than reporting a zero rate.

### Step 4: Present Results
Format the result with:
- Converted amount (2 decimal places for NIS, appropriate precision for other currencies)
- Exchange rate used and the date it was PUBLISHED (from `lastUpdate` or the SDMX `TIME_PERIOD`), not the date of the query. If the caller asked for today and today is not published yet, say so explicitly rather than presenting the previous publication as today's rate
- This skill is not a trading feed, not a bank or credit-card conversion rate, and does not cover cryptocurrency. The representative rate is published once per business day for reference and reporting
- Source: "Bank of Israel representative rate (shaar yatzig)"
- Caveat: "Representative rate for reference. Actual bank rates may differ."

### Which date's rate applies (tax)
Establish which regime governs before picking a date, because the answer depends on it.

- **Foreign-source income (the Conversion Rules).** The Income Tax Rules (Conversion to NIS of Amounts Originating Outside Israel), 5764-2003, cover foreign-source income (hachnasat chutz, as defined in section 199 of the Ordinance), foreign taxes, and capital gains on foreign assets. Business or professional foreign-source income and its expenses are translated at the representative rate on the date the income was produced, accrued or incurred AND on the date it was received or paid (Rule 2): two events, two rates. Passive foreign income is translated at the rate on the day it was paid or received (Rule 3(a)). For foreign-source interest or linkage income, the investment behind it (the principal) is ALSO translated at the rate on the investment date and at the end of each tax year or on realisation, whichever is earlier (Rule 3(b)); passive income paid after the year in which it was reported uses that year-end rate and the payment-date rate (Rule 3(c)). So the December 31 rate does concern an individual with a foreign-source interest-bearing deposit. A foreign professional company's income and losses (Rule 4) and a controlled foreign company's undistributed profits and the related tax credit (Rule 5) are translated at the rate at the end of that company's tax year or assessment period; route the substance to an accountant.
- **An Israeli freelancer or company billing a foreign client from Israel** usually has Israeli-source income, which those Rules do not govern. Which of the two dates (invoice or payment) goes into the books depends on whether the books are kept on an accrual or a cash basis, so ask the user or their accountant instead of choosing one. Never silently convert once and drop the difference between the invoice-date and payment-date figures.
- **VAT on a service:** the VAT charge arises on receipt of the consideration, on the amount received (VAT Law section 24), so the payment date and the payment period's report govern, not the invoice date. Exception: a dealer whose turnover exceeds NIS 15 million a year and who must keep books under Schedule 11 of the Bookkeeping Instructions is charged when the service is given, as are some special cases such as related-party pricing or non-cash consideration (section 29(1a)). The VAT Law fixes the date and the amount received but names no exchange rate: if the client paid in shekels, or the bank converted on receipt, the shekels actually received may be the amount, so let the accountant decide which figure is used. Whether issuing a tax invoice (heshbonit mas, as opposed to a transaction invoice, heshbonit iska) before payment brings the reporting forward was not verified here; if one was issued, have the accountant confirm the period. A service to a foreign resident may be zero-rated under section 30(a)(5), which excludes a service also given in practice to an Israeli resident in Israel; deciding eligibility is a VAT question outside this skill.
- **Year-end revaluation of balances in a business's books, and foreign-currency loans:** how foreign-currency balances and loan drawdowns and repayments are revalued and where the exchange differences are booked is an accounting-treatment question this skill has no verified source for. Do not state a rule; route it to the accountant. The sourced year-end cases are the ones under Rules 3(b), 3(c), 4, 5 and 6 above and below.
- **Capital gain on a foreign asset:** TWO different dates, not one (Rule 7). Translate the original COST at the rate on the acquisition date or the payment date, whichever is earlier, and the PROCEEDS at the rate on the sale date or the date payment was received, whichever is earlier, then compute the shekel gain from those two shekel figures. Converting a net foreign-currency gain at a single date is a different number. **Caution for an individual's foreign-currency securities:** for a security held by an individual that is denominated in, or linked to, foreign currency, section 88 of the Ordinance treats the exchange rate as the index, so part of the nominal two-date shekel gain may be an inflationary amount taxed differently from real gain. Do not present the nominal shekel gain as the taxable gain; hand that computation to a capital-gains skill or an accountant.
- **Foreign tax paid (for a credit):** translated at the rate on the payment date if paid during or before the tax year; at the year-end rate if paid after the year but within 24 months of its end; at the payment-date rate if paid later than that (Rule 6).
- **Import VAT (depends on what is imported):**
  - **Imported GOODS** cleared from customs: VAT is charged on release from customs supervision (VAT Law section 26(a)), and the foreign-currency price is translated under the Customs Rules (Calculation of Price Denominated in Foreign Currency), 5749-1989. Their "representative rate" is the Bank of Israel rate **plus 0.5%** (Rule 1). Goods released between a Tuesday and the following Monday use the rate published on the preceding Friday, or the last rate published before it if there was none that Friday (Rule 2(a)); if the rate moved by a cumulative 3% or more between that Friday and the release date, the release-day rate applies instead (Rule 2(b)). If no published rate on the release day includes that change, the Ministry of Finance's published rate plus 0.5% applies. In arithmetic terms the uplift multiplies: customs rate = BOI rate x 1.005, not BOI rate + 0.5 NIS. The Tax Authority publishes the resulting customs rates in its currency-rate query system (link below; it opens in a browser but blocks automated fetches), so prefer reading the published figure over deriving it. The customs rate applies to the price of the goods and to any other foreign-currency amount that customs law takes into account (Rule 2); customs duty and other levies on the import are then added to form the import-VAT base (section 11(a)). What enters the customs value is a customs question outside this skill.
  - **Imported INTANGIBLE goods** (and printed matter imported by post): VAT is charged when the foreign currency is bought from a financial institution to pay for them, or transferred to the seller, whichever is earlier (section 26(b)), and the price is the shekel value at the currency's **purchase rate** at that moment (section 11(b)), not the representative rate.
  - **Imported SERVICES** from a foreign resident: the buyer pays the VAT itself unless the buyer holds an invoice for the transaction (reverse charge, VAT Regulations, regulation 6D), and the customs uplift does not apply. Whether a given foreign SaaS is a service or an intangible good is a classification question, and this skill has no verified source fixing which exchange rate applies to a reverse-charge service, so do not present any rate as the legally required one; have the accountant confirm.

## Examples

### Example 1: Simple USD to NIS
User says: "Convert 1000 dollars to shekels"
Result: "1,000 USD = X NIS (at the live Bank of Israel representative rate; fetch the dated rate before quoting a figure)."

### Example 2: Historical Rate
User says: "What was the dollar rate on January 1, 2026?"
Result: Fetch the SDMX RER_USD_ILS series. Jan 1, 2026 is New Year's Day, a non-publication day, so walk back to the most recent earlier publication (December 31, 2025) and say which date you used. Do not jump forward to January 2.

### Example 3: Tax-Relevant Rate
User says: "I invoiced a German client 2,500 EUR on December 15, 2025 and was paid on January 6, 2026. Which rate goes in my VAT report?"
Result: under section 24 the VAT charge on a service generally arises on receipt of the consideration, so the period that includes the payment date (January 6) is the likely one rather than December, unless the user is a dealer above NIS 15 million keeping books under Schedule 11. Ask whether a tax invoice was issued in December, and have the accountant confirm the period. The VAT Law names no exchange rate, so the January 6 SDMX EUR rate is a reasonable conversion of the euros received; if the payment arrived already converted into shekels, the accountant may use the shekels actually received. Flag that a service to a foreign resident may be zero-rated, and that the income-tax books may also need the December 15 rate depending on whether they are kept on an accrual or a cash basis.

## Bundled Resources

### Scripts
- `scripts/fetch_rates.py` - Fetches official Bank of Israel representative exchange rates (shaar yatzig) and performs currency conversions to/from NIS. Uses the live JSON endpoint for current rates and the SDMX EXR series for historical date lookups (with publication-day walk-back). On a fetch failure it fails loud (prints an error, exits non-zero) and never substitutes sample rates for a real conversion; illustrative sample output is only available behind the explicit `--demo` flag. Run: `python scripts/fetch_rates.py --help`

### References
- `references/boi-api-guide.md` - Bank of Israel exchange rate API documentation: the live JSON endpoint and its fields, the SDMX EXR historical series, update schedule, and the import-VAT customs-rate caveat. Consult when troubleshooting API calls or understanding rate publication timing.
- `references/currency-codes.md` - Supported currency codes with Hebrew names, typical NIS rate ranges, and unit values (important for JPY and other multi-unit currencies). Consult when parsing user currency requests or handling unit-based conversions.

## Reference Links

| Resource | URL |
|----------|-----|
| BOI exchange rates page | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ |
| Live JSON rates endpoint | https://www.boi.org.il/PublicApi/GetExchangeRates |
| BOI SDMX EXR historical series | https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_USD_ILS |
| BOI explanatory notes (publication time, non-publication days) | https://www.boi.org.il/en/economic-roles/financial-markets/explanatory-notes-to-the-representative-exchange-rates/ |
| Tax Authority customs currency-rate query (opens in a browser) | https://www.gov.il/apps/taxes/currencyGates/ |
| Customs Rules (foreign-currency price), 5749-1989 | https://www.gov.il/BlobFolder/service/exchange-rate/he/Service_Pages_Customs_Foreign-currency.pdf |
| Income Tax Conversion Rules, 5764-2003 | https://www.nevo.co.il/law_html/law01/999_233.htm |

## Recommended MCP Servers

For live exchange rate data, pair this skill with:

| MCP Server | What it provides | Install |
|------------|-----------------|---------|
| **boi-exchange** | Official Bank of Israel daily representative rates (sha'ar yatzig) for the published currencies, historical rate series, rate change calculations, and direct currency conversion via BOI SDMX API. No API key required. | [Install boi-exchange](https://agentskills.co.il/en/mcp/boi-exchange) |

When the `boi-exchange` MCP is available, use its tools for real-time conversions instead of the static reference tables above. The MCP provides the official representative rate (shaar yatzig) which is the rate Israeli tax rules require for the transaction date.

## Gotchas
- The official NIS currency code is ILS (ISO 4217), but Israelis colloquially say "shekel" or "shekalim". Agents may not recognize "NIS" as a valid currency code or confuse it with the pre-1985 old shekel, whose ISO code was ILR.
- Bank of Israel publishes ONE representative rate per currency per day (no separate buy/sell rates). Its explanatory notes say it is currently published soon after 15:15, or soon after 12:15 on Fridays, holiday eves and some other Jewish holidays, while warning that the time is not fixed. No rate is set on Saturdays, Sundays, Israeli holidays, Christmas Day, New Year's Day or Easter. Agents may fetch a rate before publication and get the previous publication's rate without indicating it is stale; the `lastUpdate` stamp, not the clock, settles it.
- Only the official Bank of Israel published currencies have a representative rate (currently 14: USD, GBP, JPY, EUR, AUD, CAD, DKK, NOK, ZAR, SEK, CHF, JOD, LBP, EGP). The skill is not a general FX converter for every world currency.
- NIS amounts use a comma for thousands and a period for decimals (1,234.56). Agents may use the European convention (1.234,56). Symbol placement differs by language: the Unicode CLDR Hebrew pattern puts the sign after the number (1,234.56 ₪), while English text usually puts it before (₪1,234.56).
- Where Israeli tax rules fix a conversion rate, it is the BOI representative rate (sha'ar yatzig) for the relevant date, not a live forex rate. For import VAT on goods use the customs rate (representative rate plus 0.5%, fixed weekly from the preceding Friday) published by the Tax Authority; intangible goods use the bank purchase rate when the currency was bought or transferred. Agents may use real-time rates that are not legally valid for tax reporting.

## Troubleshooting

### Error: "Rate not available for date"
Cause: Requested date is a Saturday, Sunday, Israeli holiday, Christmas Day, New Year's Day or Easter, or a future date.
Solution: For a past non-publication day, use the most recent earlier published date from the SDMX series and say which date you used. For a future date there is no rate yet: say so, and never substitute demo or sample rates. The helper script rejects future dates up front.

### Error: "Currency not supported"
Cause: Bank of Israel does not publish a representative rate for this currency (only the 14 listed currencies are covered).
Solution: There is no Bank of Israel rate to quote. For foreign-source income, the Conversion Rules compute such a currency's rate from its conversion rate to the US dollar, so the tax figure is that currency's rate against the dollar times the Bank of Israel USD/ILS rate. The USD/ILS leg is the Bank of Israel rate; the currency-to-dollar leg must come from a source outside the Bank of Israel. Name that source, and label the result as derived, never as the shaar yatzig.

### Error: "CERTIFICATE_VERIFY_FAILED" from the helper script
Cause: verified on 2026-10-18 with python.org Python 3.13 on macOS. `edge.boi.gov.il` (the SDMX host) chains to the Sectigo Public Server Authentication Root R46, which the system bundle `/etc/ssl/cert.pem` lacked; the JSON host verified fine against that bundle while the SDMX host failed, so only historical lookups broke. Verified NOT to be a server fault: curl, which uses the macOS keychain, verifies both hosts.
Solution: The script retries with the `certifi` bundle when it is installed (`pip install certifi`), which contains R46. On python.org builds, running the bundled "Install Certificates.command" also fixes it. Never disable certificate verification.
