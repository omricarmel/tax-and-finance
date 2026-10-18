---
name: pelecard-payment-gateway
description: "Integrate Pelecard payment processing into Israeli web and mobile apps -- covers the iframe payment flow on gateway21.pelecard.biz, ActionType selection (J2/J4/J5/J5h), tashlumim (installments), tokenization, ConfirmationKey server-side validation via PaymentGW/GetTransaction, refunds, 3D Secure 2, Bit wallet, and Apple Pay via ClientSecure.js. Use when user asks to accept payments via Pelecard, set up slikat ashrai with Pelecard, validate a Pelecard callback, charge a saved Pelecard token, or mentions Pelecard, gateway21, PelecardStatusCode, or ConfirmationKey. Do NOT use for Cardcom (use cardcom-payment-gateway), Tranzila (use tranzila-payment-gateway), Grow/Meshulam (use grow-payment-gateway), multi-gateway orchestration (use israeli-payment-orchestrator), or invoice generation (use green-invoice)."
license: MIT
compatibility: Requires network access for Pelecard API calls. Works with Claude Code, Cursor, Claude Desktop, OpenAI Codex, and GitHub Copilot.
version: 1.2.0
---

# Pelecard Payment Gateway

## Problem

Pelecard is a Payment Service Provider (PSP) that aggregates Israeli merchants onto the card acquirers over Shva, but its public documentation is scattered across a Postman workspace, a sandbox UI, a WordPress plugin listing and third-party PHP libraries, with no single canonical reference. Agents integrating Pelecard end up treating the hostname as an environment switch (it is not), inventing a refund endpoint that does not exist, picking the wrong `ActionType` (which silently changes whether money moves), or trusting a browser-side `ConfirmationKey` instead of re-verifying server-side. Each mistake leaks revenue or ships an exploitable "free order" path.

## Overview

Card transactions clear on the Israeli Shva network (https://www.shva.co.il/, שב"א); Pelecard handles merchant onboarding, the iframe surface, tokenization and reconciliation on top. Your acquirer, not Pelecard, answers the PCI-tier and broadcast-policy questions below.

Pelecard's dominant integration is an iframe payment page: your server posts a credentials triple (`terminal` + `user` + `password`) plus the transaction parameters, gets back a `URL` and a `ConfirmationKey`, and redirects or embeds it. After the customer pays, Pelecard calls your server-side feedback URL. Store the Phase-1 `ConfirmationKey` keyed by your order; on the callback you MUST (a) match it byte-for-byte and (b) re-call `PaymentGW/GetTransaction` before treating the order as paid.

Pelecard has **two** server-to-server surfaces with different parameter-naming conventions.
`/PaymentGW/*` is the iframe surface and has exactly three endpoints. `/services/*` is where every
other operation lives: charges on a saved token, authorizations, voids, refunds, tokens, lookups, settlement,
3DS, invoices. Pelecard publishes a live request builder for them at
https://gateway21.pelecard.biz/services with a preset body for each; that page is the authoritative
endpoint reference, ahead of any third-party wrapper.

A third host, `match-api.pelecard.biz` ("Match API"), is **not** a payment surface. Its Swagger spec
(`/swagger/docs/v2`) shows a settlement-reconciliation API: acquirer records, deny/cancellation lines,
balances, future deposits, `ArnToParamX`. Use it to reconcile deposits, never to charge.

## Instructions

### Step 1: Choose Integration Pattern

| Pattern | Card Data Handling | Best For |
|---------|-------------------|----------|
| **Iframe / hosted page** | Pelecard hosts the card-entry page | Most integrations; smallest PCI scope |
| **Charge stored token** (`/services`) | Token only, no raw card data | Recurring billing, hora'ot keva, one-click |
| **Apple Pay via ClientSecure.js** | Apple Pay handles card data | iOS/Safari customers |
| **Bit wallet** | Customer pays in the Bit app | Single payment, ILS only; caps set by your agreement |
| **Server-to-server** (`/services/*`) | Token, or a PAN you handle | Authorizations, voids, reconciliation. A PAN raises your PCI scope. |

### Step 2: Set Up Authentication

Every Pelecard call needs a credentials triple, sent server-side only:

- `terminal` -- your terminal ID issued by Pelecard
- `user` -- API username
- `password` -- API password

These three values open your terminal to charges. They MUST live in server-side environment variables. Never embed them in browser JavaScript, mobile app bundles, or git history.

**The hostname is not an environment switch.** `gateway20.pelecard.biz` and
`gateway21.pelecard.biz` serve the same API: both answer `PaymentGW/init`,
`PaymentGW/GetTransaction` and `PaymentGW/ValidateByUniqueKey` identically, and a 404 on gateway21
redirects to an error page on gateway20. `gateway21` is the current gateway generation and
`gateway20` the older one; `gateway20.pelecard.biz/sandbox` is a sandbox **UI page**, not a
separate API host.

What decides whether a call is a test or a real charge is **the terminal number and credentials you
send**, not the host. Ask Pelecard which host your test terminal was issued on, keep host + terminal +
credentials in one config object you swap as a unit, and never write code that infers "this is safe"
from a hostname: a build pointed at `gateway20` with live credentials is a live charge. Post to
`gateway21.pelecard.biz` unless Pelecard tells you otherwise.

### Step 3: Create the Iframe Payment Page

Build the request body from your credentials, `Total`, `Currency`, `ActionType` and the feedback URLs.

**Money fields use minor units (agorot).** Send `Total: 9900` for ₪99.00. The dofinity wrapper documents `FirstPayment` as "the amount is in agorot/cents", and Pelecard's builder sends 1 shekel as `total: "100"` and `TotalX100: "100"`. Still do a 1 ₪ test charge.

The create-session path is `PaymentGW/init`, verified live on both gateway hosts.

```
POST https://gateway21.pelecard.biz/PaymentGW/init
Content-Type: application/json

{
  "terminal": "<your-terminal>",
  "user": "<api-user>",
  "password": "<api-password>",
  "ActionType": "J4",
  "Currency": 1,
  "Total": 9900,
  "MaxPayments": 12,
  "MinPayments": 1,
  "GoodURL": "https://example.com/pay/success",
  "ErrorURL": "https://example.com/pay/error",
  "CancelURL": "https://example.com/pay/cancel",
  "ServerSideGoodFeedbackURL": "https://example.com/api/pelecard/ipn-success",
  "ServerSideErrorFeedbackURL": "https://example.com/api/pelecard/ipn-error",
  "ParamX": "order-2026-0042",
  "ShopNo": "main-shop",
  "CreateToken": true
}
```

On success Pelecard responds with a `URL` and a `ConfirmationKey`. **Persist the
`ConfirmationKey` server-side keyed by your order** (you will compare it on the callback in Step 4).
Then redirect the customer to that URL or embed it as an iframe.

**A failed `init` still returns HTTP 200**, as the same two fields blank plus an `Error` object:

```json
{"URL":"","ConfirmationKey":"","Error":{"ErrCode":501,"ErrMsg":"Login for user x failed"}}
```

Check `Error.ErrCode` before using `URL`; treating HTTP 200 as success renders a blank iframe with no
diagnostic. Resolve the code via `/services/GetErrorMessageEn` (Step 8).

**`init` does not return a transaction id.** There is no transaction until the customer transacts, so
correlate on the `ParamX` you sent, not on an id you do not have.

**ActionType reference (full table in `references/payment-parameters.md`):**

| Value | Meaning |
|-------|---------|
| `J4` | Standard sale (default). Money moves now. |
| `J2` | Card validation / registration only. No charge. |
| `J5` | Authorize now, charge later. |
| `J5h` | A J5 variant listed in Pelecard's sandbox; its semantics are not published, ask Pelecard. |

### Step 4: Validate the Callback Server-Side

When the customer finishes paying, Pelecard hits your `ServerSideGoodFeedbackURL` with a `PelecardStatusCode`, `ConfirmationKey`, and `PelecardTransactionId`. Before you treat the order as paid, you MUST do all of the following server-side:

1. Compare your stored Phase-1 `ConfirmationKey` byte-for-byte to the callback value. No match, refuse the payment.
2. Re-call `PaymentGW/GetTransaction` with `terminal/user/password/TransactionId` (the callback's `PelecardTransactionId`).
3. Confirm the debited amount matches the order's expected price and the transaction id matches the callback. `GetTransaction` does not return the `ConfirmationKey`, so this amount/id match is what authenticates the lookup.

**Pelecard documents no signature (HMAC or otherwise) on IPN deliveries, so treat them as unsigned.** A browser-side `ConfirmationKey` can be forged, so the only authoritative source is the server-to-server `GetTransaction` lookup.

The lookup call is the credentials triple plus the `TransactionId`:

```
POST https://gateway21.pelecard.biz/PaymentGW/GetTransaction
{
  "terminal": "<terminal>",
  "user": "<user>",
  "password": "<password>",
  "TransactionId": "<PelecardTransactionId from callback>"
}
```

The response is **not flat**. It is `{"StatusCode":"...","ErrorMessage":"...","ResultData":{...}}`.
Read `StatusCode` first (`"000"` = success), then take the transaction fields from inside
`ResultData`: the authoritative debited amount, the Shva approval number, the installment count,
masked card last 4, expiry, and your `ParamX` echoed back. Compare the debited amount against the
order's expected price; a mismatch means tampering, so do NOT mark the order paid.

**Inbound dedupe.** Pelecard may legitimately deliver the same IPN twice (timeout retry; plugin v1.5.1: "Fixed timeout-retry issues"). Dedupe on **`PelecardTransactionId`**, unique per attempt, not on `ParamX`, which is your order id and repeats across deliveries.

**Reconciliation safety net.** The server-side feedback URL fires only when the transaction reaches
a terminal state. If the customer closes the browser mid-flow, no IPN fires. Three status codes
describe a broken merchant leg, and they do **not** mean the same thing:

| Code | Pelecard's own wording | What it tells you about the money |
|---|---|---|
| `302` | "Debit was successful but merchant is not responding" | The debit **succeeded**. Look it up, then mark paid. |
| `301` | "Session to Pelecard Timed Out" | **Outcome unknown**, and most likely no debit at all. |
| `303` | "Merchant is not responding" | **Outcome unknown.** Says nothing about the debit. |

Only `302` asserts that money moved. Treat `301` and `303` as unresolved until a lookup settles them.

In all three cases you have no `PelecardTransactionId`, and `init` never gave you one. Reconcile on a
key you own:

- `POST /services/CheckGoodParamX` with your `paramX` and `shvaSuccessOnly` answers "was this order
  actually paid?" directly. `/services/CheckGoodParamXList` does it in a batch.
- `POST /services/TrxLookUp` with `paramX` returns the transaction.

`PaymentGW/ValidateByUniqueKey` (no credentials) is a second check, not a lookup: Pelecard's plugin
sends its order key as `UserKey` on `init`, then validates with that value as `UniqueKey` plus the
`ConfirmationKey` and `TotalX100`. For finding a lost transaction, `paramX` is still the key.

Run a lookup on a schedule for every session with no IPN inside your timeout window. **Never re-charge
to resolve an unknown outcome; look it up first.**

**Outbound idempotency (the double-charge you will otherwise ship).** All of the above is *inbound*
dedupe. When a token charge times out at the socket you do not know whether it landed, so `paramX` has
to do double duty: make it `<order-id>-<attempt-n>` and reconcile with a prefix match on `<order-id>`,
so `CheckGoodParamX` can still answer "was this order paid". (Pelecard's builder shows `userKey` only on
the `Pending*Type` family; its WooCommerce plugin also sends `UserKey` on `DebitRegularType`, but no
lookup by it is documented, so do not rely on it.) Look the attempt up before retrying. Pelecard rejects some repeats with `308`
"Duplicated transaction." or `425` "Double entry" -- proof your retry fired twice, not a transient
error to retry again.

Run the bundled `scripts/validate_pelecard_response.py` against your callback while developing. It is a shape check, not a security gate: it cannot know your expected order amount and never verifies the transaction, so a passing result still requires both checks above. With the opt-in `--resolve-codes` flag it POSTs only the numeric status code to Pelecard's public code lookup; no callback content leaves your machine.

### Step 5: Charge a Stored Token (Recurring Billing)

The first transaction sets `CreateToken: true` on the iframe request and Pelecard stores the token
against `TokenForTerminal`. Save the token, the card last-4 and the expiry.

**Renewals are a `/services` call, not an iframe parameter.** Post to
`/services/DebitRegularType` with the saved `token` **instead of** `creditCard`:

```
POST https://gateway21.pelecard.biz/services/DebitRegularType
{
  "terminalNumber": "<terminal>", "user": "<user>", "password": "<password>",
  "shopNumber": "001", "token": "<saved-token>", "creditCardDateMmYy": "1230",
  "total": "9900", "currency": "1", "paramX": "sub-2026-08-0042"
}
```

Note the casing: `terminalNumber` / `total` / `currency` / `paramX` on `/services`, versus
`terminal` / `Total` / `Currency` / `ParamX` on `/PaymentGW`. Sending the `/PaymentGW` names to a
`/services` endpoint is the most common silent failure here. Use `/services/DebitPaymentsType`
(adds `paymentsNumber`, `firstPayment`) when the renewal is in installments.

**Maintain the token, don't just create it.** Cards get reissued and expiries roll, so
`/services/UpdateToken` (plus `ConvertToToken`, `RetrieveToken`, `CheckCreditCardForToken`, all in
`references/api-endpoints.md`) is what keeps a subscriber. Status `506` "Token number abnormal."
means the stored token is no longer chargeable: re-tokenize or `UpdateToken`, never retry it. The Pelecard WordPress plugin has shipped "Saved payment
methods (tokenization)" since v1.2.0 and "WooCommerce Subscriptions support" since v1.4.

**Recurring charges + 3DS (MIT exemption).** Under EMV 3DS 2.x, repeat charges on a stored token can qualify for the MIT (Merchant Initiated Transaction) exemption, so the customer is not challenged on each renewal. No Pelecard parameter for it is published; ask Pelecard which one your terminal uses before relying on it.

**Cancellation is a legal duty, not a feature.** A monthly token charge is an ongoing transaction: under Consumer Protection Law section 13D(c) the contract ends within three business days of the customer's cancellation notice, and you may not charge after that. Gate every renewal on subscription status, and accept cancellation online through a dedicated link on your home page (s.14I(b)). Dunning and the rest are in `references/refunds-and-billing.md`.

### Step 6: Process Refunds

**There is no refund endpoint under `/PaymentGW`.** Refunds are a `/services` call, and the one
Pelecard's own WooCommerce plugin uses (v1.5.3 onward: "Refactored refund flow from DebitRegularType
to ReverseTransaction") is `/services/ReverseTransaction`. It is absent from the public builder, but
answers live with a JSON auth error where a fabricated path redirects to a 404 page.

```
POST https://gateway21.pelecard.biz/services/ReverseTransaction
{
  "terminalNumber": "<terminal>", "user": "<user>", "password": "<password>",
  "debitTrxId": "<original PelecardTransactionId>", "NewAmount": "4900",
  "UID": "", "NewParamX": "", "NewPaymentNo": ""
}
```

The plugin passes the refund amount in agorot as `NewAmount`, partial refunds included, and leaves the
other three empty. Pelecard publishes none of these semantics, so rehearse full, partial and repeat
refunds on your test terminal first (`references/refunds-and-billing.md`). Success is `StatusCode` `"000"`, and the top-level `DebitTrxId` is the
refund leg's own id (fall back to `PelecardTransactionId`); store it against the order. **Send it from
the terminal that made the original charge**: anything else fails with `507` "User is not authorized in
this terminal." The plugin also uses it to release an uncaptured J5 hold.

| Situation | Endpoint |
|---|---|
| Refund, full or partial | `/services/ReverseTransaction` |
| Void while still in the open batch (ביטול) | `/services/DeleteTran` (by `debitTrxId`, `uid`, or `voucherId` + `creditCard` + `total`) |
| Release an authorization you will not capture | `/services/DeleteIshur` (by `debitTrxId`) |

Pelecard does not publish whether `ReverseTransaction` voids an un-broadcast transaction or always
issues a credit (זיכוי). The difference is money: a void never settles, so no clearing fee; a זיכוי is
itself cleared, so you pay on the credit leg too. Run both cases on your test terminal, checking
`/services/GetTransDataBeforeBc` (Step 6b), before relying on either. A pending line may linger in the
customer's card app even after a void.

**A refund retry is a double refund.** Write a refund-intent row before calling, refuse any refund that
would take the total refunded past the original charge, and on a timeout look the refund leg up before
trying again; never auto-retry. Installment refunds and cards that refuse a credit (`129`, `146`,
`161`, `169`) are covered in `references/refunds-and-billing.md`.

**Israeli consumer protection law (חוק הגנת הצרכן, סעיפים 14ג-14ה)** governs distance-selling refunds: consumers may cancel within 14 days, the merchant must refund within 14 days of the cancellation notice, and cancellation fees are capped at 5% of the order value or 100 ₪, whichever is lower. **Do not hard-code 14 days as the whole rule:** customers who are people with disabilities, aged 65 or over, or new immigrants may cancel within **4 months** where a conversation took place during the sale, and some service categories have their own shorter windows. Treat the above as a summary, not the full statute. A זיכוי settles on the issuer's cycle, so the money can reach the customer well after you issue it; the 14-day duty is on your issuing it. (Source: kolzchut, Consumer Protection Law remote-sales chapter.)

### Step 6b: Broadcast (שידור) -- an approval is not money

An approved transaction holding an approval number is an authorization sitting in your terminal's
open batch. It becomes a claim on the issuer only when the terminal **broadcasts** to Shva. Until
then it is not settled and still voidable.

`/services/Broadcast` (credentials only) triggers it, `/services/GetBroadcast` and
`GetBroadcastsByDate` report status, `/services/GetTransDataBeforeBc` lists what has not gone yet.

Terminals differ on whether broadcast is automatic or merchant-triggered. **Find out which yours is.**
A terminal that quietly stops broadcasting piles up approved-but-unsettled transactions while your
database says "paid". Alert on anything in `GetTransDataBeforeBc` older than one broadcast cycle.

### Step 7: Configure 3D Secure 2 and Bit

**3D Secure 2 (EMV 3DS).** On the iframe surface the sandbox UI exposes `Initiate` and
`AskForChallenge` toggles (each: `None` default, `False`, `True`), and Pelecard runs the
authentication for you.

Server-to-server, 3DS2 is an **ordered sequence**: `POST /Services/Initiate3DSAuthenticationProcess`
(fields in `references/api-endpoints.md`), the customer is authenticated frictionlessly or challenged
at your `RedirectUrl`, then the debit **carries the result** in `eci`, `xid` and `cavv`. Skipping the
last step wastes the authentication and forfeits the liability shift. Status `650` is
"3DS process failed". The Pelecard plugin v1.4.19 changelog notes "Added Emv errors in order notes.
ShvaResultEmv parameter" -- log `ShvaResultEmv` whenever it appears.

**Bit wallet.** Pelecard does not publish its Bit limits; your Bit terms come from your agreement. The
closest public statement is another Israeli PSP's (allpay.co.il) Bit page, which shows the shape:

- **No installments** ("You can only pay with Bit in one payment"): hide the tashlumim selector.
- **Shekels only**: send `Currency: 1`.
- **No saved card**, so Bit cannot carry a subscription. Use a card token for recurring billing.
- **Caps**: allpay's are 5,000 ₪ per payment and 20,000 ₪ a month across all customers, with a
  10-minute window. Treat them as a design starting point and get your own figures from Pelecard.
- The charge is made from the card linked to Bit, so card declines still apply. Confirm the Bit
  refund and reconciliation path with Pelecard before enabling it.

**Apple Pay.** Pelecard hosts the SDK at `ClientSecure.js`, loaded into your own checkout page (see Step 9 on PCI scope). The plugin lists it as "optional, disabled by default".

### Step 8: Handle Errors

Pelecard returns a numeric status code everywhere: `PelecardStatusCode` on the callback,
`StatusCode` on a `GetTransaction` response, `Error.ErrCode` on a failed `init`. `000` is success.

**Do not hard-code a hand-written mapping, and do not tell users to email support.** Pelecard
publishes the official message for every code through two endpoints that need **no credentials**:

```
POST https://gateway21.pelecard.biz/services/GetErrorMessageEn
POST https://gateway21.pelecard.biz/services/GetErrorMessageHe
{"ErrorCode": "033"}      ->  invalid credit card.  /  כרטיס לא תקין.
```

Wire `GetErrorMessageHe` into your failure path to show the customer a real Hebrew decline message,
and cache the responses.

`references/error-codes.md` carries the full enumerated table (254 assigned codes, both languages,
swept 2026-08-27, re-swept unchanged 2026-10-18) plus a retry policy, including the merchant-unreachable codes `301` / `302` / `303`
and which of them actually means money moved. EMV / 3DS results ride alongside in
`ShvaResultEmv`, a separate code space.

### Step 9: Keep your PCI scope where you think it is

The iframe pattern keeps card data off your servers, which is why it is the default recommendation
here. Two things in this skill quietly move that line, so decide deliberately:

- **Any `/services` call sending `creditCard` puts a PAN through your systems** (typically SAQ D). A
  saved `token` does not. Prefer the token.
- **Apple Pay via `ClientSecure.js` loads a Pelecard script into your own checkout page.** A pure
  redirect/iframe merchant is normally SAQ A; a merchant page hosting a payment script is normally
  SAQ A-EP. Your acquirer decides; those names are the shape of the question to ask them.

**Do not log `ConfirmationKey`**: Step 4's verification rests on an attacker not knowing it, so log
a hash if you need to correlate. **Do not log `CardHolderID`** (te'udat zehut) in
plaintext; it is personal data under the Privacy Protection Law (Amendment 13) and carries retention
duties your log pipeline probably does not meet.

## Examples

### Example 1: First-Time Iframe Checkout
User says: "I want to accept credit-card payments on my Israeli site via Pelecard, with up to 12 tashlumim."
Actions:
1. Server: POST credentials + `ActionType: J4` + `Total: 9900` (₪99.00 in agorot) + `Currency: 1` + `MaxPayments: 12` to `PaymentGW/init`. Check `Error.ErrCode` before using the returned `URL`.
2. Persist the `ConfirmationKey` keyed by your order. Render the `URL` in an iframe (or redirect).
3. Listen on `ServerSideGoodFeedbackURL`, and run a `CheckGoodParamX` sweep for sessions that never call back.
4. Compare the callback `ConfirmationKey` to your stored value, then re-verify via `PaymentGW/GetTransaction` and confirm the debited amount before marking the order paid.
Result: Customer pays in 1-12 tashlumim, against a verified transaction.

### Example 2: Save a Card and Charge It Monthly
User says: "I run a SaaS, I need to charge users 99 ₪ every month with their saved card."
Actions:
1. First payment: iframe POST with `CreateToken: true` and `Total: 9900` (agorot). Save the token, last-4 and expiry.
2. Monthly cron: POST `/services/DebitRegularType` with `token`, `total`, `currency` and a `paramX` of `<order>-<attempt>`.
3. Verify each charge, dedupe inbound IPNs on `PelecardTransactionId`, and on any timeout look the attempt up before retrying.
4. Gate each run on subscription status so nobody is charged after a cancellation takes effect (Step 5). Handle declines via the code table, and refresh reissued cards with `/services/UpdateToken`.
Result: Recurring billing without storing a single PAN on your servers.

### Example 3: Add Bit as a Checkout Option
User says: "Most of my Israeli customers want Bit, can I add it?"
Actions:
1. Enable Bit on the Pelecard terminal (vendor-side configuration).
2. Send `Currency: 1` and gate Bit to the per-payment cap in your Pelecard agreement (5,000 ₪ is a common figure; get yours).
3. Hide the tashlumim selector when Bit is chosen; Bit is single-payment only.
4. Same callback flow. Settle the Bit refund path with Pelecard before launch, not after.
Result: Bit added cleanly, no failed charges from wallet-side constraints.

### Example 4: Validate a Callback Payload Locally
User says: "My Pelecard callback came in, how do I sanity-check it before hitting GetTransaction?"
Actions:
1. Run `python scripts/validate_pelecard_response.py --resolve-codes --response '{"PelecardStatusCode":"000","ConfirmationKey":"...","PelecardTransactionId":"...","Total":9900,"Currency":1}'`.
2. It flags a missing `ConfirmationKey` or `PelecardTransactionId`, requires the canonical `"000"`, and resolves any failing code to Pelecard's own bilingual message. `--explain 033` looks a code up on its own.
3. If it passes, do the two real checks: stored-vs-callback `ConfirmationKey`, then `PaymentGW/GetTransaction` for the debited amount.
Result: Quick local check before hitting the Pelecard API.

### Example 5: Authorize Now, Charge on Shipment (J5)
User says: "I want to authorize the customer's card at order time but only charge when I ship -- like Amazon."
Actions:
1. First call: `ActionType: J5` **with `CreateToken: true`**. The capture needs a `token` (or a
   `creditCard`), and an iframe J5 without `CreateToken` leaves you with neither. Persist the token and
   the authorization number from the IPN / `GetTransaction` `ResultData` (it is not in the `init` response).
2. On shipment, post `/services/DebitRegularType` (or `DebitPaymentsType` / `DebitCreditType` with
   `paymentsNumber` if the authorization was in installments) with the saved `token`, the amount and the
   `authorizationNumber`. This is how Pelecard's own WooCommerce plugin captures a J5, and it sends the
   capture **from the terminal that holds the authorization**: its v1.5.3 changelog fixed a capture
   routed to another terminal, which left the hold open alongside a separate charge. Rehearse on your
   test terminal before going live.
3. If you decide NOT to ship, release the hold with `/services/DeleteIshur` and check on the test
   terminal that the hold is really freed. An abandoned hold is a support ticket.
4. Verify the captured transaction via `PaymentGW/GetTransaction`, and confirm it broadcasts.
Result: Auth-then-capture pattern compatible with Israeli e-commerce flows.

### Example 6: Refund a Failed Order
User says: "Customer disputed order #5678, I need to refund."
Actions:
1. Pull the original `PelecardTransactionId` from your order record (stored from the IPN / `GetTransaction`).
2. Write a refund-intent row and check the total refunded stays within the original charge. Then post
   `/services/ReverseTransaction` with it as `debitTrxId` and the refund in agorot as `NewAmount`, from
   the terminal that made the charge. Check `StatusCode` `"000"`; a `507` means the wrong terminal; a
   timeout means look it up, not retry.
3. Persist the refund leg's `DebitTrxId` against the original order.
4. Honor the Israeli Consumer Protection Law deadlines in Step 6, including the 4-month window for some customers. If the card refuses the credit, refund another way within the deadline.
5. Issue the credit note (חשבונית זיכוי) via your invoice provider, or via Pelecard's own `/services/CreateInvoice` family.
Result: One refund, issued once, with a credit note.

## Bundled Resources

### References
- `references/api-endpoints.md` -- The verified endpoint catalogue: host model, the three `/PaymentGW` endpoints with their real response envelopes, and the `/services` surface (charge, authorize, void, tokens, lookup, broadcast, 3DS, invoices) with parameter names.
- `references/payment-parameters.md` -- The iframe (`PaymentGW/init`) parameter reference: ActionType, Currency, tashlumim, tokenization, BIN controls, UI customization, feedback URLs, passthrough fields.
- `references/error-codes.md` -- The full status-code table (254 assigned codes, English + Hebrew, swept from Pelecard's credential-free lookup), plus a retry policy and the EMV/Shva note.
- `references/refunds-and-billing.md` -- What `ReverseTransaction` is known (and not known) to do, refund idempotency, installment refunds, cards that refuse a credit, subscription cancellation under Consumer Protection Law s.13D, dunning.

### Scripts
- `scripts/validate_pelecard_response.py` -- Shape-checks a Pelecard callback JSON and, with `--resolve-codes`, resolves a failing status code to Pelecard's own bilingual message. `--explain <code>` looks one up directly; `--self-test` checks the 000/302/301/303 handling offline.

## Recommended MCP Servers

No Pelecard MCP exists yet. Pair with the `green-invoice` skill for the Israeli tax document (חשבונית מס), or use Pelecard's own `/services/CreateInvoice` family.

## Reference Links

| Source | Purpose |
|--------|---------|
| https://gateway21.pelecard.biz/services | **Primary reference.** Pelecard's live public request builder: 54 `/services` endpoints plus the `/PaymentGW` lookups, each with a preset request body. Use this instead of guessing parameter names. |
| https://www.postman.com/peleteam/pelecard-public/overview | Pelecard's official Postman workspace ("Gateway21" collection). |
| https://gateway20.pelecard.biz/sandbox | Official Pelecard sandbox + parameter reference. ActionType, currency, 3DS, Bit/Apple Pay/Google Pay toggles. |
| https://wordpress.org/plugins/woo-pelecard-gateway/ | Pelecard-authored WooCommerce plugin; its source (plugins.svn.wordpress.org) shows the real refund (`ReverseTransaction`) and J5 capture calls. |
| https://github.com/dofinity/pelecard | Third-party PHP wrapper. Documents the full `PaymentRequest` parameter set, the `ConfirmationKey` validation flow, and `PaymentGW/GetTransaction`. |
| https://gateway21.pelecard.biz/services/GetErrorMessageEn | Credential-free official status-code lookup (`{"ErrorCode":"033"}`). `GetErrorMessageHe` for Hebrew. |
| https://match-api.pelecard.biz/swagger/docs/v2 | Swagger spec of the "Match" settlement-reconciliation API (not a payment surface). |
| https://www.allpay.co.il/en/help/bit | Another PSP's published Bit terms (5,000 ₪ per payment, 20,000 ₪ a month, no installments, 10 minutes). Illustrative, not Pelecard's. |

## Gotchas

- **The hostname is not an environment switch.** `gateway20` and `gateway21` serve the same API; both answer `PaymentGW/init`, `GetTransaction` and `ValidateByUniqueKey` identically, and `gateway20.pelecard.biz/sandbox` is a UI page, not a separate API host. Test-versus-live is decided by the terminal and credentials. Keep host + terminal + credentials in one config object and swap them as a unit; never let code infer safety from a hostname.
- **Refunds go through `/services/ReverseTransaction`, which the public builder does not list.** There is no refund endpoint under `/PaymentGW`. Send it from the terminal that made the charge (else `507`), record the intent first, and never auto-retry a timed-out refund.
- **An approval number is not money.** A transaction settles only after the terminal broadcasts to Shva. Alert on anything sitting in `/services/GetTransDataBeforeBc` longer than one broadcast cycle.
- **`302` means the debit succeeded; `301` and `303` mean the outcome is unknown.** Only `302` says money moved. Resolve the other two by lookup before touching the order.
- **The two surfaces use different parameter casing.** `/PaymentGW` takes `terminal` / `Total` / `Currency` / `ParamX`; `/services` takes `terminalNumber` / `total` / `currency` / `paramX`, and a couple of token endpoints use PascalCase credentials. Copy the preset from https://gateway21.pelecard.biz/services rather than guessing.
- **A failed `init` returns HTTP 200 with a blank `URL`.** Check `Error.ErrCode`, not the HTTP status.
- **Wrong `ActionType` silently changes whether money moves.** `J2` is registration-only and does not charge, but the merchant UI looks identical to `J4`. Default to `J4`. Plugin v1.4.7: "Bypass validation for J2 transactions."
- **A J5 taken without `CreateToken` may be uncapturable,** and a capture sent from a different terminal than the authorization leaves the hold open beside a new charge.
- **Pelecard documents no IPN signature (no HMAC).** Protections: re-verify every callback via `PaymentGW/GetTransaction`, ask Pelecard whether it publishes outbound IPs you can allowlist, enforce TLS 1.2+. Never trust a payload just because its `ConfirmationKey` looks familiar.
- **`PelecardTransactionId` is your inbound dedupe key, not `ParamX`.** Pelecard may deliver one IPN twice (timeout retry). `ParamX` is your order id and repeats; `PelecardTransactionId` is unique per attempt.
- **Bit is one payment, shekels only, and no saved card.** Hide the tashlumim selector, gate to the cap in your own agreement (public figures such as 5,000 ₪ are another PSP's), and send `Currency: 1`.
- **The credentials triple is server-side only,** and money fields are agorot (`Total: 9900` = ₪99.00). Do a 1 ₪ test charge before going live.

## Troubleshooting

### Error: Callback received but `PaymentGW/GetTransaction` returns "transaction not found"
Cause: The terminal you are querying with is not the terminal the transaction was made on (a test terminal looking up a live transaction, or vice versa). Verified NOT to be a host problem: gateway20 and gateway21 serve the same API, so switching hosts will not fix this.
Solution: Confirm the terminal number and credentials match the transaction. `POST /services/GetTerminalName` with the credentials triple is the cheapest check that your credentials resolve to the terminal you expect. Then re-run the lookup.

### Error: `ConfirmationKey` missing from callback
Cause: The customer abandoned mid-flow, or the request was tampered with.
Solution: Treat the order as unpaid. Do NOT mark it paid even if `PelecardStatusCode` looks like success; resolve it with a `paramX` lookup instead.

### Error: Refund returns `507` "User is not authorized in this terminal."
Cause: `ReverseTransaction` was sent with the credentials of a different terminal from the one that made the original charge (typical on two-terminal setups). Pelecard's plugin v1.5.3.1 fixed exactly this.
Solution: Store which terminal performed each charge and send the refund with that terminal's credentials.

### Error: Bit payment fails for amounts above 5,000 ₪
Cause: the per-payment cap in your Bit terms. 5,000 ₪ is the figure another Israeli PSP publishes; Pelecard does not publish one, so ask for yours.
Solution: Gate the Bit option to the cap your agreement allows, surface a "Bit limited to <your cap>" message, offer card as the alternative, and confirm `Currency: 1`.

### Error: 3DS challenge appears in sandbox but transaction is rejected
Cause: A challenge on a test terminal needs specific test cards and challenge responses configured per terminal. Status `650` is "3DS process failed"; resolve any code with `/services/GetErrorMessageEn`.
Solution: Ask Pelecard which test cards and challenge codes work against your terminal. The `Initiate` / `AskForChallenge` toggles control whether 3DS is invoked at all.

### Error: Token charge succeeds but customer claims no payment
Cause: J5 (authorize) was used instead of J4 (sale), and capture was never triggered.
Solution: Verify the `ActionType` on the original transaction via `PaymentGW/GetTransaction`. If it was `J5` or `J5h`, capture it by posting a debit carrying the `authorizationNumber` from the same terminal, or release it with `/services/DeleteIshur`. Default to `J4` for one-shot sales. If the ActionType was `J4` and it still has not settled, check `/services/GetTransDataBeforeBc` -- an un-broadcast J4 is approved but not yet money.
