# Domain Checklist: pelecard-payment-gateway

Scope: integrate the Pelecard (unofficial/community-documented) payment gateway. Category: tax-and-finance (payments/dev).

## Must cover (core)
- Hosts: gateway21.pelecard.biz (current generation) and gateway20.pelecard.biz (older generation) serve the SAME API; the hostname is not an environment switch. Environment is decided by the terminal + credentials. Credentials triple server-side only.
- The two parameter surfaces: /PaymentGW/* (terminal, Total, Currency, ParamX, TransactionId) vs /services/* (terminalNumber, total, currency, paramX). Mixing them is the most common silent failure.
- Refunds: /services/ReverseTransaction (debitTrxId + NewAmount in agorot, same terminal as the charge, else 507), as used by Pelecard's own plugin since v1.5.3. Explicit void before broadcast: DeleteTran; hold release: DeleteIshur. There is NO refund endpoint under /PaymentGW. Whether ReverseTransaction voids pre-broadcast is unpublished.
- The Shva broadcast (שידור) cycle: /services/Broadcast, GetBroadcast, GetTransDataBeforeBc. An approval number is not settled money.
- J5 capture via authorizationNumber on the debit, sent from the authorizing terminal; J9 pending via Pending*Type + ClearPendingBy*.
- Token lifecycle beyond creation: ConvertToToken, RetrieveToken, UpdateToken, CheckCreditCardForToken.
- 3DS2 as an ordered sequence: Initiate3DSAuthenticationProcess -> eci/xid/cavv carried into the debit.
- Status codes are fully public via the credential-free /services/GetErrorMessageEn and GetErrorMessageHe.
- Outbound idempotency (unique paramX per attempt; look up before re-charging), not only inbound IPN dedupe.
- PCI scope: token vs PAN on /services; ClientSecure.js on the merchant page. Never log ConfirmationKey or CardHolderID.
- Iframe create-session (PaymentGW/init) returning URL + ConfirmationKey; money in agorot; Currency 1 = ILS.
- ActionType J4 (sale) / J2 (validation only, no charge) / J5 (auth-later) / J5h - and the "wrong ActionType silently changes whether money moves" warning.
- Server-side callback validation: match the callback ConfirmationKey to the stored Phase-1 value AND re-verify via PaymentGW/GetTransaction (confirm DebitTotal + PelecardTransactionId). No documented IPN signature (no HMAC) - the server-to-server lookup is the only authoritative source. Dedupe on PelecardTransactionId.
- Tokenization / recurring (CreateToken, IsToken, MIT/3DS exemption), refunds, 3DS2, Apple Pay (ClientSecure.js), Bit (single payment, ILS, no saved card; caps from the merchant's own agreement, allpay's 5,000 NIS is illustrative).
- Recurring billing cancellation: Consumer Protection Law s.13D(c), contract ends within 3 business days of notice (6 by registered mail); gate renewals on status. Refund idempotency and a cumulative refund cap.
- Israeli Consumer Protection Law distance-selling refunds (14-day cancel, 14-day refund, fee cap 5% or 100 NIS).

## Should cover (advanced)
- Reconciliation safety net (poll GetTransaction for sessions with no IPN); DebitApproveNumber join to the Shva clearing report; the Match API (match-api.pelecard.biz) for settlement reconciliation, not payments; pairing with green-invoice for the tax document.

## Out of scope (explicit)
- Cardcom / Tranzila / Grow-Meshulam single gateways; multi-gateway orchestration; invoice generation. Re-checked 2026-10-18: each has its own skill (cardcom-payment-gateway, tranzila-payment-gateway, grow-payment-gateway, israeli-payment-orchestrator, green-invoice), so a user asking for them is routed, not left unanswered.

## Authoritative sources
- github.com/dofinity/pelecard (PHP wrapper: PaymentGW/init, ValidateByUniqueKey, agorot, Currency 1); wordpress.org/plugins/woo-pelecard-gateway (gateway21, refunds, tokenization, Apple Pay); postman.com/peleteam/pelecard-public (Gateway21 collection); allpay.co.il (Bit); Consumer Protection Law 14C-14E.
