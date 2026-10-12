# Domain Checklist: boi-economic-data

Scope: fetch and present Bank of Israel + CBS economic data (policy rate, exchange rates, CPI). Category: tax-and-finance (developer/data skill).

## Must cover (core)
- The CORRECT, working BOI data paths: `ws/public/sdmxapi/rest/data/{DATAFLOW}/{series}` and `sdmx/v2/data/dataflow/BOI.STATISTICS/{DATAFLOW}/1.0/{series}`, both live, both accepting `format=csv`, with the explicit User-Agent and startPeriod/endPeriod requirements and the `<Obs TIME_PERIOD OBS_VALUE></Obs>` response shape.
- Queries must be bounded: a dataflow queried with no date filter returns every series with full history (EXR is ~20 MB back to 1948). Naming the series, or adding startPeriod/endPeriod or lastNObservations, is what keeps a call cheap. A date-bounded dataflow query is the correct way to get all currencies at once.
- `lastNObservations` limits the result; `lastNPeriods` is accepted and silently ignored. Documenting the wrong one is a silent full-history download.
- Exchange rates (sha'ar yatzig): EXR dataflow, RER_<CUR>_ILS series, representative rate (DATA_TYPE OF00), UNIT_MULT read from the response (JPY per 100), published once per business day, soon after 15:15 (soon after 12:15 on Fridays and holiday eves; the BOI says the time is not fixed), Mon-Fri only (the series shows the same Mon-Fri pattern in 2015, 2023 and 2025; there was no January 2026 change for this rate), with no rate on Israeli holidays, Christmas Day, New Year's Day, Easter or other days the BOI does not publish. The last rate published on or before a date (endPeriod + lastNObservations=1) is the fallback the Inflationary Adjustments Law definition uses.
- Annual average and year-end rate: no BOI average series for single currencies; simple mean of published business-day rates, year-end = last rate on or before 31.12.
- Legal status of the representative rate: no official or legal standing of its own (BOI explanatory notes); between parties it binds only when stipulated and the contract decides which date's rate applies, while statutes can adopt it directly (Income Tax (Inflationary Adjustments) Law s.1 definition of שער החליפין, with a last-published fallback).
- Madad yadua by date: the CBS linkage calculator treats month X as known from the 16th of X+1; the calculator endpoint (index/data/calculator/120010) links an amount between two dates.
- Policy interest rate: BR dataflow, daily series MNT_RIB_BOI_D. NOT the BIR dataflow, which is bank credit rates excluding housing and returns plausible wrong numbers.
- CPI: the CBS index API, id 120010 ("מדד המחירים לצרכן - כללי"), with its base period. The BOI PRI dataflow is explicitly NOT the headline index.
- CPI by month range (startPeriod/endPeriod, mm-yyyy), reading every page (the API pages at 100 months), and restating a cross-rebase range on one base via coef=true / prevBase. Each month is published on the base current at the time, so raw values across a rebase must never be divided.
- CPI-linkage conventions: madad yadua vs madad bagin, the base period and the need for a CBS linking coefficient across a rebase, and the floor clause (taniyat ritzpa).
- Failure semantics: the CBS index API returns HTTP 200 for an unknown id and for an undefined path, so payloads must be validated rather than status codes.
- A working helper script that fetches real data (correct URLs, correct parser, explicit User-Agent, TLS verification ON) and exits non-zero rather than emitting placeholder numbers.
- Gotchas: weekend/holiday gaps, representative-vs-realtime rate, CPI lag, BIR/BR confusion.
- Monetary Committee decisions: 8 scheduled in 2026, announced 16:00, each with a later effective date; the BR series carries effective dates.
- Policy rate vs prime: prime is the policy rate plus a bank-convention spread (1.5% at Hapoalim and Mizrahi-Tefahot, checked 2026-10-12) plus the borrower's margin.

## Should cover (advanced)
- Cross-analysis (mortgage, business, investment, import/export).
- CBS / TASE / data.gov.il alternative sources.
- Structure/metadata path to discover dataflow ids, with the ids named outright (EXR, BR, BIR, PRI, ZCM, MAG, TLB).

## Out of scope (explicit)
- Stock-market data (tase-stock-analysis). Re-litigated 2026-08-27: still out of scope, the sibling skill owns it and a user asking about share prices is not asking a BOI question.
- Currency conversion as a product (shekel-currency-converter). Re-litigated 2026-08-27: still out of scope; this skill supplies the representative rate, the sibling skill does the conversion UX.
- Inflation-expectations and zero-curve series (ZCM) and monetary aggregates (MAG) as computed outputs. Re-litigated 2026-08-27: an ordinary user of this skill would plausibly ask, so the dataflow ids are now NAMED in the Reference Links and reference file so a caller can reach them, but the skill does not add fetch flags for them. Reconsider if usage shows demand.
- CPI basket component weights as stated figures. Re-litigated 2026-08-27: the previous table carried "n/a" in every row, which conveyed nothing. Weights are revised periodically by the CBS and are not worth freezing into the skill; the skill now names the CBS basket publication as the place to read them.

- ITA year-average / year-end exchange-rate table for annual tax reporting. Added 2026-10-12 after the 1.4.0 cycle deferred it: a dedicated search (Hebrew and English, gov.il internal search) found no such ITA publication, so the skill must not claim one exists. A user asking for an annual average can compute it from the daily `RER_<CUR>_ILS` series. Reconsider if the ITA publishes one.
- Re-litigated 2026-10-12: stock-market data, currency conversion UX, ZCM/MAG fetch flags and CPI basket weights all stay out of scope for the reasons above; none became capturable in a way that changes that.

## Authoritative sources
- BOI new series database (Fusion Edge Server), dataflow list at sdmx/v2/structure/dataflow/BOI.STATISTICS.
- boi.org.il Data and Statistics (en/economic-roles/statistics), monetary-policy, press-releases, the 2026 interest-rate announcement dates page, and the explanatory notes to the representative exchange rates (legal standing, non-publication days, publication time).
- CBS API documentation page "מדדי מחירים באמצעות API" (startPeriod/endPeriod/coef).
- Bank published prime pages (Bank Hapoalim interest-update, Mizrahi-Tefahot index-table) for the prime spread.
- CBS index API (api.cbs.gov.il/index) and cbs.gov.il Consumer Price Index.
