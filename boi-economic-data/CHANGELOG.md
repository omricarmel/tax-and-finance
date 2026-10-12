# Changelog

## 1.5.0 - 2026-10-12

Fixed a silent CPI error in the script. The CBS index API publishes each month on the base that
was current at the time (January 2019 is 100.1 on the 2018 base, August 2026 is 105.8 on the 2024
base), and the script printed one "Base" header over the whole range, inviting a division across
a rebase. `--cpi` now requests the CBS chaining coefficients (`coef=true`), shows each row's
published base, and adds a column restating every month on the oldest row's base, with a warning
when a range spans several bases. On the 2018 base August 2026 is 120.69.

The CBS API pages its answer at 100 months. The script read only the first page, so
`--cpi-last` above 100 silently dropped the oldest months, usually the base month a contract
names. It now reads every page. New `--cpi-from MM-YYYY` / `--cpi-to MM-YYYY` fetch an exact
range (closes the historical-CPI item carried from 1.4.0).

Corrected the claim that the representative rate is "the official rate for tax calculations".
The Bank of Israel states the rates have no official or legal standing of their own; they bind
contracting parties when stipulated, and statutes can adopt them directly (the Income Tax
(Inflationary Adjustments) Law defines the exchange rate for a date as that day's representative
dollar rate, or the last one published before it). The skill now tells the agent to apply the
governing rule's date and fallback.

Corrected a false history carried since 1.3.0: the representative rate did not move to
Monday-Friday in January 2026. The BOI series shows Friday rates and no Sunday rates in 2015,
2023 and 2025, so the "agents trained on pre-2026 data fall back to Thursday" gotcha was wrong
and would have pushed historical weekend lookups to Thursday instead of Friday. The 1.3.0 entry
below is left as written, as history; this entry supersedes it. Publication time is now quoted as the BOI states it (soon after 15:15,
12:15 on Fridays and holiday eves, not fixed) instead of ~15:30 / ~12:30, and Christmas Day, New
Year's Day and Easter are documented as non-publication days. The Reference Links row now points
at the BOI explanatory notes, which render in a browser, instead of a bot-blocked page.

New `--date YYYY-MM-DD` returns the rate published on a date or the last one before it (the
fallback most rules use; 26 December 2025 resolves to 24 December), `--from`/`--to` fetch and
print a whole range, and `--average` prints its simple mean (246 published USD rates in 2025,
mean 3.4529). Documented the CBS linkage calculator, its date convention (month X is known from
the 16th of X+1) and its HTTP 500 for a future date. The Monetary Committee has 8 scheduled
decisions in 2026, not "about 6", each announced at 16:00 and effective a few days later; the
BR change points are effective dates. `--cpi --json` now returns an object carrying the bases,
whether the requested end month is unpublished, and whether every page arrived, instead of a
bare list. `--cpi-to` alone now means the `--cpi-last` months ending there, instead of every
month since 1951. Added LBP. Fixed two dead BOI statistical-information links and a TASE host
that no longer resolves, and dropped "tax brackets are updated annually by CPI" (unsourced).
The EXR dataflow carries non-rate series with the `RER_` prefix, so the filter is now the exact
series name plus `DATA_TYPE=OF00`.

Stated the prime spread: Bank Hapoalim and Mizrahi-Tefahot both publish prime as the policy rate
plus 1.5% (closes the item carried from 1.4.0), framed as a bank convention.

The script now reports a TLS certificate-verification failure as a local CA-bundle problem
instead of retrying it and blaming CBS connection resets, and uses certifi's CA bundle when
installed (verification stays on). Negative `--days` and other out-of-range arguments are
rejected up front. Refreshed the BR sibling-series table (policy rate 3.25 since 2026-09-03).
Removed a stray `version` key from both SKILL frontmatters.

## 1.4.0 - 2026-08-27

Corrected the interest-rate endpoint. Every previous version documented the `BIR` dataflow as
"Bank of Israel rate data". `BIR` is "Interest rates and business volume - exc. housing loans",
i.e. commercial-bank credit rates. The policy rate is the `BR` dataflow, daily series
`MNT_RIB_BOI_D`. Because `BIR` resolves and returns plausible percentages, the error could only
ever surface as a wrong number, never as a failure. Fixed in SKILL.md, SKILL_HE.md,
references/boi-api.md, references/domain-checklist.md, evidence.json and the script.

`--interest` now fetches the rate instead of printing links to the BOI website, and prints the
dates it changed (3.5% since 2026-07-09). This closes a gap deferred in both the 1.2.0 and 1.3.0
cycles, which had been searching for the headline series inside the wrong dataflow.

Added a CPI path. The headline index is the CBS index API, id 120010, and the skill now says so.
The BOI `PRI` dataflow, which the previous version pointed at for CPI, is not the published
index. New `--cpi` flag, with `--cpi-last N` to reach the base month a contract names.

Removed the script's fabricated-data fallback. On any parse failure it previously returned
hardcoded rates stamped with today's dates and printed them in the same format as real data.
It now exits non-zero on every failure path, and `--example` is the only source of sample
numbers and is labelled as such.

Documented three API behaviours that fail while looking like success: `lastNPeriods` is accepted
and silently ignored (use `lastNObservations`), an unbounded dataflow query returns the entire
history rather than an error (EXR is about 20 MB back to 1948-05-15), and the CBS index API
returns HTTP 200 for an unknown index id and for an undefined path. Added retry-with-backoff for
the CBS server's intermittent connection resets.

Corrected the claim that the older `sdmx/v2` path returns 404. It is live given the
`BOI.STATISTICS` agency and `1.0` version segments, and both paths accept `format=csv`.

Quotation units now come from the API's `UNIT_MULT` attribute rather than a hardcoded table, and
`--json` carries the unit, so the per-100 yen quote cannot be read as a per-1 rate.

Added the CPI linkage conventions a real calculation needs: madad yadua versus madad bagin, the
base period and the CBS linking coefficient across a rebase, and the floor clause. Added a
warning that the policy rate is not the rate a borrower pays.

Removed the assertion that the BOI edge server rejects the default urllib User-Agent; a request
carrying that exact agent string returns 200.

## 1.3.1 - 2026-08-11

Removed the CPI basket weight column. The CBS CPI page carries no weights and the index API exposes no weight field, so all six figures were unsourced.

