# Domain checklist: israeli-bank-connector (tax-and-finance)

Bootstrapped 2026-10-12 by a research subagent, then corrected by the updater where an item
contradicted a verified source or a deliberate design decision (each correction is marked).

Scope: analyze Israeli bank and credit-card transactions from israeli-bank-scrapers (via israeli-bank-mcp / il-bank-mcp) or a bank CSV/Excel export. Library state checked 2026-10-12: latest release v6.12.2 (2026-09-29), MIT.

## Must cover (core)

**A. Transaction schema (src/transactions.ts). Each field and variant is a separate computation rule.**
1. `chargedAmount`: the amount actually debited/credited in the account or card bill; this is the ONLY field to sum for spending. Sign convention: negative = money out, positive = money in (refund, salary, transfer in). Source: src/transactions.ts; README result-object block.
2. `originalAmount` + `originalCurrency`: the deal amount in the merchant's currency. For a foreign purchase it differs from `chargedAmount` (FX conversion, fees); for an installment deal it may be the full deal total, not this month's slice. Never sum `originalAmount`. Source: src/transactions.ts.
3. `chargedCurrency` (optional): currency of the charge. Usually ILS; may be USD/EUR for foreign-currency accounts (Leumi FX accounts added in v6.12.0). Do not add amounts across currencies without conversion. Source: transactions.ts; release v6.12.0.
4. `date` vs `processedDate`: `date` = purchase date; `processedDate` = billing/value date (for cards, the monthly charge date). Monthly budgets by purchase use `date`; cash-flow and reconciliation with the bank account use `processedDate`. Source: transactions.ts.
5. `status: 'completed'`: final; include in totals. Source: TransactionStatuses enum.
6. `status: 'pending'`: not yet final; may later reappear as completed with different amount/identifier. Report separately, exclude from closed-month totals and from the accountant export. [Updater note] The bundled script includes pending lines in running totals but prints them separately; leave them out of a closed month or an accountant export. Source: TransactionStatuses enum; opt-in flags `mizrahi:pendingIfNoIdentifier`, `mizrahi:pendingIfHasGenericDescription`, `mizrahi:pendingIfTodayTransaction` (src/scrapers/interface.ts).
7. `type: 'normal'`: a single charge. Source: TransactionTypes enum.
8. `type: 'installments'` + `installments {number, total}` (עסקת תשלומים): each monthly slice is its own transaction. Budget counts only the slice charged this month; remaining commitment = slice x (total - number). Source: TransactionTypes / TransactionInstallments.
9. `combineInstallments: true` option: merges all slices into the first one; totals then differ from the card bill. State which mode the data was fetched in. Source: interface.ts `combineInstallments`.
10. `identifier` (אסמכתא), may be missing: dedup key is (account, identifier) when present, else (account, date, chargedAmount, description). Source: transactions.ts comment "sometimes called Asmachta".
11. `description` / `memo`: merchant name (often Hebrew, truncated, uppercase Latin for foreign merchants) and bank free text; the basis for categorization. Source: transactions.ts.
12. `category` (optional): issuer's own category, only filled when `additionalTransactionInformation: true` (slower). Treat as a hint, not truth. Source: interface.ts.
13. Account-level fields: `accountNumber`, `balance`/`balanceDate` (not implemented for all accounts), `cardType` (`bankIssued` / `companyIssued`), `cardFrame` (credit limit), `savingsAccount` flag. Source: TransactionsAccount interface.
14. `futureDebits[]` (amount, chargeDate, bankAccountNumber) and `futureMonthsToScrape`: upcoming card charges, report as "upcoming", not as spent. Source: interface.ts FutureDebit.
15. `startDate`: each scraper has a minimum look-back; request explains gaps. `enableTransactionsFilterByDate` returns unfiltered data. Source: interface.ts.

**B. Double counting and reconciliation**
16. Card bill appears twice: the monthly card debit in the bank account (e.g. "ישראכרט", "מקס", "כאל") AND the itemized card transactions. Exclude the bank-side card-bill line when card data is also loaded. Source: common practice; both MCP READMEs combine banks and cards.
17. Internal transfers between the user's own accounts, and the card bill, are not spending. Source: common practice (il-bank-mcp `get_financial_summary`).
18. Refunds/credits (זיכוי, positive `chargedAmount`): never counted as spending. [Corrected by updater] NOT auto-netted against a category: nothing in the data distinguishes a refund from a salary, and an earlier version that netted credits reported negative category totals (see optimization-log 1.4.0). Net only rows the user identifies.

**C. Savings vs spending (Israeli context)**
19. Separate deposits to pension (קרן פנסיה), keren hishtalmut (קרן השתלמות), kupat gemel / gemel lehashkaa, and transfers to deposits/savings plans (פיקדון, תוכנית חיסכון) as "savings", not expenses. Identify them by payee name (managing companies: Altshuler Shaham, Meitav, Migdal, Harel, Clal, Phoenix, Menora, More, Infinity, Analyst) on a monthly direct debit. Source: common practice; `savingsAccount` flag in transactions.ts.
20. For a self-employed user, flag pension and keren hishtalmut deposits for the accountant (they affect the user's income-tax position), and state the skill does not compute any relief. Source: Income Tax Ordinance (pension and hishtalmut provisions); accountant domain.

**D. Recurring charges (הוראות קבע / subscriptions)**
21. Detect recurring charges: same payee, similar `chargedAmount`, ~monthly interval; separate bank direct debits (הרשאה לחיוב חשבון) from card standing charges (הוראת קבע בכרטיס). Source: il-bank-mcp `get_recurring_charges`.
22. [Carry, not verified this cycle] How to stop a recurring charge: a bank direct debit is cancelled with the bank, a card standing charge with the card company or the merchant. Exact notice periods and dispute windows were not verified from the current Directive 439 text, so the skill states none.

**E. Categorization of Israeli merchants**
22a. Category map for common Israeli payees: supermarkets (שופרסל, רמי לוי, יוחננוף, ויקטורי, טיב טעם), fuel (פז, דלק, סונול, דור אלון, Ten), transport (רב-קו, Moovit, Gett, Pango, Cello), utilities (חברת החשמל, תאגידי מים, ארנונה/עירייה, בזק, HOT, Partner, Cellcom, פלאפון), health (כללית, מכבי, מאוחדת, לאומית, Super-Pharm), food delivery (Wolt, 10bis/Cibus), Bituach Leumi, taxes. Source: common practice; il-bank-mcp example "Analyze spending patterns of Wolt".
23. Unknown merchants go to "uncategorized" for user confirmation; never guess silently. Source: common practice.

**F. CSV/Excel import path**
24. Bank exports: Hebrew headers, often windows-1255 encoding, dd/mm/yyyy dates, separate חובה/זכות (debit/credit) columns instead of a signed amount, a running balance (יתרה) column, header/footer summary rows to drop. Normalize to the scraper schema (items 1-11). Source: common practice.
25. Card statements (Isracard, Max, Cal) list "סכום עסקה" (deal) vs "סכום חיוב" (charge) and "תשלום X מתוך Y" text; map to originalAmount / chargedAmount / installments. Source: common practice; transactions.ts mapping.

**G. Business-expense export for an accountant**
26. Export only `completed`, `processedDate` in the requested period, the columns date, processedDate, payee, chargedAmount, currency, originalAmount, category, business/private flag, and installment number/total. CSV with UTF-8 BOM so Excel renders Hebrew. Source: common practice.
27. A bank/card line is not a tax invoice: deducting input VAT requires a tax invoice (חשבונית מס) per the VAT Law and VAT Regulations; flag every business expense as "invoice needed". Source: חוק מע"מ s.38; תקנות מע"מ.
28. Mixed-use items (car, phone, home office) are marked for the accountant, not split by the skill. Source: Income Tax Regulations (car/phone expense rules), accountant domain.

**H. Credentials and data safety**
29. Credentials only in environment variables / OS keychain, never in chat or tool arguments; israeli-bank-mcp reads `<BANK_ID>_<FIELD>` env vars precisely to keep them out of LLM history. Source: mottibec/israeli-bank-mcp README.
30. Per-company login fields from `SCRAPERS` (e.g. Discount/Mercantile: id+password+num; Isracard/Amex: id+card6Digits+password; Yahav: username+nationalID+password; OneZero: email+password+OTP). Source: src/definitions.ts.
31. 2FA: OneZero needs `otpCodeRetriever` or `otpLongTermToken`; treat a long-term token like a password. Source: README "Two-Factor Authentication Scrapers".
32. Error types and what to tell the user: INVALID_PASSWORD, CHANGE_PASSWORD (log in on the bank site first), ACCOUNT_BLOCKED (stop retrying, contact bank), TIMEOUT, GENERIC/GENERAL_ERROR, TWO_FACTOR_RETRIEVER_MISSING. Never retry-loop a bad password (lockout risk). Source: src/scrapers/errors.ts.
33. "Local" is only partly true: il-bank-mcp keeps data in local SQLite, but sending transactions to a cloud LLM sends them off the machine. Minimize: mask account and ID numbers, avoid `includeRawTransaction`, and do not paste full statements. Source: il-bank-mcp README; Privacy Protection Law Amendment 13 (in force 14.8.2025).
34. Do not keep `storeFailureScreenShotPath` screenshots (they capture account pages); delete exports after use. Source: interface.ts.
35. Personal use: Financial Information Service Law s.60 addresses accessing a customer's financial data in the course of business (דרך עיסוק), online, using the customer's own login credentials, to provide them a service; the penalty provision (s.57(ב) in the consolidated Wikisource text) makes a breach an offence. An accountant or bookkeeper running the scraper with a client's bank password in the course of their work is the conduct s.60 addresses. The section does not address a person scraping their own accounts. Source: חוק שירות מידע פיננסי, התשפ"ב-2021, ss.2, 57, 60.

## Should cover (advanced)
36. Licensed open-banking alternative: banks must give API access under the FIS Law s.39 to licensed providers per BOI Directive 368 (circular 2778, 7.4.2024; corporations from 14.4.2024). Point business users to an ISA-licensed financial information service provider. Source: Directive 368 circular; FIS Law ss.2, 39.
37. Scraper fragility: screen scraping breaks when bank sites change (v6.12.2 fixed Mizrahi change-password URL, v6.12.1 Visa Cal balance). Pin version, check releases. Source: GitHub releases.
38. Foreign transactions: FX conversion fee and `originalCurrency` != ILS, flag for spending reports. Source: transactions.ts.
39. `optInFeatures` (`isracard-amex:skipAdditionalTransactionInformation`, Mizrahi pending flags) change output; record which were set. Source: interface.ts.
40. Joint accounts: a household budget must not double count when both spouses connect the same account. Source: common practice; FIS Law s.43 (joint accounts).
41. [Carry, not verified this cycle] Israel Invoice model allocation numbers (מספר הקצאה) on B2B invoices: a question for the accountant; the threshold was not verified, so the skill states none.
42. Record retention for business records: keep source documents per bookkeeping instructions (הוראות ניהול פנקסי חשבונות). Source: ITA bookkeeping instructions.
43. Supported company list (18 `CompanyTypes` entries, incl. behatsdaa, beyahadBishvilha, pagi, massad, yahav, union, oneZero) and the core vs full npm package (puppeteer-core). Source: definitions.ts; README.

## Out of scope (explicit), 2026-10-12
- Payment initiation, transfers, paying bills: read-only analysis only; FIS Law covers information, payment services are separately regulated.
- Investment, pension-track, or insurance advice: regulated advice (Regulation of Investment Advice Law, 1995; pension advisor licensing).
- Computing tax liability, VAT returns, or deduction amounts: accountant's work; skill prepares the export only.
- Operating as a service for third parties with their credentials: prohibited by FIS Law s.60.
- Credit scoring or loan decisions: Credit Data Law domain.
- Bypassing 2FA or reverse-engineering long-term tokens via MITM: security risk and possible ToS breach.

## Authoritative sources
- israeli-bank-scrapers: https://github.com/eshaham/israeli-bank-scrapers (README; src/transactions.ts; src/definitions.ts; src/scrapers/interface.ts; src/scrapers/errors.ts; releases v6.12.0-v6.12.2, Sept 2026)
- israeli-bank-mcp: https://github.com/mottibec/israeli-bank-mcp (README: env-var credentials, tools fetch-transactions, two-factor-auth; last push 2026-05-02)
- il-bank-mcp: https://github.com/glekner/il-bank-mcp (README: local SQLite, 8 tools; last push 2025-06-13)
- Financial Information Service Law 2021: https://he.wikisource.org/wiki/חוק_שירות_מידע_פיננסי (ss.1, 2, 3, 39, 43, 57, 60, 81)
- BOI Directive 368 circular 2778 (7.4.2024): https://www.boi.org.il/media/k1dl4le3/2778.pdf
- BOI Directive 439 (direct debit authorization), not fetched by the updater; locate the current consolidated text before relying on it
- Privacy Protection Law Amendment 13 (in force 14.8.2025)
- Income Tax Ordinance ss.17, 45א, 47; VAT Law s.38 and VAT Regulations reg.18; ITA Invoices Israel model
- Note: kolzchut.org.il blocked automated fetch (Cloudflare 403) on 2026-10-12; items 8, 21-22 should be cross-checked there before publishing.
