# 3D Secure V2 Implementation for Tranzila

## Overview

3D Secure V2 (3DS2) adds a cardholder authentication step between your server and the card issuer. It shifts fraud liability from the merchant to the issuer for authenticated transactions. Tranzila implements 3DS2 via a **redirect flow** -- the customer is redirected to their bank's authentication page, then returned to your site.

## Flow (API V2)

```
1. Customer submits payment on your site
2. Your server calls POST /v1/transaction/credit_card/create with activate_3ds="Y"
   and a 3ds_settings object (browser data, force_txn_on_3ds_fail, force_challenge,
   auth_3ds_redirect)
3. Either the card authorises frictionlessly (result returned now, flow finished),
   or the response carries a challengeUrl
4. Open challengeUrl in the customer's browser (OTP, app approval, biometric)
5. The challenge result is redirected to the auth_3ds_redirect URL you sent in step 2
6. Your server calls POST /v1/transaction/credit_card/3ds/complete with
   {track_id, terminal_name}
7. Read transaction_result.processor_response_code, error_code and t3ds_data
```

## Enabling 3DS

**On the API** it is per transaction: send `activate_3ds: "Y"` plus `3ds_settings`, whose `browser` object carries `user_agent`, `accept_header`, `ip`, `language`, `color_depth`, `screen_height`, `screen_width`, `time_zone`, `java_enabled` and `window_size`. Collect these from the customer's browser at checkout; they feed the issuer's risk decision.

**On Hosted Fields** the optional 3DS keys go inside `fields.charge()`. Note that `force_txn_on_3ds_fail` defaults to `Y` there, so a failed or unsupported 3DS still charges, without liability shift, unless you send `N`.

**On the iframe**, 3DS is handled inside the iframe once Tranzila has enabled it on the terminal; contact Tranzila support (073-222-4444) to enable it.

## Response Fields for 3DS

After the authentication flow completes, Tranzila includes these additional fields:

On API V2 the 3DS result is **nested under a `t3ds_data` object**, and the transaction result sits beside it in `transaction_result`. This is the shape the vendor documents for the 3DS `complete` call:

```json
{
  "error_code": 0,
  "message": "Success",
  "transaction_result": {
    "processor_response_code": "000",
    "transaction_id": "372803",
    "token": "...",
    "last_4": "1029",
    "card_mask": "458097******1029",
    "card_locality": "domestic"
  },
  "t3ds_data": {
    "version": "1.0",
    "statusCode": "YA",
    "statusMessage": "Authenticated successfully.",
    "xid": "...",
    "cavv": "...",
    "eci": "05"
  }
}
```

| Field | Description |
|-------|-------------|
| `transaction_result.processor_response_code` | The SHVA code, `000` = approved |
| `error_code` | Application error code. `900` means the transaction failed during 3D Secure validation, and the HTTP status is still 200 |
| `t3ds_data.statusCode` / `statusMessage` | The authentication outcome, e.g. `YA` with "Authenticated successfully." |
| `t3ds_data.eci` | Electronic Commerce Indicator, the authentication level |
| `t3ds_data.xid` | Transaction identifier from the 3DS flow |
| `t3ds_data.cavv` | Cardholder Authentication Verification Value |

**There is no flat `three_ds_status` field with `Y` / `A` / `N` / `U` / `R` values.** Earlier versions of this file documented one; it appears in no vendor source. Read `t3ds_data.statusCode` and `error_code` instead, and do not branch on a status letter this API does not return.

The flow itself starts with the ordinary `POST https://api.tranzila.com/v1/transaction/credit_card/create` (the vendor's "3DS Create" page documents that same path: a 3DS V2 card either authorises automatically or returns a challenge), and after the challenge you call `POST https://api.tranzila.com/v1/transaction/credit_card/3ds/complete` with `{track_id, terminal_name}`. Related request options worth knowing: `auth_3ds_redirect.url` sets the redirect target, `force_challenge` forces a challenge, and `force_txn_on_3ds_fail` (Y/N) decides whether the charge proceeds when authentication fails, which is a liability decision, not a technical one.

### ECI Values

The ECI values below are the card-scheme conventions, not a Tranzila-published table. `t3ds_data.eci` carries whatever the scheme returned (the vendor's own example shows `"eci": "05"`), so read it, log it, and confirm the mapping with your acquirer before you make a liability decision on it.

| ECI | Card Network | Meaning |
|-----|-------------|---------|
| `01` | Mastercard | 3DS authenticated |
| `02` | Mastercard | 3DS attempted |
| `05` | Visa | 3DS authenticated |
| `06` | Visa | 3DS attempted |
| `07` | Visa / Mastercard | No 3DS / not enrolled |

## Fallback Handling

Not all transactions will go through 3DS. Handle these cases:

**Card/issuer does not support 3DS:**
- Tranzila processes the transaction as a regular (non-3DS) charge
- `eci` will be `07` (Visa) or empty
- Liability remains with the merchant
- No action needed -- the transaction completes normally

**Customer abandons authentication:**
- Nothing comes back to your `auth_3ds_redirect` URL, so `3ds/complete` is never called
- Implement a timeout on your side for a challenge the customer never completes, and decide in advance whether an abandoned challenge is a failed sale or a retry
- Display a "payment not completed" message and allow retry

**3DS system unavailable:**
- Tranzila falls back to non-3DS processing
- Transaction may still succeed with `Response=000` but without liability shift
- Log the `eci` value to track which transactions were authenticated

**Response code 900:**
- Authentication explicitly failed
- Do not retry automatically with 3DS
- Offer the customer the option to retry or use a different card

## Israeli Issuer Notes

- **Isracard, Visa Cal, and Max (formerly Leumi Card)** all support 3DS V2 for Visa and Mastercard branded cards
- Coverage differs by scheme and by issuer, and Israeli issuer behaviour (which challenge method appears, which brands fall back to non-3DS) is not published by Tranzila. Do not tell a merchant what a given brand will do; test it on their own terminal and read the result out of `t3ds_data`.
- Some Israeli business cards (kartis ishi) may be exempt from 3DS requirements based on terminal configuration
- Test 3DS on your terminal before going live, and ask Tranzila support which sandbox scenarios their environment can simulate for you
