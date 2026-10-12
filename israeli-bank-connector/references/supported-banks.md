# Supported Israeli Banks and Credit Card Companies

Authoritative list reflects the `CompanyTypes` enum in [eshaham/israeli-bank-scrapers](https://github.com/eshaham/israeli-bank-scrapers/blob/master/src/definitions.ts). The library is the foundation for both `israeli-bank-mcp` and `il-bank-mcp`. Library version floor: `israeli-bank-scrapers >=6.9.x` (current release 6.12.2, 2026-09-29, re-verified against the npm registry on 12 October 2026; the `CompanyTypes` enum is unchanged from 6.9.0, still 18 entries). The package declares `engines.node >= 22.22.2`, so run Node 22.22.2 or newer for `israeli-bank-mcp` (22.0 to 22.22.1 is below the floor). `il-bank-mcp` builds its own Node into its Docker image.

Two capabilities landed in 6.9.0 that change what you can retrieve, so an older pin will
silently return less than the user expects: Leumi now exposes **savings accounts**, and Max
now exposes **credit card balances**. If a user says a Leumi savings account or a Max
balance is missing, check the installed version before debugging the scrape. 6.8.0
completed the Visa Cal frame implementation, and 6.7.9/6.7.10 fixed a Max login-page
failure (6.7.9) and an Isracard bot-detection problem (6.7.10), so a release before 6.7.9 is
likely to fail on Max, and one before 6.7.10 on Isracard, rather than merely return less.

Later releases added more of the same kind: 6.10.0 (2026-09-06) Isracard credit card
balances, 6.12.0 (2026-09-10) Leumi **foreign-currency accounts**, 6.12.1 more Visa Cal
balance fixes, and 6.12.2 (2026-09-29) a fix for Mizrahi's changed change-password page.
A Leumi foreign-currency account reports its transactions in that currency, so never add
them to a shekel total.

BOI Code column shows Bank of Israel bank identification codes. `-` means no separately-assigned code (the entity shares a parent's code or is not listed as an independent payment-system participant). **Sourcing caveat, added 27 August 2026:** the BOI page previously cited for this column ([Access to Payment Systems](https://www.boi.org.il/en/economic-roles/supervision-and-regulation/payment-systems-oversight/access-to-payment-systems/)) was rendered in a browser this cycle and is a landing page last updated 19/11/2023 that does not contain an identification-code list at all. The codes below are the conventional two-digit Israeli bank numbers and are useful for recognising a bank, but they are **not verified against a BOI publication in this skill**, and the previously-stated expansion from two to three digits by the end of December 2026 is likewise unverified and has been withdrawn as a factual claim. Never use a code from this table to construct a payment instruction; take it from the bank or from a current BOI publication.

## Banks

| Bank | Hebrew | BOI Code | israeli-bank-scrapers ID | Notes |
|------|--------|----------|--------------------------|-------|
| Bank Hapoalim | bank hapoalim | 12 | `hapoalim` | Login is `userCode` + password, not a username |
| Bank Leumi | bank leumi | 10 | `leumi` | Savings accounts from 6.9.0, foreign-currency accounts from 6.12.0 |
| Israel Discount Bank | bank discount | 11 | `discount` | Separate scraper from Mercantile |
| Mercantile Bank | bank mercantile | 17 | `mercantile` | Separate scraper (own loginFields: id, password, num); subsidiary of Discount but not subsumed |
| Mizrahi-Tefahot | mizrahi tefahot | 20 | `mizrahi` | 6.12.2 fixed detection of the bank's change-password page |
| FIBI (First International) | benleumi rishon | 31 | `beinleumi` | Separate scraper from Otsar HaHayal |
| Bank Otsar Hahayal | bank otsar hahayal | 14 | `otsarHahayal` | Separate scraper (own loginFields: username, password); part of FIBI group but not subsumed |
| Pagi Bank | bank pagi | 52 | `pagi` | Separate scraper |
| Union Bank | bank igud | 13 | `union` | Separate scraper from Mizrahi-Tefahot |
| Bank Yahav | bank yahav | 04 | `yahav` | History capped at six months (library README); login also needs a national ID |
| Bank Massad | bank masad | 46 | `massad` | Separate scraper |
| OneZero Digital Bank | onezero | 18 | `oneZero` | Supports a long-term two-factor token, which is a credential: store it like a password |
| Behatsdaa | bank behatsdaa | - | `behatsdaa` | Smaller institutional scraper |
| Beyahad Bishvilha | beyahad bishvilha | - | `beyahadBishvilha` | Smaller institutional scraper |

## Credit Card Companies

| Company | Hebrew | israeli-bank-scrapers ID | Notes |
|---------|--------|--------------------------|-------|
| Visa Cal (CAL) | visa cal | `visaCal` | Visa/Mastercard/Diners. Verify current ownership against Bank of Israel filings; card-issuer ownership has been shifting under BOI competition rulings |
| Max (formerly Leumi Card) | max | `max` | Mastercard/Visa |
| Isracard | isracard | `isracard` | Isracard/Mastercard |
| American Express Israel | amex | `amex` | Amex cards (issued via Isracard) |

## MCP Server Coverage

Not every scraper in the upstream library is exposed by every MCP wrapper. Check the specific MCP's tool list before assuming an account is reachable.

### israeli-bank-mcp (Motti Bechhofer)
- Directly wraps `israeli-bank-scrapers`. `fetch-transactions` returns the library's raw scrape result (`accounts[].txns[]`, amounts in `chargedAmount`), which the bundled script accepts as-is. Declares `israeli-bank-scrapers ^6.7.3`, a floor rather than a hard pin, so a fresh install resolves to the current release.
- **Coverage tracks the library, not its own README.** Its README bank list omits Pagi, but the server calls `SCRAPERS[bankId]` from the library rather than carrying a hardcoded list, so every entry in `CompanyTypes` is reachable. Do not treat the README omission as a coverage gap; it has been re-raised as one before.
- Two tools (`fetch-transactions`, `two-factor-auth`) and one resource (`banks://list`). It fetches. It does not analyse.
- Has a `two-factor-auth` tool, which cannot complete the OneZero token flow (see Authentication Notes).
- **Not published to npm** (the registry returns 404) and declares no `bin`, so it cannot be run with `npx`. Clone, `npm install`, `npm run build`, then run `node build/server.js`.
- Credentials come from environment variables only, never from tool arguments, so they stay out of the conversation history. Names are `<BANK_ID>_<FIELD>` derived by camelCase-to-upper-snake: `LEUMI_USERNAME`, `OTSAR_HAHAYAL_USERNAME`, `HAPOALIM_USER_CODE` (the field is `userCode`; the upstream README's `HAPOALIM_USERCODE` is wrong by the server's own rule). A missing variable is reported only as a generic `BANK_SCRAPER_ERROR`, not by name.
- Last pushed May 2026.
- Repo: <https://github.com/mottibec/israeli-bank-mcp>

### il-bank-mcp (Gilad Lekner)
- Docker-based deployment: `docker compose up -d` with the bank env vars set, and the MCP client runs `docker compose -f /path/to/il-bank-mcp/docker-compose.yml run --rm -i mcp-server`
- A monorepo: the scraper dependency lives in `packages/scraper`, which declares `israeli-bank-scrapers ^6.1.4`, and the committed `yarn.lock` resolves it to exactly 6.1.4. The Dockerfile runs `yarn install --immutable`, so every fresh build installs 6.1.4: before the 6.7.9 Max and 6.7.10 Isracard fixes and without anything added from 6.9.0 on. Updating the lockfile is the only way to move it.
- Last pushed June 2025
- Adds transaction analysis features (spending breakdowns, recurring charge detection)
- Uses SQLite for local data storage (`better-sqlite3`, no encryption layer declared), so the scraped history sits on disk in readable form
- Its README passes bank passwords on the `docker compose up` command line, which leaves them in shell history. Prefer an env file readable only by the user, kept out of git
- Repo: <https://github.com/glekner/il-bank-mcp>

## Sourcing note on the Notes column and the operational figures below

As of 12 October 2026 the Notes column carries only facts about the scraper itself (login
fields, history cap, release that added a capability), taken from the library's README and
release notes. Earlier cycles carried unsourced ownership and market-position notes and an
unsourced session lifetime; those were removed rather than carried a fourth time. The scraper
id column is diffed row by row against the library's `CompanyTypes` enum each cycle. The BOI
Code column remains unverified (see the caveat above).

## Authentication Notes
- Some providers require two-factor authentication (the library README: "Some companies require two-factor authentication"). The library does not answer the prompt itself: the caller supplies an OTP callback or, where supported (OneZero), a long-term token. `israeli-bank-mcp` exposes a `two-factor-auth` tool, but it creates a fresh scraper per call, so the OneZero trigger/get-token pair cannot complete through it; obtain the token with the library directly
- Bank scrapers use headless browser automation
- How long a bank session lasts is not documented by the library or found in a primary source, so do not design against a fixed window
- Some banks may temporarily block automated access
- Rate limiting varies by bank

## Data Available
- Account balances
- Transaction history. Per the library README: one year for most scrapers (Hapoalim, Leumi, Mizrahi, Otsar Hahayal, Visa Cal, Max, Isracard, Amex), one year minus a day for Discount and Mercantile, six months for Yahav. An older start date is clamped, not refused. Check what the scrape actually returned
- Credit card transactions
