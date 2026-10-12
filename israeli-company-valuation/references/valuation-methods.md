# Valuation Methods Reference

Method selection, multiple definitions, and the approaches that apply where a standard DCF does not.

## Choosing the governing approach

| Company profile | Primary | Why |
|---|---|---|
| Profitable, stable, forecastable | Income (DCF) | Cash flow is the economic substance |
| Asset-heavy, holding company, real-estate-holding | Asset / NAV | Value sits in the assets, not the earnings stream |
| Loss-making with no credible turnaround forecast | Asset / NAV, as a floor | A DCF on negative cash flow produces a meaningless negative |
| Dense peer set, listed or transacted | Market multiples | The market has already priced the risk |
| Pre-revenue or venture-backed | Round-based methods plus allocation | No forecastable cash flow exists to discount |
| Cyclical at a cycle extreme | DCF on a normalized mid-cycle, never on a peak or trough year | Multiples on a peak year embed the peak |

Always run at least two and reconcile. A single-approach valuation is not reviewable.

## Multiple definitions and the consistency rule

The numerator and denominator must sit on the same side of the capital structure.

| Multiple | Numerator | Denominator | Pairs with |
|---|---|---|---|
| EV / EBITDA | Enterprise value | Pre-interest, pre-tax, pre-D&A | Correct |
| EV / EBIT | Enterprise value | Pre-interest | Correct |
| EV / Sales | Enterprise value | Pre-interest | Correct, weak unless margins are comparable |
| P / E | Equity value | Post-interest, post-tax | Correct |
| P / B | Equity value | Equity book value | Correct |

Wrong pairings, both common and both wrong: enterprise value over net income, and market capitalisation over EBITDA.

Notes on applying multiples in Israel:

- The Israeli listed peer set is thin in most sectors. Global sector data is often the only workable source, and the substitution itself must be disclosed.
- A multiple derived from listed companies embeds liquidity that a private company does not have. That is part of what the marketability discount addresses. Do not silently apply a listed multiple to a private company and then also skip the discount.
- Match the multiple to the same normalized earnings figure you built in the normalization bridge, not to reported earnings.
- Listed sector multiples are not small-business multiples. A two-partner owner-managed company is smaller, more dependent on its owners, and sold into a much thinner pool of buyers than the listed companies behind a sector median, so treat a listed multiple as an upper bound and prefer private-transaction comparables where any exist. We are not aware of a published Israeli study of small-business transaction multiples; say so rather than inventing one, and if you rely on one, name it, and treat an implied multiple far above private-deal evidence as a red flag.

## Asset / NAV approach

Adjust each balance sheet line from book to market:

- Real estate: needs a licensed appraiser. Flag it, do not estimate it.
- Machinery and equipment: market or depreciated replacement cost.
- Receivables: net of a realistic bad-debt view, not the book provision.
- Inventory: net of obsolescence.
- Intangibles developed in-house: usually absent from the books entirely.
- Liabilities: including contingent ones and any severance provision shortfall.

NAV usually sets a floor for a going concern. If DCF lands below NAV, ask whether the business is worth more broken up than continued, and say so.

## Pre-revenue and venture-backed companies

A standard DCF fails here because there is no forecastable cash flow. Use:

| Method | When |
|---|---|
| Backsolve from the last priced round | A recent arm's length round exists |
| Option pricing model allocation | Multiple share classes with different rights |
| Venture capital method | An exit value and a target return can be reasoned |
| Scorecard or comparable-round benchmarking | Very early, no round yet |

**The allocation waterfall matters more than the headline number.** A company with a preferred round does not have one value per share. Liquidation preferences, participation rights, and conversion mean ordinary shares are worth materially less than preferred shares at the same headline valuation. Valuing ordinary shares as a pro-rata slice of the post-money valuation is simply wrong, and it is the most common error in early-stage Israeli valuations.

Always ask for the cap table with the rights attached, not just the ownership percentages.

## Normalization bridge

Present it as a visible table, from reported to normalized:

| Line | Effect |
|---|---|
| Reported EBITDA | Starting point |
| Owner salary adjustment to market | Usually the largest single item |
| Related-party rent to market | |
| Private expenses run through the company | |
| One-off legal, restructuring, or war-period items | |
| Grant income treatment | |
| Normalized EBITDA | The figure multiples and DCF should use |

## Sensitivity and presentation

The output is a range. Build the grid across:

- WACC, stepped around the central estimate.
- Terminal growth, stepped around the central estimate.
- The marketability discount, stepped across the band you can support.

Present the grid, the range, and the midpoint labelled explicitly as a midpoint rather than as the answer.

## Cross-check discipline

After running the approaches, reconcile:

1. Does the DCF sit inside the multiples range? If not, which assumption drives the gap?
2. Does either sit below NAV? If so, address break-up value.
3. Does the implied exit multiple from the terminal value look sane against current sector multiples? An implied exit multiple far above today's sector median means the terminal assumption is doing the work, and that must be stated.

## Discounts and the levels-of-value ladder

Three things decide the rung, and percentage alone decides none of them:

1. **What the articles actually give this block.** Ordinary resolutions pass by simple majority, but reserved matters, veto rights, board appointment rights and special majorities are set in the articles and the shareholders' agreement. A large minority holder with vetoes holds a blocking position and is not a plain minority.
2. **Who the buyer is.** This is the one most often missed. A stake sold to an existing holder who thereby crosses into full or majority control is a control-consolidating purchase. That block carries swing value, and in practice it can command a premium rather than a discount. Applying a textbook minority discount in that situation systematically underprices the seller. If the buyer ends up at or near full ownership, say explicitly that a discount is likely inappropriate and that a control premium is arguable.
3. **Whether tag-along or drag-along equalises the per-share price.** If the minority is contractually entitled to the same price per share as the majority, much of the rationale for a discount disappears.

Never stack a marketability and a control discount without justifying each one independently. Careless stacking is the most challenged move in a review.

### Placing a marketability discount

No Israeli regulator publishes a range, and we are not aware of a published Israeli empirical study, so the discount has to be argued from the facts of this holding. The factors practitioners weigh, none of which is a number on its own:

- **The pool of likely buyers.** When the natural buyer is an existing shareholder, or the company itself, the marketability rationale largely disappears, because the holding already has a ready buyer.
- **Transfer restrictions** in the articles and the shareholders' agreement: rights of first refusal, consent requirements, lock-ups. Tag-along and drag-along rights point the other way.
- **Distribution history and policy.** A holding that pays regular dividends is easier to hold and to sell than one whose only return is an eventual exit.
- **Expected holding period and exit route.** A planned sale or listing shortens the period the discount compensates for.
- **Size of the block and the company's financial strength.** A larger block and a stronger company draw more buyers.

The empirical support comes from international study families: restricted-stock studies, pre-IPO studies, and option-based models such as the protective put. We are not aware of an Israeli one. Name the specific study and its vintage, and explain where on its range this holding sits by reference to the factors above.

## Purchase price allocation after an acquisition

A buyer that consolidates the target allocates the price, under the applicable financial reporting framework, to identifiable assets and liabilities, including intangibles such as customer relationships, technology and brands, with the remainder as goodwill. That is a fair-value exercise for financial statements, a different standard of value from the market value this skill estimates. Flag it to a buyer who reports consolidated statements and route it to the auditor; do not perform it here.

## Discount rate components

The risk-free rate and the Israel country risk premium are handled in SKILL.md Step 5, because they are the Israel-specific, fast-drifting inputs. The remaining components are set out here.

**Beta.** A private company has no observable beta. Take industry betas from a peer set, unlever at the peers' structure and tax rate, then relever at the subject's target structure using the subject's Israeli effective rate from Step 4.

Consider a total beta where the owner is undiversified, which is the normal case for an Israeli private company whose owner holds most of their wealth in it: a market beta prices only the risk a diversified investor cannot shed, while an owner with everything in one company bears the total risk. A market beta for a sale to a diversified buyer and a total beta for a valuation from the owner's perspective is a defensible distinction. State which one you used and why.

**Size premium.** An Israeli private company almost always sits below the smallest listed size bucket, and conventional practice adds a size premium. Treat that as contested, not settled: part of the literature argues the premium has largely disappeared from the data. Present it as a choice you can defend rather than as a correction whose omission would be an error. We are not aware of a published Israeli-specific size study, so practitioners import US empirical data, and the primary dataset is paywalled. Name the dataset and vintage you are using. If you do not have access to one, say so and present the valuation across a band of size premia instead of asserting a figure you cannot source.

**Company-specific premium.** Key-person dependency, customer concentration, thin management depth. Reason it out loud rather than adding a round number.

**Cost of debt and WACC.** Take the pre-tax cost from the company's actual borrowing rate, or build it synthetically as a spread over the shekel government yield. Apply the tax shield at the Step 4 effective rate. Weight at market values, state whether you used the target or the actual capital structure, and note that market-value weighting is circular and resolved by iteration.

## Documentation benchmarks used in Israeli practice

Israel has no licensing statute for business valuers, unlike real estate appraisal, which the Real Estate Appraisers Law reserves to licensed appraisers. So no statute tells a private-company valuation what it must contain. The closest statutory benchmark is regulation 8ב of the Securities Regulations (Periodic and Immediate Reports), which binds only reporting corporations but is the checklist reviewers instinctively reach for. When a material valuation is used in a periodic report, it must disclose in a table, among other things:

- the identity and characteristics of the valuer, including education, experience, and dependence on whoever commissioned the valuation, and any indemnity agreement with the valuer;
- the valuation model used;
- the assumptions, including the share of the value that comes from the terminal value.

Use the same list as the minimum disclosure for any indicative valuation this skill produces. It is also why Step 10 asks for a statement of who prepared the valuation and on what basis: in a market without a licence, acceptance turns on exactly those disclosures.
