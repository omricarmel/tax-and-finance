# Changelog

## 1.3.0 - 2026-10-19

A destination re-check (every named site re-opened in a real browser against a fabricated-path control) found one source that had changed and one rule the skill was missing.

- **Kol-Zchut narrowed the 4-month precondition.** The page now reads "a conversation (by phone or chat)"; it used to include email. Both language files said "phone, chat, or email". Corrected.
- **A coupon from another site can cancel a cashback rebate.** Cashback.co.il's terms (s.19) say the rebate may not be paid when a coupon or discount from another site or service is used, or when the order is paid later from a cart saved outside the referred visit. The skill told shoppers to stack a code on a cashback visit without warning that the two can cancel each other. Step 4 now carries a stacking order and that check.
- **Split parcels.** Splitting one order to stay under the 75 USD exemption does not work: parcels from the same supplier within 72 hours are taxed as one shipment. Added to the landed-cost gotcha.
- **Payment line in every summary.** "Pay by credit card, not Bit, PayBox or bank transfer" lived only inside the scam-site rubric, so a normal coupon run could finish without it. Step 5 now requires it.
- **Payment line no longer overpromises a chargeback.** Kol-Zchut's credit-transaction page says the issuer stops the REMAINING installments on non-delivery after a cancellation notice and does not refund what was already paid. Both files now say exactly that, and tell the shopper to ask the issuer about disputing the charge rather than promising one.
- **The parcel-SMS warning contradicted the skill's own source.** It said real carriers never ask for payment by SMS; Kol-Zchut says most couriers do notify a tax payment by SMS or email. Rewritten: the tell is paying through the link, not the message.
- **Deferred items from 1.1.0 partly closed:** a global-marketplace note, Facebook deal groups as a search surface, grocery coupon codes explicitly in scope, the open-account-then-re-enter cashback step, the Example 3 Israeli-business qualifier, KSP in Example 2, and a warning that coupon auto-apply extensions can take over a cashback referral. Still open and re-logged: marketplace-native levers (coins, welcome deals, free-shipping thresholds) and a price-history source, reservist and student benefit programs, and lever-type ranking in the script.
- **`rank_codes.py` now reads an optional `expires` (YYYY-MM-DD).** An expired code is dropped and named on stderr; an unreadable expiry is kept, flagged in the table, and capped at medium confidence (including when the input states a higher confidence). `--today` sets the comparison date. Before this the description promised expiry checking and nothing in the script did it.
- All other destinations confirmed alive and on-topic: couponim.co.il, cashback.co.il, buyme.co.il, max.co.il/benefits/lobby, benefits.isracard.co.il, cal-online.co.il/benefits, hvr.co.il. Customs figures unchanged (75 USD, 130 USD window 25.02 to 01.06.2026, 18% VAT band to 500 USD).

## 1.2.0 - 2026-08-27

A link-rot sweep that came back clean, and two script defects that did not.

**Every named destination was verified alive by navigation, not by status code**, each with a per-host control request to a fabricated path so a soft-404 could not pass as a hit. couponim.co.il, cashback.co.il, buyme.co.il and max.co.il/benefits/lobby all returned 200 against controls that returned 404 with a different body, and their page titles still describe the service the skill claims (coupon aggregator, cashback platform, gift cards, card benefits). benefits.isracard.co.il and cal-online.co.il/benefits/ return 403 and 400 to a plain fetch with bodies **byte-identical** to their controls, so those two were confirmed in a real browser instead: both render their benefits hubs. No dead or renamed destination was found.

- **`scripts/rank_codes.py` silently dropped unrecognised keys.** Feeding it a plausible-looking candidate list with `expires`, `min_cart` and `new_customers_only` produced a fully-formed table with every column showing `-`, ending in "Try this first: SAVE20" for a code it knew nothing about. It now names the ignored keys on stderr, and refuses outright when an item carries none of the recognised keys rather than rendering a row of dashes.
- **The documented field name was wrong, which is what produced those dashes.** Both language files described the input as "(code, source, **date**, discount, conditions)" while the script reads **`date_seen`**. Anyone following the documentation got blank columns. The exact key set is now spelled out in both languages, with the `date_seen` trap called out, plus a note that `discount` and `conditions` are free text and that the script ranks and formats but does not parse dates or evaluate expiry.
- **A missing input file raised a raw `FileNotFoundError` traceback.** It now prints one line and exits 1.
- **"Moadon Chaver (hvr.co.il, operated by Isracard)" was an unverifiable ownership claim.** The site itself does not state it. Dropped. Replaced with what the visit actually established: hvr.co.il is the career-soldier and retiree club, and it sits **behind a member login** (teudat zehut plus password), so the shopper has to check it themselves and this skill cannot read it, which is more useful to say than who owns it.

The customs figures were re-checked against `israeli-product-price-comparator`, corrected in the same batch, and match exactly: 75 USD from 2 June 2026, the 130 USD window from 25 February to 1 June 2026, VAT-only from 75 to 500, and commercial treatment above 1,000.

## 1.1.1 - 2026-08-19

### Fixed

- Translated section headings that had been left in English in SKILL_HE.md, where they rendered as-is on the Hebrew page. Hebrew is the site's default locale, and the skill validator never checked the Hebrew file, so these went unnoticed.

