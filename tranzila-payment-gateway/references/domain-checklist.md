# Domain coverage checklist, tranzila-payment-gateway

Anchor for expert review. Scope: integrating Tranzila payments (iframe, hosted fields, API V2, tokens, installments, refunds, 3DS, Bit) into Israeli apps.

## Must cover (core)
- Integration patterns + PCI scope (typically Iframe SAQ A with the SAQ A r1 script-attack eligibility criterion and FAQ 1588, Hosted Fields SAQ A or A-EP, API V2 SAQ D, attributed to PCI SSC and subject to the acquirer), plus the prohibition on storing CVV or full PAN after authorization (PCI DSS 3.3.1).
- Auth: legacy supplier+TranzilaPW; API V2 = 4-header HMAC-SHA256 (app-key + request-time + nonce + access-token) at api.tranzila.com/v1.
- Endpoints: directng.tranzila.com/{supplier}/iframenew.php (direct.tranzila.com is Legacy Deprecated, support ends 1 January 2027); secure5.tranzila.com CGIs (tranzila31/36a/31tk/71u) as legacy, no longer on docs.tranzila.com; API V2 token charge = token in `card_number` on /v1/transaction/credit_card/create.
- Hosted Fields: `fields.charge()` performs the charge in the browser with a server-issued Handshake V2 `thtk` (mandatory); token only with `tokenize: true`.
- Handshake V2 (/v2/handshake/create, `thtk`, 20 minutes, 912791 on amount mismatch, Token Module) as an amount lock, distinct from `response_hash` callback integrity.
- Standing orders: /v2/sto/create and /v2/sto/update (V1 create/update deprecated), /v1/stos/get, iframe tranmode=J and My Billing recur_* parameters, API txn_type=verify + verify_mode=6 then txn_type=sto.
- Israeli payment types: installments (cred_type=8, npay/fpay/spay, fpay+npay*spay=sum), credit types 1/6/8, currency codes 1/2/978/826, tokenization (TranzilaTK treated as opaque, tranmode K/VK/AK/NK), refund (tranmode=C{index} against tranzila71u.cgi with CreditPass and authnr).
- Error handling: HTTP 200 on failure, read the Response field; the SHVA table plus the separate 3DS set 900-930, and the application-level codes (Hosted Fields errors[], API error_code such as 22101); verify every code against the official Transaction Response Codes page and never explain a code that is not on it.
- Bit dedicated API + constraints (NIS, >5 NIS, Visa/Isracard, Max-only not supported).
- Webhook signature verification (don't trust inbound shape).
- Allocation number via Tranzila, per surface: iframe `myid` + `business_id`; Hosted Fields `card_holder_id_number` + `business_id`; API V2 `card_holder_id` + `user_defined_fields` entry `business_id`. No number if none is right.
- API V2 request contract: amount in `items` (no `sum`), `authorization_number` required for credit/cancel/reversal, no raw PAN unless PCI DSS certified, 3DS via `activate_3ds` + `3ds_settings`.
- Server-side confirmation of unsigned iframe notifies via the Transactions / Reports API before fulfilment; Hosted Fields `notify_url` IPN always set.
- ITA allocation number for B2B invoices, selected by the invoice's OWN date across the full schedule: none before May 2024, then 25K (May 2024), 20K (Jan 2025), 10K (Jan 2026), 5K (Jun 2026). The boundary is 'exceeds', zero-rated and exempt-only invoices are excluded, and a missing number blocks the buyer's deduction without voiding the invoice.

## Out of scope (explicit)
- Cardcom (use cardcom-payment-gateway), general accounting. Re-checked 2026-10-18: still a separate skill and not a Tranzila question.
- MASAV bank standing orders through Tranzila's MASAV API (a separate bank-clearing product needing an institution code and a paid module). Added 2026-10-18: a user could ask, so the skill should say it exists and route to the vendor's MASAV API page rather than explain it.
- EMV device (Pay Bridge) transactions: card-present hardware, outside an online-payments skill. Added 2026-10-18.

## Authoritative sources
- Tranzila docs: https://docs.tranzila.com/
- Tranzila site: https://www.tranzila.com
- tranzilajs: https://github.com/NirTatcher/tranzilajs
