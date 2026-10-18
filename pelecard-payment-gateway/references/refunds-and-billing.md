# Refunds and Recurring Billing: the Details

SKILL.md Step 5 and Step 6 carry the rules you cannot skip. This file carries the rest: what is and
is not known about `ReverseTransaction`, how to stop a refund retry becoming a double refund,
installment refunds, cards that refuse a credit, and cancelling a subscription lawfully.

## What `ReverseTransaction` is known to do (and what is inferred)

Everything below comes from Pelecard's own WooCommerce plugin, v1.5.3.1
(`plugins.svn.wordpress.org/woo-pelecard-gateway/tags/1.5.3.1/includes/Api.php` and `Gateway.php`).
Pelecard does not publish this endpoint in its request builder or anywhere else we could find.

| Known from the plugin code | Not published anywhere |
|---|---|
| Body: `terminalNumber`, `user`, `password`, `debitTrxId` (original `PelecardTransactionId`), `NewAmount`, with `UID`, `NewParamX`, `NewPaymentNo` sent empty | What `NewParamX` and `NewPaymentNo` do |
| The plugin passes the refund amount x100 as `NewAmount`, including for partial refunds | Whether `NewAmount` is "amount to refund" for every terminal type, or how a second partial refund on the same `debitTrxId` behaves |
| Success is `StatusCode` `"000"`; top-level `DebitTrxId` is the refund leg's id (fallback `PelecardTransactionId`) | Whether it voids an un-broadcast transaction or always issues a credit |
| Must be sent from the terminal that made the charge, otherwise `507` | Behaviour months after the charge, or after the card was reissued |
| Also used by the plugin to release an uncaptured J5 | Whether it rejects a repeat call on the same `debitTrxId` |

**Rehearse before go-live, on your test terminal:** a full refund, a partial refund, a second partial
refund on the same transaction, a refund of a transaction that has already been broadcast, and a
deliberate double call. After each, confirm what actually moved with `PaymentGW/GetTransaction` and
`/services/GetCompleteTransData` rather than trusting the `"000"`.

### History: refunds used to be a negative `total`

Up to v1.5.2 the same plugin refunded by setting the order total to a negative amount and posting it to
`/services/DebitRegularType` with the saved token. v1.5.3 moved to `ReverseTransaction` ("no longer
requires saved card token"), and v1.5.3.1 still recognises "negative DebitTotal from old
DebitRegularType refunds". Two consequences: your reconciliation must handle negative `DebitTotal`
lines on older transactions, and if you ever use the token route instead of `ReverseTransaction`,
rehearse it on the test terminal first; nothing public documents how a terminal treats it.

## Refund idempotency (the double refund you will otherwise ship)

On a socket timeout the plugin records the failure only as an order note and a log line, with no
refund-intent state, so nothing stops an operator pressing Refund again. Nothing shown so far proves Pelecard rejects the second
call, so two successful calls are two refunds. Build it like the outbound charge rule in Step 4:

1. Before calling, write a refund-intent row: order, original `debitTrxId`, terminal, amount, your own
   refund id, state `pending`.
2. Under a database lock, refuse the call if refunds already issued plus this one exceed the original
   charge. The plugin leaves that cap to WooCommerce; outside WooCommerce, nobody enforces it for you.
3. On a timeout, mark the intent `unknown` and **do not retry automatically**. Look for the refund leg
   with `/services/GetTransData` or `/services/GetCompleteTransData` over a window that covers the
   attempt (both take only a date range), matching on the refund amount and time, plus the card if the
   response carries it; the output fields are not published. Then decide.
4. If a refund call ever returns `308` "Duplicated transaction." or `425` "Double entry", do not retry:
   reconcile first. Whether `ReverseTransaction` returns these codes at all is undocumented.

## Installment (tashlumim) refunds

Before broadcast, `/services/DeleteTran` deletes the transaction from the open batch; nothing has
settled yet, but what that does to an installment schedule is not documented, so confirm it with
Pelecard. After broadcast, expect the refund to be a credit (עסקת זכות) on **regular** terms: code
`169` reads "credit transaction cannot be executed with credit different from usual" (Hebrew: "לא
ניתן לבצע עסקת זכות עם אשראי שונה מ-רגיל"). How the issuer then treats the remaining installments of the
original purchase is the issuer's process, so do not promise the customer that "the installments
stop"; tell them a credit is coming and confirm the treatment with Pelecard. Leave `NewPaymentNo` alone
unless a rehearsal shows what it does.

## When the card refuses a credit

`129`, `146`, `161` and `169` are the codes whose Hebrew text names a refund/credit transaction
(עסקת זכות): a terminal without approval for credits above a ceiling, an immediate-debit card, a zero
credit ceiling for that card type, and credit terms other than regular. (`150`, `151`, `155` and
`156` read similarly in English, but their Hebrew shows they concern credit-terms purchases, אשראי /
קרדיט, not refunds.) The
legal refund deadline does not pause for a decline. Refund by another route (bank transfer, for
example), still issue the credit invoice, and record why the card route failed.

## Recurring billing and cancellation

A monthly charge on a saved token is an ongoing transaction (עסקה מתמשכת) under the Consumer
Protection Law. Section 13D(c): the contract ends **within three business days** of the cancellation
notice (six business days if it was sent by registered mail), unless the consumer named a later
date, and from then on the merchant may not charge for goods or services given after it. Section 14I
lists the channels the merchant must accept a cancellation notice through (orally by phone, registered
mail, email, fax if the merchant has one, and online for a transaction that can be made online), and
s.14I(b) requires a site that sells online to place a dedicated, prominent cancellation link on its
home page. These are the merchant's general duties under the statute, not advice on a particular case.
In code this means:

- record the customer's explicit consent to recurring charges and the amount;
- offer an online way to cancel, reachable from a dedicated link on the home page;
- gate every renewal `DebitRegularType` on the subscription's status, so a cancelled subscriber is
  never charged after the cancellation date;
- confirm the cancellation to the customer.

This is a summary for engineers, not the statute; read section 13D and 14I before you design the flow.

**Renewal declines (dunning).** Use the groups in `error-codes.md`: retry a soft or technical failure
on a schedule, never retry a hard decline or a retain-card code, refresh the card with
`/services/UpdateToken` on `506` or an expiry error, and stop after a fixed number of attempts.
Chargebacks and deny lines from the acquirer can be pulled from the Match API
(`MatchApi/GetDenyAndCancellationLines`, see `api-endpoints.md`).
