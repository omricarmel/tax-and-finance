---
name: tranzila-payment-gateway
description: Integrate Tranzila payment processing into Israeli applications -- covers iframe payments, tokenization, installments (tashlumim), refunds, 3D Secure, and Bit wallet. Use when user asks to accept payments via Tranzila, integrate Israeli credit card processing, set up "slikat ashrai", handle tashlumim (installment payments), create payment tokens, process refunds through Tranzila, or mentions "Tranzila", "tranzila API", "secure5", or Israeli online payments. Supports both legacy CGI endpoints and modern API V2. Do NOT use for Cardcom integration (use cardcom-payment-gateway), general accounting, or non-payment financial queries.
license: MIT
compatibility: Requires network access for Tranzila API calls. The bundled validator needs Python 3. Works with Claude Code, Cursor, Codex, Windsurf, OpenCode, Gemini CLI and GitHub Copilot.
---

# Tranzila Payment Gateway

## Overview

Tranzila, part of the Interspace group, is one of Israel's leading payment processors (solek). It connects to the Shva network (reshet shva) -- Israel's central card processing infrastructure -- and supports all Israeli card issuers: Isracard, Visa Cal, and Max (formerly Leumi Card).

This skill guides integration with Tranzila for accepting credit card payments (slikat kartis ashrai) in Israeli applications.

**Official docs:** `https://docs.tranzila.com/`

**Test credentials:** ask Tranzila support for the sandbox card numbers for your terminal, and configure the terminal for sandbox mode via the Tranzila dashboard. Test-card values circulating in blog posts and older versions of this skill are not published by the vendor and should not be treated as valid.

## Instructions

### Step 1: Choose Integration Pattern

Help the user select the right approach based on their needs:

| Pattern | Hebrew | PCI Scope | Best For |
|---------|--------|-----------|----------|
| **Iframe** | daf tashlum mutman | Smallest (typically SAQ A) | Quick integration, minimal compliance |
| **Hosted Fields** | sdot mitarachim | Small (SAQ A or A-EP, see below) | Custom checkout UX with low PCI burden |
| **API V2 (server-to-server)** | sharat le-sharat | Largest (typically SAQ D) | Token charging, recurring, refunds |

The SAQ mapping is the PCI Security Standards Council's, not Tranzila's, and the acquirer confirms it. For the iframe, SAQ A r1 (in force since 31 March 2025) dropped requirements 6.4.3 and 11.6.1 and added an eligibility criterion: the merchant "has confirmed that their site is not susceptible to attacks from scripts that could affect the merchant's e-commerce system(s)". PCI SSC FAQ 1588 applies it to pages that EMBED the processor's form (an iframe), not to plain redirects, and lets the merchant meet it with script protections like those in 6.4.3 and 11.6.1 or with written confirmation from the PCI DSS compliant processor. So "iframe means nothing to do" is wrong. Hosted Fields also injects Tranzila iframes, but whether that lands on SAQ A or A-EP is the acquirer's call.

Most Israeli merchants start with **Iframe** for collecting payments, then use **API V2** for server-side operations like token charging and refunds.

### Step 2: Set Up Authentication

Tranzila uses different credentials depending on the integration:

**For Iframe / Legacy CGI:**
- `supplier` -- Terminal name (provided by Tranzila)
- `TranzilaPW` -- Transaction password

**For API V2 (api.tranzila.com/v1):** authentication is a 4-header HMAC-SHA256 handshake, NOT a single key header. Every request must send all four:
- `X-tranzila-api-app-key` -- your public application key
- `X-tranzila-api-request-time` -- current Unix time in SECONDS
- `X-tranzila-api-nonce` -- a random nonce (about 40 bytes)
- `X-tranzila-api-access-token` -- `hmac_sha256(secret + request_time + nonce, app_key)` (HMAC-SHA256 of the app key, keyed with secret concatenated with the request-time and nonce)

You get a public app key and a secret on enrolment. A request with only the app key is rejected, and the secret must never reach the browser, so call the API from your server only. Base URL `https://api.tranzila.com`: `/v1` for payments, `/v2` for Handshake and standing orders. Confirm the concatenation on the Authentication page before shipping.

Remind the user to store credentials securely (environment variables, secrets manager) and never commit them to source control.

### Step 3: Implement the Payment Flow

#### Option A: Hosted Fields (Recommended for Custom UX)

Hosted Fields let you design your own checkout form while Tranzila's iframes, injected into your containers, take the card input:

1. Load `https://hf.tranzila.com/assets/js/thostedf.js` on the payment page
2. Create block-level containers (a `div`, not a `span`) for the card number, the expiry, and the CVV where your acquirer agreement requires it
3. **Server-side, create a handshake first.** The vendor states that all use of Hosted Fields requires the handshake: `POST https://api.tranzila.com/v2/handshake/create` with `terminal_name` and `sum` (and the four HMAC headers) returns a `thtk`, which you pass to the page
4. On submit, call `fields.charge({terminal_name, amount, thtk, notify_url, ...})`. **Tranzila performs the charge itself** and hands the result to your browser callback; it is not a tokenise-then-charge-from-your-server flow. Add `tokenize: true` for a reusable token in `transaction_response.token`
5. **Always set `notify_url`** (the server-to-server IPN). Without it the result exists only in the browser, so a closed tab after an approved charge leaves a paid order your server never heard about. Verify the `response_hash` before marking the order paid

Hosted Fields uses its own key names (`payment_plan`, `total_installments_number`, `tran_mode`, `card_holder_id_number`) and `force_txn_on_3ds_fail` defaults to `Y`; see `references/api-v2-flows.md`.

> **Callback integrity: two mechanisms, do not confuse them.** Never trust a POST to your notify page (`notify_url_address` on the iframe, `notify_url` on Hosted Fields and Bit) on its shape alone.
> - **Response Hash** authenticates a Hosted Fields response, which carries a `response_hash` (the transaction API pages document none); remove it, hash the rest with the secret from Tranzila support (`requested_by_user` selects a personal secret), and compare. The vendor describes the concatenation only in prose, so confirm the exact string with support.
> - **Handshake V2 (`thtk`) does not sign callbacks.** It locks the amount before the payment page loads; a tampered sum is refused with "Illegal Operation 912791".
>
> The iframe Notify POST has no documented signature, and the amount and any reference you put in the iframe form are visible to the buyer, so matching on them authenticates nothing. **Before fulfilling, confirm the transaction from your server** with the documented Transactions API (`https://api.tranzila.com/v1/transactions`, or `https://report.tranzila.com/v1/transaction` with filters), never with `myid`; details in `references/api-v2-flows.md`.

**Callback and redirect parameter names differ by product.** On the **iframe** they are `success_url_address`, `fail_url_address` and `notify_url_address` (the "Notify" page receives the transaction data as actually performed). The bare `notify_url` is the name used by Hosted Fields, the 3DS API and Bit; on the iframe it is simply not the parameter. Sending `notify_url` to `iframenew.php` means no webhook ever arrives: the customer is charged and the order is never fulfilled.

#### Option B: Iframe Integration (Quick Start)

1. Embed the Tranzila iframe in your checkout page:
   - URL: `https://directng.tranzila.com/{supplier}/iframenew.php` (DirectNG). The old `https://direct.tranzila.com/{supplier}/iframenew.php` is marked "Legacy Deprecated", and the old iframe page says official support ends on **1 January 2027**, so do not build anything new on it and migrate existing integrations
   - Send the parameters by POST from your server-rendered form (the vendor recommends POST over GET): `sum`, `currency`, `cred_type`
   - `tranmode` selects the mode: `A` standard charge (the default behaviour), `V` verification (J5), `N` verification (J2), `J` standing-order initiation, `K` create a token without charging, and the token variants `AK`, `VK`, `NK`. There is no `J4` mode, and the iframe does not create a token unless you ask for one

2. Handle the response via your `notify_url_address`:
   - Tranzila POSTs results to your server
   - Check `Response` field: `000` = approved
   - Store `TranzilaTK` (token) for future charges

3. Lock the amount with Handshake V2 (recommended):
   - Before rendering the iframe, call `POST https://api.tranzila.com/v2/handshake/create` and pass the returned `thtk` with the other iframe parameters. A `thtk` is valid for 20 minutes. The older `/v1/handshake/create` is deprecated
   - The vendor lists the Token Module (a paid module) as a requirement, and on the iframe you also turn it on under Settings, Terminal, iFrame, Advanced. Once enabled, every iframe transaction without a valid `thtk` is rejected, so deploy the server-side call first

#### Option C: Server-to-Server (API V2, or the legacy CGI)

For token charging, refunds and other no-card-entry operations. **Prefer API V2.** The legacy card CGIs on `secure5.tranzila.com` (tranzila31, 36a, 31tk, 71u) are no longer described on docs.tranzila.com (checked 2026-10-18); they still answer, but an unregistered caller gets "Transactions are not allowed from this location", so confirm access with support before depending on one.

**Charge a token on API V2:** `POST https://api.tranzila.com/v1/transaction/credit_card/create` with the token in `card_number`, `expire_month` / `expire_year` (and the CVV where required), and **the amount as an `items` array** (`name`, `type`, `unit_price`, `units_number`): there is no `sum` field. A token replaces only the card number, and a non-PCI-certified merchant must never send a raw card number to this API.

**Charge a token on the legacy CGI:**
```
POST https://secure5.tranzila.com/cgi-bin/tranzila31tk.cgi
Content-Type: application/x-www-form-urlencoded

supplier={terminal}&TranzilaPW={password}&TranzilaTK={token}&expdate={MMYY}&sum={amount}&currency=1&cred_type=1
```

**Process a refund:**
Refunds run on their own endpoint and need credentials the charge request does not use.

- **Legacy CGI:** POST to `https://secure5.tranzila.com/cgi-bin/tranzila71u.cgi` with `tranmode=C{index}` (the index of the original transaction), plus `supplier`, `sum`, `currency`, `TranzilaTK`, `expdate`, `cred_type`, `TranzilaPW`, **`CreditPass`** and **`authnr`**. `CreditPass` is a separate credit password that has to be obtained from Tranzila and enabled on the terminal, so a refund flow that was never tested end to end usually fails on it first. This field list comes from the tranzilajs client, not from the current vendor docs, so treat it as legacy.
- **API V2:** `POST https://api.tranzila.com/v1/transaction/credit_card/create` with `txn_type` set to `credit` (return funds), `cancel` (cancel a debit or credit) or `reversal` (release a credit limit taken by a J5), referencing the original with `reference_txn_id` **and `authorization_number`, which is required for all three** (missing it returns 22101). Store the approval number when you charge.

Decide which of the two you are on before writing the code: the parameter names do not carry across.

Consult `references/api-parameters.md` for the complete parameter reference.

### Step 4: Handle Israeli-Specific Payment Types

Israeli payments have unique features that differ from international processing:

**Installments (Tashlumim):**
- Set `cred_type=8` for installments (`cred_type=6` is the card company's own credit plan, which is a different product)
- Parameters: `npay` (number of payments minus 1), `fpay` (first payment), `spay` (subsequent payments)
- The sum of `fpay + (npay * spay)` must equal the total `sum`
- Not all terminals are authorized for installments (you get an error if the terminal is not enabled for them; check the exact code in the official table)

**Credit Types (cred_type):**

| Value | Type | Hebrew |
|-------|------|--------|
| 1 | Credit card, a regular single charge | ashrai ragil |
| 6 | Credit installments (kredit): the customer needs credit authorisation from the card issuer, and only `npay` is sent, minimum 3 | kredit |
| 8 | Installments | tashlumim |

These are the only three values the vendor's iframe table publishes; the 2, 3, 5 and 9 in older guides are undocumented, so do not send them.

**Currency codes (matbea):**

| Code | Currency | Hebrew |
|------|----------|--------|
| 1 | ILS (Shekel) | shekel chadash |
| 2 | USD | dolar |
| 978 | EUR | euro |
| 826 | GBP | lira sterling |

Euro and Sterling use their ISO 4217 numeric codes; the `3` and `7` in older guides are undocumented.


**These parameter names are the iframe and legacy-CGI ones.** API V2 renames every one of them (`txn_currency_code` with ISO alpha codes, `payment_plan` and `installments_number`, `expire_month` / `expire_year`, `card_holder_id`); the full mapping is in `references/api-parameters.md`.

**Israeli ID (teudat zehut):**
Some transactions require `myid`, the 9-digit Israeli ID (mispar zehut). Under the Privacy Protection Law and Amendment 13 it is regulated personal data: keep it out of plain logs and analytics, and do not retain it beyond its purpose.


**Prevent duplicate charges with `DCdisable`.** Send a unique value per transaction (max 254 characters); Tranzila deduplicates against it for up to 24 hours at parent-terminal level, and a transaction that FAILED is not checked, so a genuine retry still goes through. Enable it as field 20 under "Additional Fields for Transaction" in my.tranzila on the parent and child terminals. Never blind-retry a request whose outcome you did not read; code 425 (duplicate record) is what a double submission looks like afterwards.

**J5 authorizations have to be captured.** `verify_mode=5` (J5) takes a credit limit on the amount without charging it. The charge itself is a separate call with `txn_type=force`, and `txn_type=reversal` releases the limit if you decide not to collect. A subscription that starts with a J5 and never issues the capture never collects its first payment.

**Iframe extras worth knowing.** `google_pay=1` and `apple_pay=1` add those wallets. `bit_pay=1` adds a Bit payment option to the iframe, which is a one-line alternative to a full Bit API integration for iframe merchants. `maxpay` sets a maximum number of installments, and the vendor's rule is explicit: pass either `npay`, `fpay` and `spay`, or `maxpay`, never both together.

### Step 5: Implement Tokenization for Recurring Payments (hora'ot keva)

Tokens (not to be confused with the asmachta, the approval number) let you charge returning customers without handling card data again:

1. **Create token during first payment:**
   - Iframe: pass `tranmode=K` (token only) or `AK` / `VK` (charge or verify, plus token) to get a `TranzilaTK` back
   - Hosted Fields: `tokenize: true`. API V2 has no `tranmode`, and a non-PCI-certified merchant must tokenise through the iframe or Hosted Fields, never by posting a card number to the API

2. **Store the token securely:**
   - Treat the token as an opaque string. The vendor does not publish a fixed length or format, and tokens seen in the API V2 documentation are alphanumeric and longer than the legacy CGI ones, so never validate it by length or assume the last four digits match the card
   - Store token, expiry date, and card last-4 in your database
   - Token has no value without your terminal credentials
   - **Never store the CVV / CVV2 after authorization, and never store the full card number.** PCI DSS requirement 3.3.1 prohibits retaining sensitive authentication data (CVV, full magnetic-stripe or chip data, PIN) once the transaction is authorized, even encrypted. Storing the token, the expiry and the last four digits is the whole of what you keep. This applies no matter which integration pattern you chose, and it is the single most common way a merchant loses its compliance posture

3. **Charge the token later:**
   - API V2: the token goes in `card_number` on `/v1/transaction/credit_card/create`, with `expire_month`, `expire_year` and an `items` array for the amount
   - Legacy CGI: `/cgi-bin/tranzila31tk.cgi` with `TranzilaTK`, `expdate`, `sum` and `currency`

### Step 6: Add 3D Secure (if required)

3D Secure V2 adds cardholder authentication. On the API it is requested per transaction with `activate_3ds: "Y"` and a `3ds_settings` object carrying the customer's browser data; consult `references/3ds-flow.md` for the full flow. Key points:
- 3DS changes the payment flow to include a bank authentication step
- Response includes additional fields for authentication status
- Some Israeli issuers may not support 3DS for all card types

### Step 7: Accept Bit Payments

Tranzila supports Bit through a **dedicated Bit API** (`Bit - Init`, `Bit - Refund` under `https://api.tranzila.com/v1`, same 4-header HMAC auth), not a flag on the card CGI.

1. Call `POST /v1/transaction/bit/init` with the required `success_url`, `failure_url`, `notify_url` and `items` (the amount comes from the items)
2. Display the returned `sale_url` in an iframe on your page; it shows the QR code and a phone-number field
3. Customer approves payment in the Bit app
4. Tranzila sends the result to your `notify_url` (Bit API naming)
5. Bit refunds use the dedicated Bit Refund endpoint, not the card refund flow

**Bit constraints (from the docs):** NIS only, sum above 5 NIS, and a Visa or Isracard identifier (**Max-only merchants are not offered Bit**). The Bit page says Hosted Fields and 3DS are not supported, yet the Hosted Fields page documents `fields.chargeBit()`; confirm with support before building Bit on Hosted Fields. On the iframe, Bit is `bit_pay=1`; there is no `bit=1` / `bit_url` on the legacy CGI. Full Bit Init contract: `references/api-v2-flows.md`.

### Step 8: Generate Payment Request Links

Payment Requests (TRAPI) send a Tranzila-hosted payment link by email or SMS, with no checkout page to build: `POST https://api.tranzila.com/v1/pr/create` with the four HMAC headers, and you confirm payment through the Transactions API. Useful for phone orders and invoicing. It answered an unauthenticated probe with HTTP 200 and `"code":401` in the body, so read the body, not the status.

### Step 9: Set Up Standing Orders (Recurring Payments)

For automated recurring billing beyond simple token charging, Tranzila offers Standing Orders:

1. Create the standing order with `POST https://api.tranzila.com/v2/sto/create` and change it with `/v2/sto/update`. **The V1 create and update endpoints are deprecated and no longer supported**; `/v1/stos/get` (list STOs) is still the live read endpoint because it has no V2 replacement yet
2. Tranzila charges the customer on schedule
3. Monitor results through the list endpoint or your notify page

Two other routes the docs describe: on the iframe, the My Billing module's `recur_*` parameters (`recur_transaction` 4 / 5 / 7 for monthly, quarterly, yearly, `recur_start_date`, `recur_payments`, `recur_sum`); and on the transaction API, `txn_type=verify` with `verify_mode=6` to initialise, then `txn_type=sto` with `reference_txn_id` for each charge. Standing orders and My Billing are paid modules, so confirm they are enabled on the terminal first. Bank standing orders through MASAV are a different Tranzila product (the MASAV API, which needs an institution code from MASAV and its own module) and are outside this skill; point the user to that page in the docs.

### Step 10: Generate Invoices

Tranzila has an Invoicing API for generating digitally-signed tax documents approved by the Israeli Income Tax Authority:

1. Create invoices tied to transactions or standalone
2. Invoices are digitally signed for tax compliance
3. Supports tax invoices, receipts, and credit notes

**Israel Tax Authority allocation number (mispar haktza'a), mandatory for B2B invoices over thresholds.** Since May 2024 the ITA requires a B2B tax invoice above a threshold to carry an allocation number obtained from SHAAM. The threshold is keyed to the INVOICE's own date, not today's, so a system that reissues, migrates or audits older documents needs the whole schedule (amounts before VAT): NIS 25,000 from May 2024, NIS 20,000 from January 2025, NIS 10,000 from January 2026, **NIS 5,000 from 1 June 2026 (now in force)**. An invoice dated before May 2024 predates the regime and never needed one. The statute says `עולה על` (EXCEEDS), so an invoice sitting exactly on a band figure is outside the requirement.

Two statutory limits matter for any validation you build: zero-rated and exempt-only invoices are outside the requirement (s.47(א2)(1)), and a missing number disallows the BUYER's input-VAT deduction under s.38(א1) without voiding the invoice, with no buyer-request condition. The verbatim statute text and how to apply it are in `references/allocation-number.md`. Tranzila's invoice module gets the number automatically when the cardholder ID matches the customer's registered business ID; otherwise send the business ID separately, and the field differs by surface: `business_id` as a parameter on the iframe (alongside `myid`), `business_id` as a non-hosted field on Hosted Fields (alongside `card_holder_id_number`), and a `user_defined_fields` entry named `business_id` on API V2 (alongside `card_holder_id`), defined first under Terminal Settings, Additional Fields for Transaction. If none holds the correct ID the charge still succeeds but **no allocation number is issued**, which is exactly what happens to a B2B subscription renewal on API V2 that copies the iframe pattern. If you invoice elsewhere (Green Invoice, Morning, etc.), that provider requests the number instead.

The Invoices API itself is served from `https://billing5.tranzila.com` and binds documents to a transaction; see `references/api-v2-flows.md`.

### Step 11: Handle Errors

Check the `Response` field in every transaction result. `000` means approved -- anything else is a decline or error.

**Important: the HTTP status of an API V2 call is 200 even on a declined/failed transaction.** The HTTP 200 does NOT mean success; read the `Response` / response-code field in the body for the actual SHVA result. There are also application-level codes beside the SHVA result (Hosted Fields `errors[]`, API `error_code` such as 22101, Bit codes); the two transaction code spaces are: the SHVA/issuer codes (hundreds of codes: refusals in 001-017, missing terminal vector or parameter files in 051-089 and 101-152, acquirer and issuer permission errors in 300-354, installment errors in 401-406) and a separate 3D-Secure set, 900-930, on its own tab of the response-codes page. Do not assume codes from Stripe or other gateways.

Key codes from the vendor table (the full list is in `references/error-codes.md`): `000` approved; `777` success for an operation that records no transaction, including J2 and J5; `004` refusal; `015` expired card (`905` in the 3DS space); `016` unauthorized currency; `017` unauthorized credit type; `406` installment sum mismatch; `425` duplicate record, do not blind-retry; `900` failed at the 3D Secure stage; `927` / `928` challenge cancelled by the user, not a card fault.

**Do not carry a code table from memory into your integration.** Earlier versions of this skill listed codes that are not in the vendor table at all and gave others invented meanings; the audit trail is in `references/error-codes.md`. Look every code up by exact number.

## Examples

### Example 1: Accept a One-Time Payment
User says: "I need to add credit card payments to my Node.js checkout page"
Actions:
1. Choose: Iframe integration (minimal PCI scope)
2. Guide: Embed iframe with supplier name, sum, currency=1 (ILS)
3. Implement: a server-side handler at your `notify_url_address` to capture the response, on the DirectNG host
4. Validate: confirm the transaction server-side (Transactions API), check Response=000, store `transaction_id` / `index`
Result: Working checkout that accepts Israeli credit cards via embedded form.

### Example 2: Set Up Monthly Subscription
User says: "I want to charge customers 99 NIS every month automatically"
Actions:
1. First payment: iframe with token creation (`tranmode=AK` to charge and tokenise, or `VK` to verify and tokenise)
2. Store: Save TranzilaTK and the expiry. The DirectNG response sample lists no expiry field, so confirm with Tranzila which notify field carries it, or tokenise with Hosted Fields, which returns `expiry_month` / `expiry_year`. Collecting card fields on your own page instead can take the merchant out of SAQ A scope. A token without an expiry cannot be charged
3. Monthly: Cron job charges the stored token on API V2 (token in `card_number`, the expiry, and the amount as `items`), or on the legacy tranzila31tk.cgi
4. Handle: Check for expired cards, declined tokens
Result: Recurring monthly billing using tokenized cards.

### Example 3: Process Installment Payment
User says: "My customer wants to pay 6,000 NIS in 3 tashlumim"
Actions:
1. Set: cred_type=8 (installments)
2. Calculate: fpay=2000, spay=2000, npay=2 (3 payments total)
3. Verify: Terminal authorized for installments
4. Process: Transaction with installment parameters
Result: Payment split into 3 equal installments of 2,000 NIS.

### Example 4: Refund a Transaction
User says: "I need to refund transaction from last week, confirmation code 0283456"
Actions:
1. Prefer API V2: POST `/v1/transaction/credit_card/create` with `txn_type=credit`, `reference_txn_id`, `authorization_number` (the approval number, here 0283456), the token and expiry, and the refund amount as `items` (partial or full)
2. On the legacy CGI instead: `tranmode=C{index}` against tranzila71u.cgi, which also needs `CreditPass` and `authnr` (see Step 3)
3. Verify: `transaction_result.processor_response_code` on API V2, or `Response=000` on the CGI
Result: Refund processed and linked to original transaction.

### Example 5: Accept Bit Payment
User says: "I want to let customers pay with Bit on my website"
Actions:
1. Call `/v1/transaction/bit/init` (4-header HMAC auth) with `items`, `success_url`, `failure_url` and `notify_url`
2. Show the returned `sale_url` in an iframe (QR code or phone number)
3. Confirm the outcome from `notify_url` plus a server-side Transactions API check
4. Constraints: NIS only, sum above 5 NIS, a Visa/Isracard identifier (Max-only merchants not supported)
Result: Customers can pay using Israel's Bit mobile wallet alongside credit cards.

### Example 6: Send Payment Link via SMS
User says: "I need to collect payment from a customer over the phone"
Actions:
1. Create the request with `/v1/pr/create` (amount and the customer's phone)
2. Tranzila sends the link by SMS and the customer pays on Tranzila's page
3. Confirm the payment through the Transactions API before fulfilling
Result: Payment collected remotely without building a checkout page.

## Community Libraries

- **tranzilajs** (TypeScript/Node.js, `npm install tranzilajs`, `https://github.com/NirTatcher/tranzilajs`): the most complete community client, HMAC auth, Bit, card operations and iframe generation. Its last release is 1.0.0 (August 2025), and its constants still point the checkout at the deprecated `direct.tranzila.com` host and standing-order update at the deprecated `/v1/sto/update`, so override both.
- **futureecom/omnipay-tranzila** (PHP/Omnipay): the driver lives under `futureecom`, not `omnipay/tranzila` (that slug 404s on Packagist).
- **active_merchant_tranzila** (Ruby): only release 0.0.1 from August 2010. Treat it as abandoned.

## Bundled Resources

### References
- `references/api-parameters.md` -- Complete Tranzila API parameter reference for both legacy CGI and API V2 endpoints, including authentication headers, transaction parameters, token operations, and installment fields. Consult when constructing API requests or debugging unexpected parameter behavior.
- `references/error-codes.md` -- Full listing of Tranzila response codes (000-999) with meanings and recommended handling. Consult when a transaction returns a non-000 response code.
- `references/api-v2-flows.md` -- API V2 and Hosted Fields request contracts: `items`, `authorization_number`, allocation-number fields per surface, 3DS, Bit Init, server-side confirmation, Invoices API.
- `references/allocation-number.md` -- The verbatim VAT Law text behind the allocation-number limits (zero-rated carve-out, buyer-deduction effect, 'exceeds' boundary). Consult before building invoice validation.
- `references/3ds-flow.md` -- Step-by-step 3D Secure V2 implementation guide for Tranzila, including redirect flow, authentication parameters, and fallback handling. Consult when adding 3DS to an existing integration.

### Scripts
- `scripts/validate_tranzila_response.py` -- Validates a Tranzila transaction response: checks response code, verifies required fields are present, and flags common issues (missing confirmation code, mismatched amounts). Run: `python scripts/validate_tranzila_response.py --help`

## Gotchas
- The two surfaces use different body formats. The iframe and the legacy CGIs take form-encoded key-value pairs (`application/x-www-form-urlencoded`); API V2 at api.tranzila.com takes JSON (`application/json`). Sending one format to the other surface fails, so pick the format from the endpoint, not from habit.
- **Hosted Fields charges in the browser call, not on your server.** An agent that writes "tokenise in the browser, then charge from the backend" builds a flow the vendor does not document. `fields.charge()` with a server-issued `thtk` is the charge.
- The legacy CGI response is a plain-text `key=value` string joined by `&`, in the same shape as a query string (`Response=000&ConfirmationCode=...&index=...&Tempref=...`), not JSON and not newline-separated. Parse it as a query string. API V2, by contrast, does return JSON, with the SHVA result in `transaction_result.processor_response_code` and an application `error_code` beside it.
- Test cards from Stripe or other international gateways do not work on a Tranzila terminal; ask Tranzila support for your terminal's sandbox cards.
- **A code you cannot find in the vendor table is a code you must not explain.** Several plausible-looking codes (033, 036, 037, 039, 091, 125, 200) do not exist in Tranzila's table at all, and an agent that "recognises" one will hand the merchant a confident wrong diagnosis, most often "card expired" when the real fault is a terminal vector or parameter file. Expired card is **015**.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Tranzila developer docs | https://docs.tranzila.com/ | API reference, authentication, supported card networks, 3DS flow, error codes |
| Hosted Fields integration | https://docs.tranzila.com/ (Payments &amp; Billing → Hosted Fields) | PCI-friendly embedded card capture, and the Response Hash callback-integrity feature |
| Transaction response codes | https://docs.tranzila.com/docs/payments-and-billing/transaction-response-codes | The authoritative SHVA and 3DS code tables. Look every code up here by exact number |
| Authentication (API V2 headers) | https://docs.tranzila.com/docs/payments-and-billing/authentication | The four HMAC headers and the exact access-token derivation |
| Iframe parameters (DirectNG) | https://docs.tranzila.com/docs/payments-and-billing/iframe-integration-directng | The current host, cred_type, currency, tranmode and business_id values |
| Handshake API V2 | https://docs.tranzila.com/docs/payments-and-billing/handshake-v2 | The `thtk` amount lock, its 20-minute life and the Token Module requirement |
| Israel Tax Authority allocation numbers | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice | Required above the band for the invoice's own date: nothing before May 2024, then NIS 25,000 (May 2024), 20,000 (Jan 2025), 10,000 (Jan 2026), 5,000 (Jun 2026, in force) |
| Tranzila company site | https://www.tranzila.com | Terminal enablement requests, installment permissions, contact, PCI certification |
| tranzilajs community client | https://github.com/NirTatcher/tranzilajs | Community TypeScript/Node client and usage examples |

## Troubleshooting

### Error: "Transaction rejected with a non-000 response code"
Cause: Missing or invalid parameters, a card-issuer decline, or a config/permission issue. Remember the HTTP status is 200 even on failure, read the `Response` field for the actual code.
Solution: Verify all required parameters are present: supplier, TranzilaPW, sum, ccno (or TranzilaTK), expdate. Check parameter names are exact (case-sensitive). Look up the exact response code in the official Transaction Response Codes page (see references/error-codes.md), do not guess its meaning.

### Error: "Terminal not authorized for installments / Amex"
Cause: Your Tranzila terminal does not have installment (or Amex) permissions enabled.
Solution: Contact Tranzila support (073-222-4444) to enable installment or Amex processing on your terminal.

### Error: "Token charge fails but iframe worked"
Cause: Common when using the wrong endpoint or omitting the expiry. A token replaces only the card number.
Solution: On API V2 put the token in `card_number`, send `expire_month` / `expire_year`, and carry the amount in `items` (there is no `sum`). On the legacy CGI use `/cgi-bin/tranzila31tk.cgi` (not tranzila31.cgi) with both TranzilaTK and expdate.

### Error: "Transaction approved in test but not production"
Cause: Test and production are separate terminals with their own name and credentials.
Solution: Switch the terminal name, password and API keys together, and ask Tranzila support if behaviour still diverges.

### Error: "Currency mismatch"
Cause: Usually the terminal is not enabled for that currency (code 016), or the code is wrong.
Solution: On the iframe all four currencies go in the one `currency` parameter (`1`, `2`, `978`, `826`); on API V2 use the ISO alpha `txn_currency_code`. Older guidance that EUR and GBP need `tranzila36a.cgi` concerns only the legacy CGI and is not in the current vendor docs. For 016, ask Tranzila to enable the currency on the terminal.