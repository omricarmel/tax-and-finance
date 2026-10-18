# Bank of Israel Exchange Rate API Guide

## Current Rates (live JSON endpoint)
- **URL:** `https://www.boi.org.il/PublicApi/GetExchangeRates`
- **Method:** GET (no authentication required)
- **Format:** JSON
- **Update time:** per the BOI explanatory notes, currently soon after 15:15 Israel time, or soon after 12:15 on Fridays, holiday eves and some other Jewish holidays. The notes stress the time is not fixed, so the response's `lastUpdate` is the authority. No rate on Saturdays, Sundays, Israeli holidays, Christmas Day, New Year's Day or Easter.

The legacy XML feed at `https://www.boi.org.il/currency.xml` no longer serves XML. It now redirects to the JSON endpoint above, so do NOT try to parse XML.

## JSON Response Structure
```json
{
  "exchangeRates": [
    {
      "key": "USD",
      "currentExchangeRate": 3.089,
      "currentChange": -0.4511762810183693200128907500,
      "unit": 1,
      "lastUpdate": "2026-10-16T09:22:04.9223221Z"
    }
  ]
}
```

Fields:
- `key` - currency code (e.g., USD, EUR, JPY).
- `currentExchangeRate` - NIS per `unit` of the foreign currency.
- `unit` - number of foreign-currency units the rate is quoted per (1 for most, 100 for JPY, 10 for LBP).
- `currentChange` - percentage move versus the previous publication (a percent, NOT an absolute NIS delta). Not used in conversion math.
- `lastUpdate` - ISO timestamp of when the rates were set.

## Historical Rates (SDMX EXR series)
The JSON endpoint's `?date=` parameter is ignored: it always returns the latest rate regardless of the date supplied. For a specific historical date (the rate that matters for tax), use the Bank of Israel SDMX EXR series.

- **URL pattern:** `https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_<CUR>_ILS`
- **Parameters:**
  - `startPeriod` (YYYY-MM-DD)
  - `endPeriod` (YYYY-MM-DD)
  - `format=csv`
- **Example:** `.../RER_USD_ILS?startPeriod=2026-01-01&endPeriod=2026-01-15&format=csv`

Parse the CSV: read `OBS_VALUE` (the rate) keyed by `TIME_PERIOD` (the date). The series omits non-publication days. If the exact requested date has no row, walk back to the most recent published date on or before it.

## Understanding Rates
- Rate = NIS per UNIT of foreign currency.
- UNIT varies by currency (usually 1, but 100 for JPY, 10 for LBP).
- Bank of Israel sets a single representative rate (shaar yatzig) per currency per day. There are no separate buy/sell rates.
- The BOI explanatory notes say the representative rates "have no official or legal standing" and bind a contract only if the parties stipulated them in advance. Their force for tax comes from the rules that adopt them, chiefly the Income Tax Conversion Rules, 5764-2003 (foreign-source income) and the Customs Rules, 5749-1989 (rate plus 0.5%).

## Import VAT and the customs rate
For import VAT and customs on GOODS, a price in foreign currency is translated under the Customs Rules (Calculation of Price Denominated in Foreign Currency), 5749-1989 (PDF: https://www.gov.il/BlobFolder/service/exchange-rate/he/Service_Pages_Customs_Foreign-currency.pdf):
- Rule 1: the customs "representative rate" is the BOI representative rate plus 0.5%.
- Rule 2(a): goods released between a Tuesday and the following Monday use the rate published on the preceding Friday; if none was published that Friday, the last rate published before it.
- Rule 2(b): if the rate moved by a cumulative 3% or more between that Friday and the release date, the release-day rate applies; if no published rate on the release day includes the change, the Ministry of Finance's published rate plus 0.5%.
- The uplift multiplies: customs rate = BOI rate x 1.005.

The Tax Authority publishes the resulting rates in its query system, https://www.gov.il/apps/taxes/currencyGates/ (a Cloudflare challenge blocks automated fetches; it opens normally in a browser). Prefer the published figure over a derived one. The customs rate applies to the price and to any other foreign-currency amount customs law takes into account (Rule 2); duty and other levies are then added for the import-VAT base (VAT Law s.11(a)).

Imported INTANGIBLE goods (VAT Law s.26(b)) are charged when the currency is bought from a financial institution or transferred to the seller, whichever is earlier, at the currency's purchase rate at that moment (s.11(b)). Imported SERVICES from a foreign resident are self-assessed by the buyer unless the buyer holds an invoice for the transaction (VAT Regulations reg. 6D), with no customs uplift; this skill has no verified source fixing the exchange rate for that case, so have an accountant confirm it.

## Published Currencies (14 total)
USD, GBP, JPY, EUR, AUD, CAD, DKK, NOK, ZAR, SEK, CHF, JOD, LBP, EGP.

This is the full set the Bank of Israel publishes a representative rate for. The skill is not a general FX converter for every world currency.

## Rate Limitations
- Saturdays, Sundays, Israeli holidays, Christmas Day, New Year's Day and Easter: no rate published (BOI explanatory notes).
- The Bank has no obligation to publish on any specific date and the time is not fixed.
- For missing dates, use the most recent published date before the requested date. For foreign-source income the Income Tax Conversion Rules, 5764-2003, make this the statutory rule.
- The SDMX series runs back before the 1985-09-04 currency reform (1 new shekel = 1,000 old shekels); earlier observations are expressed in new-shekel terms, and dates before 1980-02-24 fall in the Israeli pound (lira) era.
- Today has no SDMX row until its publication lands and the series catches up. A request for today must say "not published yet", not walk back as if today were a non-publication day. Use the Israel date.
