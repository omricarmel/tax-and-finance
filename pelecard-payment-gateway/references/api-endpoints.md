# Pelecard API Endpoints

Everything below was verified live against `gateway21.pelecard.biz` on 2026-08-27 and re-probed 2026-10-18, either by
probing the endpoint directly or by reading Pelecard's own public request builder at
`https://gateway21.pelecard.biz/services` (which ships the service list and a preset request body
for each one in `/Scripts/Services/Sandbox.js`). That script defines 57 distinct service URLs: 54
under `/services/`, plus `/PaymentGW/GetTransaction`, `/PaymentGW/ValidateByUniqueKey` and
`/PaymentEnquiry/CreateLink`. Re-swept 2026-10-18: same 54 `/services/` URLs.

The builder is not exhaustive. Pelecard's own WooCommerce plugin (v1.5.3.1, source at
`plugins.svn.wordpress.org/woo-pelecard-gateway`) calls two `/services` endpoints the builder does not
list: `ReverseTransaction` (refunds) and `CreatePayperInvoice`. Both answer live with a JSON auth error
(`StatusCode` `501`) where a fabricated `/services/` path redirects to a 404 page.

## Hosts: environment is the TERMINAL, not the hostname

| Host | What it actually is |
|------|---------------------|
| `gateway21.pelecard.biz` | Current gateway generation. Serves the live API. |
| `gateway20.pelecard.biz` | Older gateway generation. Serves the **same** API surface. |
| `gateway20.pelecard.biz/sandbox` | A sandbox **UI page** (a request builder), not a separate API host. |
| `match-api.pelecard.biz` | The "Match API": settlement **reconciliation**, not payments. Swagger spec at `/swagger/docs/v2` (the `/docs/index` page is a Swashbuckle UI that renders it client-side). Endpoints include `MatchApi/GetMatchingLinesBetweenTransactionDates` (acquirer records), `GetDenyAndCancellationLines`, `GetBalanceLines`, `GetClearingCompanyUnmatchedData`, `ParamX/ArnToParamX` and `Reports/FlowSummary` (future deposits). Requests carry `user` / `password`, some also `terminal`. |

**Do not treat the hostname as an environment switch.** Both `gateway20` and `gateway21` answer
`PaymentGW/init`, `PaymentGW/GetTransaction` and `PaymentGW/ValidateByUniqueKey` identically, and a
404 on `gateway21` redirects to an error page on `gateway20`, so they are one system. Whether a
call is a test or a real charge is decided by **which terminal number and credentials you send**,
not by which host you post to. Ask Pelecard which host your test terminal was issued on, keep host
and terminal together in one config object, and never let code infer safety from a hostname.

## The two surfaces (different parameter casing -- this bites)

Pelecard has two server-to-server surfaces and they do **not** share a naming convention. Mixing
them up is the most common cause of a request that returns an error with no useful message.

| | `/PaymentGW/*` | `/services/*` |
|---|---|---|
| Credentials | `terminal`, `user`, `password` | `terminalNumber`, `user`, `password` |
| Transaction id | `TransactionId` | varies: `debitTrxId`, `voucherId`, `uid`, `trxRecordId` |
| Amount | `Total` | `total` |
| Currency | `Currency` | `currency` |
| Order correlation | `ParamX` | `paramX` |
| Shop | `ShopNo` | `shopNumber` |

A few `/services` endpoints (`UpdateToken`, `RetrieveToken`) use PascalCase for the credentials
(`TerminalNumber`, `User`, `Password`). Copy the preset from the live builder rather than guessing.

## `/PaymentGW/*` -- the iframe surface (3 endpoints, all verified live)

### `POST /PaymentGW/init` -- create the payment session

Body: the credentials triple plus the transaction parameters (see `payment-parameters.md`).

**Success** returns `URL` and `ConfirmationKey`. **Failure** returns those two fields as empty
strings plus an `Error` object:

```json
{"URL":"","ConfirmationKey":"","Error":{"ErrCode":501,"ErrMsg":"Login for user x failed"}}
```

Check `Error.ErrCode` before using `URL`. A blank `URL` with HTTP 200 is a failure, not a session.
Resolve `ErrCode` with `/services/GetErrorMessageEn` (see `error-codes.md`).

**`init` does NOT return a `PelecardTransactionId`.** The response has exactly two data fields.
There is no transaction until the customer actually transacts, so any reconciliation design that
assumes you can store a transaction id at session-create time is unbuildable. Correlate on your own
`ParamX` (and/or `UserKey`) instead, and look the transaction up later with `/services/TrxLookUp`.

### `POST /PaymentGW/GetTransaction` -- look a transaction up by id

Body: `terminal`, `user`, `password`, `TransactionId`.

Response envelope is **not** flat. It is:

```json
{"StatusCode":"501","ErrorMessage":"Login for user x failed","ResultData":{ ...66 fields... }}
```

Read `StatusCode` first (`"000"` = success), then the transaction fields inside `ResultData`.
Do not read amount or approval fields off the top level; they are not there.

### `POST /PaymentGW/ValidateByUniqueKey` -- validate without credentials

Body: `ConfirmationKey`, `UniqueKey`, `TotalX100`. **No credentials.** Returns a bare numeric
result.

**Where `UniqueKey` comes from.** Pelecard's own plugin (v1.5.3.1) sends `UserKey` on
`PaymentGW/init` (its WooCommerce order key) and later calls `ValidateByUniqueKey` with that same value
as `UniqueKey`, the stored `ConfirmationKey`, and the transaction's `DebitTotal` as `TotalX100`. So
`UserKey` on `init` is what becomes the `UniqueKey`. It is a validation check, not a lookup: to find a
transaction whose callback never arrived, use `paramX` via `/services/CheckGoodParamX` or
`/services/TrxLookUp` (see SKILL.md Step 4).

`TotalX100` means "the amount multiplied by 100", i.e. minor units (agorot). This corroborates the
agorot convention independently of the dofinity wrapper: the builder's preset sends `TotalX100:
"100"` for the same 1 shekel that `/services/DebitRegularType` sends as `total: "100"`.

Contrary to older versions of this reference, `ValidateByUniqueKey` is **not** a gateway20-only
endpoint. It answers on both hosts.

Every other `/PaymentGW/*` path tested (`DebitRegular`, `DebitRegularCancel`, `Refund`,
`ConfirmDebit`, `CancelTransaction`, `GetToken`) 302-redirects to an HTTP 404 error page, exactly
as a deliberately fabricated control path does. **There is no `PaymentGW` refund endpoint.**

## `/services/*` -- the server-to-server surface

This is where every operation other than "create an iframe session" lives. 54 endpoints are listed
under `/services/` in the live builder. The ones an integration actually needs:

### Charge

| Endpoint | Purpose | Key parameters |
|----------|---------|----------------|
| `/services/DebitRegularType` | Standard sale (J4) | `terminalNumber`, `user`, `password`, `shopNumber`, `creditCard`, `creditCardDateMmYy`, `token`, `total`, `currency`, `cvv2`, `id`, `authorizationNumber`, `paramX`, `eci`, `xid`, `cavv` |
| `/services/DebitPaymentsType` | Installments sale | as above plus `paymentsNumber`, `firstPayment` |
| `/services/DebitCreditType` | Credit-type sale | as `DebitRegularType` |
| `/services/DebitIsracreditType` | Isracredit-type sale | as `DebitRegularType` |

Pass a saved `token` **instead of** `creditCard` to charge a stored card. That is the recurring
billing path, and it is a `/services` call, not an iframe parameter.

`eci` / `xid` / `cavv` are the 3D Secure 2 result values you carry **into** the debit after running
the authentication (see below). `authorizationNumber` carries a prior authorization into the debit,
which is the mechanism for capturing a J5 hold.

### Authorize (hold) and pending

| Endpoint | Purpose |
|----------|---------|
| `/services/AuthorizeCreditCard` | Authorize a card (J5). Places a hold; no money moves. |
| `/services/AuthorizeCreditType` / `AuthorizePaymentsType` / `AuthorizeIsracreditCard` | Authorize variants |
| `/services/PendingRegularType` (also `PendingCreditType`, `PendingPaymentsType`, `PendingIsracreditType`) | J9 pending transaction. Takes `authorizationNumber` and `userKey`. |
| `/services/ClearPendingByUserKey` | Clear a pending request by your `userKey` |
| `/services/ClearPendingByRecordId` | Clear a pending request by Pelecard's record id |

To capture a hold, submit a debit carrying the `authorizationNumber` the authorization returned.
Pelecard's own plugin does exactly this (`DebitRegularType` with `token` + `authorizationNumber`, or
`DebitPaymentsType` / `DebitCreditType` with `paymentsNumber` when the order is in installments), and
sends it from the terminal that holds the authorization: its v1.5.3 changelog fixed a capture routed to
a second terminal, which left the hold open beside a separate charge. Rehearse on your test terminal.

The plugin also sends `UserKey` on `DebitRegularType`. The builder's debit presets do not include it
and no debit-side lookup by it is documented, so correlate on `paramX`.

### Refund, void and release

| Endpoint | Parameters | Use |
|----------|-----------|-----|
| `/services/ReverseTransaction` | `terminalNumber`, `user`, `password`, `debitTrxId` (original `PelecardTransactionId`), `NewAmount` (the plugin passes the refund amount x100), plus `UID`, `NewParamX`, `NewPaymentNo` (sent empty by the plugin) | Refund, full or partial. What Pelecard's plugin uses since v1.5.3; also releases an uncaptured J5. Not in the builder; field semantics are inferred from the plugin, see `refunds-and-billing.md`. |
| `/services/DeleteTran` | `terminalNumber`, `user`, `password` + one of (`voucherId` + `creditCard` + `total`) / `debitTrxId` / `uid` | Delete a transaction from the open batch (explicit void) |
| `/services/DeleteIshur` | `terminalNumber`, `user`, `password`, `debitTrxId` | Delete an authorization (release a hold) |
| `/services/EmvReversal` | `terminalNumber`, `user`, `password`, `Uid` or `DebitTrxId` | EMV (card-present) reversal |
| `/services/EmvFinishDebit` | `terminalNumber`, `user`, `password`, `Uid` | Finish an EMV debit |

`ReverseTransaction` response: `StatusCode` `"000"` is success; the plugin stores the top-level
`DebitTrxId` as the refund leg's id, falling back to `PelecardTransactionId`. It must run on the
terminal that owns the original debit, otherwise `507` "User is not authorized in this terminal."
Whether it voids an un-broadcast transaction or always issues a credit is not published; test both on
your test terminal (see SKILL.md Step 6).

### Tokens

| Endpoint | Purpose | Parameters |
|----------|---------|------------|
| `/services/ConvertToToken` | Tokenize a card | `terminalNumber`, `user`, `password`, `creditCard`, `creditCardDateMmYy`, `addFourDigits` |
| `/services/RetrieveToken` | Fetch the token for a card | `TerminalNumber`, `User`, `Password`, `CreditCard` |
| `/services/UpdateToken` | Update a token after reissue / expiry roll | `TerminalNumber`, `User`, `Password`, `CreditCard`, `CreditCardDateMmYy`, `Token` |
| `/services/CheckCreditCardForToken` | Check a card is tokenizable before charging | `terminalNumber`, `user`, `password`, `CreditCard`, `CreditCardDateMmYy` |

`UpdateToken` is the "saved card was reissued" path. Without it, every card reissue is a lost
subscriber.

### Lookup and reconciliation

| Endpoint | Keyed on | Use |
|----------|----------|-----|
| `/services/TrxLookUp` | `paramX` | Find the transaction for one of your orders |
| `/services/CheckGoodParamX` | `paramX`, `shvaSuccessOnly` | Was this order paid successfully? |
| `/services/CheckGoodParamXList` | `paramX` list | Batch version |
| `/services/CheckGoodParamXEmv` | `paramX` | EMV variant |
| `/services/GetTransData` | `startDate`, `endDate` (`dd/MM/yyyy HH:mm`) | Transactions in a window |
| `/services/GetCompleteTransData` | `startDate`, `endDate` | Full transaction records in a window |
| `/services/GetTransDataBeforeBc` | date range | Transactions **not yet broadcast** |

`GetTransDataBeforeBc` ("before broadcast") is the endpoint that tells you what is sitting
unsettled in the open batch.

### Settlement, 3DS, operations

| Endpoint | Purpose |
|----------|---------|
| `/services/Broadcast` | Trigger the Shva broadcast (שידור) for the terminal. Takes only `terminalNumber`, `user`, `password`. |
| `/services/GetBroadcast` / `GetBroadcastsByDate` | Broadcast status / history |
| `/Services/Initiate3DSAuthenticationProcess` | Start 3DS2 authentication. Takes `RedirectUrl`, `BillingAmount`, `BillingCurrencyCode`, card or `Token`, cardholder name/email/phone/address, and browser fingerprint fields (`HttpAcceptHeader`, `BrowserScreenPixelsHeight/Width`, `BrowserLanguage`, `BrowserScreenBitDepth`, `EndUserIPAddress`, `UserAgent`). |
| `/services/GetErrorMessageEn` / `GetErrorMessageHe` | Official bilingual message for any status code. **No credentials.** |
| `/services/GetTerminalName` | Cheapest possible credential smoke test |
| `/services/ResetUserPassword` | Rotate the API password (they expire; see code `502`) |
| `/services/CreateInvoice`, `CreateICountInvoice`, `CreateEZCountInvoice` | Emit the tax invoice through Pelecard rather than a separate provider |
| `/Services/InitiateBankTransfer` | Open-banking bank transfer (returns ISO 20022 status codes `660`-`680`) |

The full list, with a preset request body for each, is at `https://gateway21.pelecard.biz/services`.
Use it as the primary reference; it is live, public, and always current.
