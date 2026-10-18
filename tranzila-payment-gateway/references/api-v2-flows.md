# API V2 and Hosted Fields request contracts

Companion to SKILL.md Steps 3 to 10. Everything here was read from the rendered vendor pages on 2026-10-18; docs.tranzila.com is a JS app, so render a page in a browser before trusting a plain fetch of it. Field names below are not interchangeable with the iframe / legacy CGI names.

## 1. Card transactions: `POST https://api.tranzila.com/v1/transaction/credit_card/create`

Source: Payments & Billing, Tranzila Transactions API, "create a credit card transaction".

- **The amount is carried by `items`, not by a `sum` field.** Each item has `name`, `type` (e.g. `I`), `unit_price` and `units_number`, with optional `price_type`, `vat_percent`, discounts and more. The page lists no top-level amount field.
- **Card data.** Send a Tranzila token in `card_number`, plus `expire_month`, `expire_year` and `cvv` where required. The vendor's rule: "Full card number integration, permitted only for PCI DSS-certified integrations. For non-PCI DSS-certified integrations, do not send the full card number directly to Tranzila through this API." Tokenise through the iframe or Hosted Fields first.
- **`txn_type`.** `debit` (default), `credit`, `verify` (with `verify_mode` 2 = J2, 5 = J5, 6 = standing-order initialisation), `force` (capture a J5), `sto` (standing-order charge, with `reference_txn_id` of the verify), `cancel`, `reversal` (release a J5).
- **Refund, cancel and reversal need the original's approval number.** `authorization_number` is "REQUIRED when txn_type is `credit`, `reversal` or `cancel`", alongside `reference_txn_id`. A `credit` example also carries the token in `card_number`, the expiry and `items`. Missing it returns application error 22101 ("Empty authorization number"); 22100 means it does not match the original, 23002 means the transaction was already credited. So persist the approval number at charge time (`auth_number` on API V2 and Hosted Fields responses, `ConfirmationCode` on the legacy CGI). The DirectNG iframe response sample does not list it, so for iframe charges retrieve it from the Transactions API (section 6) or confirm with Tranzila which notify field carries it.
- **Installments.** `payment_plan` 1 (regular), 6 (credit installments, minimum 3 payments, the cardholder's own agreement with the card company), 8 (regular installments), with `installments_number`, `first_installment_amount`, `other_installments_amount`.
- **Cardholder ID** is `card_holder_id`.
- **End-customer details and the allocation number.** Anything you want on the transaction record goes in `user_defined_fields` (`[{"name": ..., "value": ...}]`, names defined first under Additional Fields for Transaction, up to 25), not in `client`. The ITA allocation number is issued automatically when `card_holder_id` matches the customer's registered business ID; otherwise send `{"name": "business_id", "value": "<digits>"}` in `user_defined_fields`. If neither is right the charge still succeeds and no allocation number is issued. `DCdisable` is also sent this way on the API.
- **Response.** JSON with `error_code` (0 = success), `message`, and `transaction_result.processor_response_code` (the SHVA code, `000` approved). The HTTP status can be 200 on a failed transaction; read the body.

## 2. 3D Secure on the API

Source: Tranzila Api 3DS, "Create" and "Complete".

Request it per transaction on the same create call: `activate_3ds: "Y"` and a `3ds_settings` object holding `browser` data (`user_agent`, `accept_header`, `ip`, `language`, `color_depth`, `screen_height`, `screen_width`, `time_zone`, `java_enabled`, `window_size`), `force_txn_on_3ds_fail`, `force_challenge` and `auth_3ds_redirect`. If a challenge is needed, open the returned `challengeUrl` in the customer's browser; the challenge result is redirected to the `auth_3ds_redirect` URL; then call `POST /v1/transaction/credit_card/3ds/complete`. See `3ds-flow.md` for the response shape.

## 3. Hosted Fields keys (`fields.charge()`)

Source: Payments & Billing, Hosted Fields, "Request Keys".

`terminal_name`, `amount`, `thtk` (Handshake V2), `currency_code` (ILS, USD, EUR), `tran_mode` (A debit, V J5, N J2), `payment_plan` (1 / 6 / 8), `first_installment_amount`, `other_installments_amount`, `total_installments_number` (for plans 6 and 8), `tokenize`, `notify_url` (the server-to-server IPN), `requested_by_user`, `force_txn_on_3ds_fail` (**defaults to `Y`**, so a failed or unsupported 3DS still charges without liability shift unless you send `N`), `force_challenge`, `pdesc`, `json_purchase_data`. The cardholder ID is `card_holder_id_number`; `business_id` is passed as an ordinary non-hosted field. The response is under `transaction_response` (`success`, `processor_response_code`, `transaction_id`, `auth_number`, `token`, `expiry_month`, `expiry_year`, ...) plus a top-level `response_hash`, and pre-transaction validation errors come back in an `errors` array before anything reaches SHVA.

Set `notify_url` on every charge. The charge result otherwise lands only in the browser callback, so a closed tab after an approved charge leaves a paid order your server never heard about.

## 4. Bit

Sources: Bit, "Bit - Init"; Hosted Fields, "Bit payment with hosted fields".

`POST https://api.tranzila.com/v1/transaction/bit/init` requires `success_url`, `failure_url`, `notify_url` and `items` ("The amount of the transaction is calculated from the items details. There must be at least one item."). The response's `sale_url` is displayed **in an iframe** that shows the QR code and a phone-number field; on completion the iframe redirects to the success or failure URL, and `notify_url` receives the outcome regardless of success or failure. Refunds have their own Bit refund endpoint.

Vendor conflict to surface, not resolve: the Bit page says Hosted Fields is not supported, while the Hosted Fields page documents `fields.chargeBit({terminal_name, amount, currency_code, thtk, ...})`. Confirm with Tranzila support before building Bit on Hosted Fields.

## 5. Allocation number by surface

| Surface | ID field | Business ID field |
|---|---|---|
| Iframe (DirectNG) | `myid` | `business_id` parameter |
| Hosted Fields | `card_holder_id_number` | `business_id` non-hosted field |
| API V2 | `card_holder_id` | `user_defined_fields` entry named `business_id` |

In every case define `business_id` first under Terminal Settings, Additional Fields for Transaction.

## 6. Server-side confirmation (Transactions / Reports API)

Source: Reports, Tranzila Transaction Reports API.

Before fulfilling an order on an unsigned notify (the iframe Notify POST), confirm the transaction from your server: `https://api.tranzila.com/v1/transactions` returns transactions without product lines, and `https://report.tranzila.com/v1/transaction` returns them with product lines and supports `ufields` (user-defined fields) and `dfields` (core fields such as amount and date) filters. Both use the same four HMAC headers. Filtering on your own `user_defined_fields` order reference is the clean way to match.

## 7. Invoices API

Source: Invoices, Invoices API.

The Invoices API is served from `https://billing5.tranzila.com` and issues documents such as tax invoice / receipt (IR), bound to a transaction by its index. The automatic per-transaction invoice needs the paid Invoices module; its line items come from `json_purchase_data`, `pdesc`, `IMaam` and `Ilang` on the iframe and Hosted Fields, and from `items` on the API. Read the Invoices section for document types, credit documents and the exact request body before building on it.
