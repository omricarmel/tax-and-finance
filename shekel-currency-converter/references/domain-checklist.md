# Domain Checklist: Shekel Currency Converter

Scope: converting foreign-currency amounts to/from NIS at the Bank of Israel
representative rate (sha'ar yatzig) for Israeli tax, VAT, and accounting use.
Used to review the skill for correctness and completeness.

## Must cover (a wrong answer here causes a wrong tax filing)

1. **Correct live current-rate source.** Use the live BOI JSON endpoint
   `https://www.boi.org.il/PublicApi/GetExchangeRates`. The legacy
   `currency.xml` no longer serves XML (it redirects to the JSON API).
   Source: live curl 2026-10-18 (HTTP 200, JSON body, 14 keys, undefined sibling path 404s as a negative control); evidence.json json-endpoint-shape, json-negative-control.
2. **Correct historical / tax-date rate source.** The JSON endpoint's `?date=`
   is ignored (always returns the most recent publication). A specific past date must come from the
   BOI SDMX EXR series `RER_<CUR>_ILS` (CSV, `OBS_VALUE` keyed by
   `TIME_PERIOD`). Source: live curl 2026-10-18 (weekend rows absent from the series); evidence.json json-date-ignored, sdmx-weekend-gap.
3. **Weekend/holiday walk-back.** The SDMX series omits Saturdays, Sundays, and
   Israeli holidays. For a non-publication date, use the most recent published
   rate on or before it, and tell the user which date was used. Verified:
   2026-01-01 (New Year's Day) -> 2025-12-31 rate 3.19.
   Source: live curl 2026-10-18; evidence.json sdmx-dec31.
4. **Correct unit basis.** Rate is NIS per `unit` foreign-currency units;
   unit is 1 for most, 100 for JPY, 10 for LBP, both in the JSON feed and in
   the SDMX series (`UNIT_MULT` exponent: USD=0, JPY=2, LBP=1). Conversion math
   must divide/multiply by unit. Source: SDMX JPY 2025-12-31 = 2.0365 per 100
   (UNIT_MULT 2); evidence.json json-units.
5. **Tax-date rule (foreign-source income).** Income Tax Rules (Conversion to NIS
   of Amounts Originating Outside Israel), 5764-2003: business income and expenses
   at the rate on the date produced/accrued/incurred AND on the date received/paid
   (Rule 2); passive income at the payment/receipt date (3(a)), with the principal
   behind interest/linkage income also at the investment date and each year end
   (3(b)) and late-paid passive income at year end and payment date (3(c)); foreign
   professional company and CFC at year end (4, 5); foreign tax per Rule 6; capital
   gains per Rule 7 (earlier of acquisition/payment, earlier of sale/receipt).
   Read on nevo.co.il 999_233 in a browser, 2026-10-18.
6. **Import VAT on goods uses the customs rate, NOT the bare representative rate.**
   Customs Rules (Calculation of Price Denominated in Foreign Currency), 5749-1989:
   representative rate + 0.5% (Rule 1); goods released Tue to next Mon use the
   preceding Friday's rate (Rule 2(a)); a cumulative move of 3% or more switches to
   the release-day rate (Rule 2(b)). Intangible goods: bank purchase rate at FX
   purchase/transfer (VAT Law ss.11(b), 26(b)). Reverse-charge services (VAT Regs
   reg. 6D): no customs uplift; exchange rate not fixed by any verified source, so
   the skill routes to an accountant. Verified 2026-10-18 from the gov.il PDF of
   the Customs Rules and the Tax Authority service page (browser).
6a. **Which regime sets the date.** The Conversion Rules 5764-2003 cover only
   foreign-source income, foreign taxes and capital gains on foreign assets
   (Rules 1-7). Israeli-source income billed in foreign currency follows the books'
   basis. VAT on a service is charged on receipt (VAT Law s.24; s.29(1a) exception
   above NIS 15 million). Added 2026-10-18 after the coverage audit.
7. **Single representative rate per currency per day** (no buy/sell split),
   published soon after 15:15 on regular days and soon after 12:15 on Fridays,
   holiday eves and some other Jewish holidays; none on Sat/Sun/Israeli holidays,
   Christmas Day, New Year's Day or Easter. Source: BOI explanatory notes
   (rendered in a browser 2026-10-18; the page is JS-rendered).

## Should cover

- **Supported-currency set is exactly 14** (USD, GBP, JPY, EUR, AUD, CAD, DKK,
  NOK, ZAR, SEK, CHF, JOD, LBP, EGP); not a general FX converter.
  Source: live JSON (14 keys); evidence.json json-fourteen-currencies.
- **Stale-rate awareness:** a rate fetched before the day's publication is
  the previous day's; flag it as not-yet-updated, and never call today a
  non-publication day before its rate lands. Source: BOI explanatory notes.
- **NIS formatting:** comma thousands / period decimal (1,234.56), never the
  European 1.234,56. Symbol placement depends on language: after the number in
  the CLDR Hebrew pattern (1,234.56 ₪), before it in English (₪1,234.56).
  evidence.json nis-format.
- **Cross-currency via NIS** for two foreign currencies (both must be published).
- **Fail-loud on fetch failure** so a stale/sample rate is never presented as an
  authoritative "shaar yatzig" figure for a tax computation.

## Out of scope

Re-litigated 2026-10-18 (would a user ask? has it become capturable?):

- Cryptocurrency and unofficial/grey-market exchange rates. Users do ask, but no
  official rate exists; still out of scope.
- Currencies BOI does not publish (outside the 14). Users do ask; the skill now
  answers with the Conversion Rules' USD-cross definition for foreign-source
  income instead of silence. The non-BOI USD leg remains out of scope.
- Bank buy/sell spreads and card-network conversion fees. Not capturable from an
  official source; still out of scope.
- Live machine-lookup of the weekly customs rate. REOPENED and partly resolved:
  the rule itself (+0.5%, Friday window, 3% switch) is now stated from the
  Customs Rules PDF, and the query system https://www.gov.il/apps/taxes/currencyGates/
  is linked. Machine lookup stays out of scope because the page sits behind a
  Cloudflare challenge.
- Zero-rating eligibility for exported services (VAT s.30(a)(5)), the
  inflationary-amount computation under Ordinance s.88/s.91, and customs-value
  composition: flagged in the skill, decided by a VAT or capital-gains skill.
- What a foreign-currency tax invoice or receipt must show (rate used, shekel
  equivalent): users do ask, but the governing Bookkeeping Instructions clause
  was not read this cycle; route to an invoicing skill until it is sourced.
- Revaluation of a business's foreign-currency balances and loans in its books:
  an accounting-treatment question with no verified source in this skill.

## Authoritative sources

- BOI live JSON rates: https://www.boi.org.il/PublicApi/GetExchangeRates
- BOI SDMX EXR series: https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_USD_ILS
- BOI representative-rate explanatory notes (schedule, single-rate): https://www.boi.org.il/en/economic-roles/financial-markets/explanatory-notes-to-the-representative-exchange-rates/
- Israel Tax Authority customs/exchange rate service (bot-blocked to automated fetches; read in a browser): https://www.gov.il/he/service/exchange-rate
- Customs Rules (foreign-currency price), 5749-1989 (PDF, curl-readable): https://www.gov.il/BlobFolder/service/exchange-rate/he/Service_Pages_Customs_Foreign-currency.pdf
- VAT Law and VAT Regulations (full text): he.wikisource.org
- Income Tax Rules (Conversion to NIS), 5764-2003: https://www.nevo.co.il/law_html/law01/999_233.htm

The Tax Authority customs-rate query system is https://www.gov.il/apps/taxes/currencyGates/ (the shaarolami-query host suggested in an earlier review 404s).
