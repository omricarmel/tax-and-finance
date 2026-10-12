# Bank of Israel + CBS API Reference

## Overview

The Bank of Israel provides public economic data through its "new series database" (Fusion Edge Server) using the SDMX 2.1 REST API at `edge.boi.gov.il`. The headline Consumer Price Index is published separately by the Central Bureau of Statistics at `api.cbs.gov.il`.

## Base URLs

Two BOI data paths are live and return the same observations:

```
https://edge.boi.gov.il/FusionEdgeServer/ws/public/sdmxapi/rest/data/{DATAFLOW}/{series}
https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/{DATAFLOW}/1.0/{series}
```

Both accept `format=csv` in addition to the default SDMX-XML. The v2 path requires the agency segment (`BOI.STATISTICS`) and the version segment (`1.0`); omitting either is what produces a 404.

The structure/metadata path (to list available dataflows) is separate:
```
https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/structure/dataflow/BOI.STATISTICS
```

**Notes that apply to every call:** send an explicit `User-Agent` header; use `startPeriod` / `endPeriod` (capital P); and bound the query. A dataflow queried with no date filter returns every series it holds with full history: `.../data/EXR/` is about 20 MB (35 series, earliest observation 1948-05-15) and `.../data/BR/` about 3 MB. Omitting the series segment is legitimate when you want every currency for one day, but only with a date filter: `.../data/EXR/?startPeriod=2026-08-26&endPeriod=2026-08-26` returns that day's series in a few kilobytes. Not all of them are exchange rates: `NER_ILS_BSK_PCT` / `NER_ILS_BSK_IDX` (trade-weighted basket), `EXR_STD_ACTUAL_USDILS` and `WEB_STD_IMPVOL_*` (volatility), and `RER_USD_ILS_GLBLIMP` / `RER_USD_ILS_LCLIMP`, which share the `RER_` prefix but carry `UNIT_MEASURE="NBRE"`. Keep only series named exactly `RER_<CUR>_ILS` with `DATA_TYPE="OF00"`.

## Dataflows

| Dataflow | Contents |
|----------|----------|
| `EXR` | Exchange rates, including the representative rate |
| `BR` | Bank of Israel policy rate (ריבית בנק ישראל) |
| `BIR` | Commercial-bank interest rates and volumes, excluding housing loans |
| `PRI` | BOI price indices and analytical price series |
| `ZCM` | Inflation expectations and the zero-coupon yield curve |
| `MAG` | Monetary aggregates |
| `TLB` | Telbor rates |

## Endpoints

### Exchange Rates (EXR)

Representative rates (sha'ar yatzig) are per-currency series named `RER_<CUR>_ILS`.

```
GET .../data/EXR/RER_USD_ILS?startPeriod=2026-01-01&endPeriod=2026-01-31
```

**Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| startPeriod | Start date (YYYY-MM-DD) | 2026-01-01 |
| endPeriod | End date (YYYY-MM-DD) | 2026-01-31 |
| lastNObservations | Return only the N most recent observations | 1 |
| format | `csv` for a flat table | csv |

**Do not use `lastNPeriods`.** The server accepts it, returns HTTP 200, and silently ignores it, handing back the entire series (USD/ILS runs back to 1948-05-15). `lastNObservations` is the parameter that actually limits the result, and it is the correct way to fetch "the latest published rate" without modelling weekends or the holiday calendar.

Series verified live: `RER_USD_ILS`, `RER_EUR_ILS`, `RER_GBP_ILS`, `RER_JPY_ILS`, `RER_CHF_ILS`, `RER_AUD_ILS`, `RER_CAD_ILS`, `RER_ZAR_ILS`, `RER_SEK_ILS`, `RER_NOK_ILS`, `RER_DKK_ILS`, `RER_JOD_ILS`, `RER_EGP_ILS`, `RER_LBP_ILS` (quoted per 10, `UNIT_MULT="1"`).

### Policy Interest Rate (BR)

```
GET .../data/BR/MNT_RIB_BOI_D?startPeriod=2026-01-01
```

`MNT_RIB_BOI_D` is the daily Bank of Israel policy rate, and it is the ONLY series in this dataflow that carries the announced ריבית בנק ישראל. The siblings are different rates and will each return a plausible percentage for the same day, so picking one by accident is the likeliest remaining mistake now that the dataflow is correct. Latest observations as fetched on 2026-10-12 (the policy rate was cut from 3.5 to 3.25 effective 2026-09-03):

| Series | What it is | Last observation |
|--------|-----------|-------|
| `MNT_RIB_BOI_D` | Announced policy rate | 2026-10-12: 3.25 |
| `MNT_RIB_EFYB_D` | Effective rate | 2026-10-11: 3.30323985186489 |
| `MNT_WIN_LN_D` | Credit-window (lending) rate | 2026-10-12: 3.75 |
| `MNT_WIN_DEP_D` | Deposit-window rate | 2026-10-12: 2.75 |
| `MNT_SHIR_D` | A sibling rate series that has at times carried an observation dated ahead of the policy series (2026-08-27 when the policy series ended 2026-08-26) | 2026-10-12: 3.25 |

Because series inside one dataflow can carry different last-observation dates, "the latest observation" and "today" are not interchangeable. Read the `TIME_PERIOD` you actually got back.

The policy rate is not the rate a borrower pays: prime-linked credit is priced at the policy rate plus a banking-convention spread plus the borrower's margin. Bank Hapoalim and Mizrahi-Tefahot both state prime as the Bank of Israel rate plus 1.5% (checked 2026-10-12). It is a bank convention, not a BOI series, so quote 1.5% as the current convention and still take prime from the bank's published prime rate.

**`BIR` is not the policy rate.** The dataflow list gives `BIR` as "ריביות וביצועים - לא לדיור", bank credit rates excluding housing. It resolves and returns plausible percentages, so using it for the policy rate produces a wrong answer rather than an error.

### Price Indices (PRI)

`PRI` carries BOI price-index and analytical series on assorted bases and scopes. **It is not the source for the headline CPI.** Use the CBS API below for any מדד figure a user relies on.

### CPI (CBS index API)

```
GET https://api.cbs.gov.il/index/data/price?id=120010&format=json&last=6
```

Index id `120010` is "מדד המחירים לצרכן - כללי". The response gives, per month, `currBase.value` (the index), `currBase.baseDesc` (the base period), `percent` (monthly change) and `percentYear` (year-on-year change).

Other parameters (from the CBS API documentation page "מדדי מחירים באמצעות API"): `startPeriod` and `endPeriod` in `mm-yyyy` form select a month range; `coef=true` adds `prevBase`, an array restating the month on every earlier base (`{"coeff", "baseDesc", "value"}`). The Hebrew and English documentation pages disagree on the `coef` default, so pass it explicitly.

```
GET https://api.cbs.gov.il/index/data/price?id=120010&format=json&startPeriod=01-2019&endPeriod=03-2019&coef=true
```

**Months come back on the base current at the time.** In a range crossing a rebase, January 2019 is 100.1 on "2018 ממוצע" while August 2026 is 105.8 on "2024 ממוצע". Compare on the older base via the newer month's `prevBase` (August 2026 on "2018 ממוצע" is 120.6943227684).

**Paging.** Responses carry a `paging` object and hold at most 100 months per page. `last=120` returned 100 months on page 1 and 20 on page 2 (`Page=2&PageSize=100`). A client that reads only page 1 silently loses the oldest months.

**This API never signals failure by status code.** An unknown index id returns HTTP 200 with `"month": null`; an undefined path returns HTTP 200 with an HTML error page. Validate the payload.

## Response Format

The API returns SDMX XML by default. Each series carries its metadata as attributes on the `<Series>` element, and each observation is an `<Obs>` element with the date and value as `TIME_PERIOD` / `OBS_VALUE` attributes:

```xml
<Series SERIES_CODE="RER_USD_ILS" FREQ="D" BASE_CURRENCY="USD"
        COUNTER_CURRENCY="ILS" UNIT_MEASURE="ILS" DATA_TYPE="OF00"
        DATA_SOURCE="BOI_MRKT" UNIT_MULT="0" CONF_STATUS="F" PUB_WEBSITE="Y">
  <Obs TIME_PERIOD="2026-08-26" OBS_VALUE="2.972" RELEASE_STATUS="YP"></Obs>
</Series>
```

Note that `<Obs>` elements are emitted with a separate closing tag, not self-closed. Parse by matching the element name and reading the attributes (handle a namespace prefix on the tag); do not match on the raw text shape.

`DATA_TYPE="OF00"` marks the representative rate series. "Representative" is not "legal": the BOI states the rates have no official or legal standing of their own and are used mainly for valuations and in contracts. Between contracting parties a rate binds only when stipulated; a statute can also adopt it directly (the Income Tax (Inflationary Adjustments) Law, which applied mainly to tax years 1985-2007, defined the exchange rate for a date as that day's representative dollar rate or the last one published before it). Apply whichever rule governs. `UNIT_MULT` is the power of ten the value is quoted per: `0` for most currencies, `2` for the Japanese yen (quoted per 100 JPY). Read it from the response rather than hardcoding a per-currency table. `RELEASE_STATUS` accompanies every observation; the codelist is not served on the public structure path, so treat the value as opaque rather than assuming it certifies finality.

## Rate Limits

- No authentication required for public data
- No official published limit; cache responses and keep request rates modest

## Data Availability

| Data | Publication Time | Frequency | Days |
|------|-----------------|-----------|------|
| Exchange rates | Soon after 15:15 Mon-Thu, soon after 12:15 Fri and holiday eves, Israel time (not fixed) | Business days (Mon-Fri) | No Sat/Sun, Israeli holidays, Christmas Day, New Year's Day, Easter, or other days the BOI does not publish (none on 2025-12-26); use the last rate on or before the date |
| Policy interest rate | Announced 16:00 on decision day, effective a few days later | 8 scheduled decisions in 2026 | Decision dates (BOI announcement-dates page) |
| CPI | ~15th of following month | Monthly | CBS publication |

## Alternative Data Sources

- **CBS (Lishkat HaStatistika):** https://www.cbs.gov.il/he/pages/default.aspx
  - CPI data, economic indicators, demographic data
- **TASE (Tel Aviv Stock Exchange):** https://market.tase.co.il/
  - Market data, index composition, bond yields. Blocks automated fetches; open in a browser.
- **data.gov.il:** https://data.gov.il/
  - Open government data portal

## Common Issues

- Weekend queries return empty data (no rates published Saturday/Sunday; Friday is a publication day, as it was in 2015, 2023 and 2025). For a specific date, `endPeriod=<date>&lastNObservations=1` returns the last rate published on or before it (2025-12-26 resolves to 2025-12-24, 3.186).
- The Jewish holiday calendar removes further publication days, and erev chag shifts publication times. Christmas Day, New Year's Day and Easter are non-publication days too (there is no USD/ILS observation for 2025-12-25 or 2026-01-01). Do not model the calendar; read the `TIME_PERIOD` the API actually returns.
- A bare dataflow query with no date filter returns the entire dataflow history, not an error and not an empty result. Always bound with `startPeriod`/`endPeriod` or `lastNObservations`.
- SDMX XML parsing requires a namespace-aware parser.
