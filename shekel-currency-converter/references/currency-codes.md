# Currency Codes and NIS Conversion Notes

## Published Currencies (14 total)
The Bank of Israel publishes a representative rate for exactly these 14 currencies:
USD, GBP, JPY, EUR, AUD, CAD, DKK, NOK, ZAR, SEK, CHF, JOD, LBP, EGP.

## Primary Currencies

| Code | Currency | Hebrew | Illustrative Rate (NIS) | Unit |
|------|----------|--------|-------------------------|------|
| ILS | Israeli New Shekel | shekel chadash | 1.0000 | 1 |
| USD | US Dollar | dolar | about 2.97 | 1 |
| EUR | Euro | euro | about 3.47 | 1 |
| GBP | British Pound | lira sterling | about 4.05 | 1 |
| JPY | Japanese Yen | yen | about 1.87 | 100 |
| CHF | Swiss Franc | frank shveitzi | about 3.70 | 1 |

NOTE: These figures are illustrative snapshots of the 2026-08-26 publication and move daily. Always fetch the live or dated rate from the API; never quote these as the actual rate.

## Tax-Relevant Uses
- **Foreign-source business income and expenses:** the Income Tax Conversion Rules, 5764-2003 (Rule 2) translate at the rate on the date produced, accrued or incurred AND on the date received or paid. Israeli-source income billed in foreign currency follows the books' accrual or cash basis; ask the accountant.
- **VAT on a service:** charged on receipt of the consideration (VAT Law s.24), so the payment date governs, except for a dealer above NIS 15 million who must keep books under Schedule 11 of the Bookkeeping Instructions, and some special cases (s.29(1a)).
- **Year-end rate:** sourced for foreign-source interest/linkage principal (Conversion Rules 3(b)), late-paid passive income (3(c)), foreign professional companies (4), CFC profits (5) and late-paid foreign tax (6(2)). Revaluing a business's own balances is an accounting question; ask the accountant.
- **VAT and customs on imported GOODS:** Do NOT use the bare BOI representative rate. The Customs Rules, 5749-1989, use the BOI representative rate plus 0.5%, fixed weekly from the preceding Friday's publication unless the rate moves a cumulative 3% or more before release. The Tax Authority publishes the resulting customs rates; prefer the published figure. Imported intangible goods use the bank's purchase rate when the currency was bought or transferred (VAT Law s.11(b)); for reverse-charge imported services the exchange rate is not fixed by any source this skill has verified.

## NIS Symbol and Formatting
- Currency code: ILS (ISO 4217)
- Symbol: shekel sign (Unicode U+20AA)
- Common display: NIS or ILS
- Format: comma for thousands, period for decimals (1,234.56), never 1.234,56
- Symbol placement: the Unicode CLDR Hebrew pattern puts the sign after the number (1,234.56 ₪); English text usually puts it before (₪1,234.56)
