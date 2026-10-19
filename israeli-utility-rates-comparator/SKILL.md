---
name: israeli-utility-rates-comparator
description: Compare electricity providers, water tariffs, cooking-gas (LPG) rates, cellular plans, fiber internet packages, and arnona (municipal property tax) across Israeli municipalities and utility companies. Use when a user needs to understand IEC tariff structures, calculate solar panel ROI, compare tiered water pricing, pick a cheap cellular plan, switch to fiber internet, or evaluate arnona differences between cities. Covers electricity market deregulation, independent power producers, Mekorot water pricing, cellular operators and MVNOs, fiber-optic infrastructure, and municipal rate variations. Do NOT use for commercial/industrial utility contracts at scale, or utility infrastructure investment analysis.
license: MIT
allowed-tools: Bash(python:*) WebFetch
---

# Israeli Utility & Telecom Rates Comparator

## Instructions

### Step 1: Identify Which Utility to Compare

Establish which bill the user wants to move; the levers differ sharply. Electricity, water and
cooking gas are national or near-national and barely change with location, arnona changes with the
municipality, telecom with the provider. Ask for the last three bills, and where a household has
several, start with the largest line rather than the one they mentioned. Market-structure
background, including who owns which telecom brand, is in `references/details-2026.md`.

### Step 2: Electricity Comparison

**Understanding IEC tariff structure:**

The Electricity Authority sets the tariffs. A household is on the flat tariff (one rate for all
hours) or on **time-of-use** (תעו"ז), which needs a smart meter, has only two bands, peak and
off-peak, since the new clusters were first applied on 1.1.2023 (decision 63609), and has THREE
seasons, each with its own rates:

| Season | Peak band | Peak (agorot/kWh, incl. VAT) | Off-peak |
|---|---|---|---|
| Summer (Jun-Sep) | 17:00-23:00 | 172.23 (145.96 excl. VAT) | 50.42 |
| Winter (Dec-Feb) | 17:00-22:00 | 114.70 | 46.63 |
| Transition (Mar-May, Oct-Nov) | see note | 49.58 | 45.78 |

- In force from 1.7.2026, re-verified against the IEC low-voltage TOU page on 19 October 2026: all three seasons and both VAT bases still match, and no newer edition had been published.
- **Peak applies on different days per season, and this is where most of the money is.** In SUMMER and in TRANSITION there is NO peak band at all on Fridays, holiday eves, Shabbat or holidays: the whole day is off-peak. In WINTER the peak band applies on every day including Shabbat and holidays. There is no morning peak in any season.
- For TOU purposes these holidays count as Shabbat, and their eves as Friday: Rosh Hashana, Yom Kippur, the first day of Sukkot, Simchat Torah, the first and seventh days of Pesach, Independence Day and Shavuot. The hours are Israel local time and the metering equipment is adjusted when summer time is in force.
- Do not quote transition-season band hours: the IEC page states them in a garbled form ("22:00-17:00").
- **Is TOU worth it?** Compare the flat 63.52 with the household's blended TOU rate per season, then
  net off the fixed charges: on a bi-monthly single-phase connection TOU distribution is 37.88
  against 11.76 on the flat tariff, about 26 ILS more per bill. In transition even the TOU peak
  (49.58) is below the flat rate; summer turns on how much load sits in weekday 17:00-23:00. Never
  quote a flat percentage saving.

**Fixed charges, priced (from 1.7.2026, IEC residential tariff page).** These are what makes a
bill more than kWh times rate, and a total cannot be computed without them. Agorot for energy,
shekels for the rest.

| Component | Excl. VAT | Incl. VAT |
|---|---|---|
| Energy, per kWh (agorot) | 53.83 | 63.52 |
| Distribution, bi-monthly customer, single-phase meter (**the ordinary residential case**) | 9.97 | 11.76 |
| Distribution, bi-monthly customer, three-phase meter | 11.56 | 13.64 |
| Distribution, monthly customer | 157.31 | 185.63 |
| Supply, bi-monthly customer, single-phase meter | 15.60 | 18.41 |
| Supply, bi-monthly customer, three-phase meter | 15.53 | 18.33 |
| Supply, monthly customer | 107.70 | 127.09 |
| Capacity, per KVA per year | 6.18 | 7.29 |

Two fixed charges, distribution and supply, not one, and the amount depends on whether the
customer is billed monthly or bi-monthly and on whether the meter is single or three phase.
**Pick the row before quoting a total.** A normal apartment is a bi-monthly, single-phase
customer; the monthly rows are far larger per period (distribution about 16 times, supply about
7), so the wrong row can flip a supplier-switch or a TOU comparison.
On the TOU tariff the fixed charges differ again, all incl. VAT: distribution 174.50 monthly and
37.88 bi-monthly, supply 127.09 monthly and 18.33 bi-monthly.

**There is no broadcasting fee on an electricity bill**: the official page enumerates exactly
three fixed components, distribution, supply and capacity.

The residential tariff itself applies to homes used for residence only, places of worship and
buildings used for agriculture.

For apartments there is also a share of common-area electricity (chashmal klali) for
stairwells, lifts and lobby lighting. That is billed through the va'ad bayit and is not on the
IEC bill at all, which is what surprises new tenants.

**Independent electricity producers (residential market):**

The supply market is open: Calcalist reported about 279,500 customers (households and businesses)
moving to private suppliers during 2025 and more than 360,000 since the reform began in July 2024.
Active residential suppliers in 2026 include:
- **Cellcom Energy**, **Partner**, **Bezeq**, **HOT Energy** (telecom-bundled offers)
- **Pazgas Electricity**, **Amisragas**, **Electra Power** (energy and gas group offers)
- **OPC Energy**, **Dalia Energy**, **Enlight Renewable Energy** (independent generators, historically large-customer focused, also signing residential customers)

**Critical: switching does NOT replace the full bill.** Independent suppliers compete only on the **generation** (ייצור) component. The household continues to pay IEC the fixed distribution (חלוקה) and supply (אספקה) charges and the capacity charge, priced in the table above. The supplier discount applies only to the energy portion.

**Cancelling:** a contract made by phone or online is a remote sale, which Kol Zchut describes as
generally cancellable within 14 days under the Consumer Protection Law, and within 4 months for a
customer who is 65+, disabled or a new oleh where the sale involved a conversation with a representative.
Read the contract's own exit terms too.

**Switching supplier does not cost an entitled household its discount.** Kol Zchut states that
people entitled to the 50% discount keep receiving it through the private supplier: Noga receives
the list of entitled people every month and passes a credit to the supplier, which passes it on.
An entitled customer who stops seeing it after switching should contact the supplier. The 50% can
also be combined with the supplier's own general discount tracks.

**Discounts on the electricity bill (separate from supplier choice). TWELVE groups qualify, not
three**, per IEC's own entitlement page. Ask which applies before assuming none does:

1. Income-support benefit under s.2(a)(4) of the Income Support Law: per Bituach Leumi, a person
   above retirement age with an old-age or survivors' pension PLUS income supplement
2. Nazi-persecution and war-disabled compensation, and Holocaust survivors on income-tested
   compensation
3. Old-age pension for the disabled under s.251 of the National Insurance Law
4. Special-services allowance at 112% or more
5. Disabled-child allowance where the child depends on another person's help or needs special
   medical treatment (other disabled-child grounds do NOT qualify)
6. Nursing (סיעוד) allowance at level 5 or 6
7. A lone soldier in regular service, or a soldier entitled to rent assistance because of the
   distance between home and posting
8. A single parent (הורה עצמאי) with three or more children receiving income support, income
   supplement or alimony
9. A family with four or more children receiving income support, income supplement or alimony
10. IDF disabled at 50% or more, or below 50% with a permanent maintenance grant
11. Hostile-action casualties on the same terms
12. Special-services allowance at 50%

Per Kol Zchut the rate is 50% on up to 400 kWh/month (800 on a bi-monthly bill), on a residential
tariff in the home where the entitled person lives; a reported plan to deepen it to 65% for three
groups had not reached Kol Zchut by 19 October 2026, so quote 50%.

**The entitlement fails silently if the contract is in the wrong name.** The awarding body
(Bituach Leumi, the Holocaust Survivors' Rights Authority, the IDF or the Defence Ministry
depending on group) notifies the person and passes their details to IEC, but the discount only
lands if that person is the registered IEC consumer under their own name and ID number. Anyone in
one of the twelve groups who does not see a reduced payment on the bill should call IEC on 103 to
have the registration corrected. Tell users this: it is the most common reason a real entitlement
produces no money.

**Debt and disconnection (raise it with any user whose bill is unaffordable).** Ask the supplier
whether a הסדר תשלומים is available for arrears, and about any special status for a household
dependent on electrically powered medical equipment. The terms are set by the Electricity Authority
and are **not verified here**: never tell the user they cannot be disconnected. Background in `references/details-2026.md`.

### Step 3: Calculate Solar Panel ROI

**The export tariff is published, and it depends on the track and the registration date.** The
Electricity Authority tariff book published July 2026 carries it, so earlier versions of this skill
were wrong to withdraw it. For a rooftop system whose connection request was **registered**
(through the installer; not the connection date) between 12.3.2025 and 31.12.2026, in agorot per kWh:

| Track (tariff-book table) | Size cap | Tariff | Indexation |
|---|---|---|---|
| Default (5-6.7) | 630 kW | 48 up to 15 kW; 15-100 kW at T100, 37.31 for 2026 requests | fixed |
| Accelerated payback (5-6.7א, decision 71004) | 30 kW | up to 15 kW: 60 for five years after grid sync, then 39.00 | fixed |
| Real (5-6.7א) | 15 kW | 38.7 base | CPI-linked, updated every 1 January |
| Urban premium (27-6.7, decision 66406) | listed localities | +6 on top of the track | not linked |

- On the accelerated track a 15-30 kW system pays its first 15 kW at 60 and then 38.07, and the
  rest at T30, 37.31 for 2026 requests.
- The two optional tracks are open only when no other generating facility under the same
  arrangement is already connected at the site.
- **Urban premium** (earlier versions wrongly called it unsourced): the locality must be on the
  list annexed to criterion 35מה **on the date the connection request is filed**. The list covers
  localities with more than 50,000 residents (CBS) or a planned population above 50,000, or a
  qualifying outline plan, and is updated only after the Authority receives proof (decision 70806).
- **Choose the track by arithmetic, over the term in the contract.** Assuming 25 years (Globes
  reports that term for existing systems; the tariff tables read here do not state it): the
  default 48 pays more in total than the accelerated track on any term longer than about 11.7
  years, and the accelerated track only wins on present value at a discount rate above about
  10.5%, i.e. a financed system or an early sale. The real track beats the default in total if
  average inflation exceeds about 1.75% a year, and is the only inflation-protected track.
- **2027 onward is a draft, not law.** As of 19 October 2026 the Authority has a draft out for
  public comment until 10 November 2026. As reported by Globes, it cuts the up-to-15-kW tariff by
  5% a year from 2027 to 2030, to about 35.5 agorot in 2030 subject to the dollar rate, shortens
  the guarantee period, and leaves existing systems on their current terms.

The rest of the calculation:

1. **Roof**: south-facing, unshaded, structurally sound, and confirm the applicant controls it (a
   shared roof needs the building's agreement; a tenant generally cannot install alone).
2. **Annual production**: roughly 1,500-1,800 kWh per installed kWp, Negev at the top of that
   range, the north at the bottom, the centre between.
3. **Settlement method**: the tariff book pays the track rate per kWh produced OR per kWh exported,
   according to the method the consumer chooses. A self-consumed kWh is worth the household's own
   rate in solar hours: 63.52 on the flat tariff, but only the off-peak 45.78-50.42 on TOU, and
   less again with a supplier discount. Compare that with the track rate before choosing.
4. **Payback**: system cost divided by the annual value under that method, plus the premium where
   eligible. Get three quotes; this skill carries no verified installation price.

### Step 4: Water Tariff Comparison

Water is priced in two tiers by the Water Authority, nationally, so unlike arnona it barely moves
between cities.

**The Tier-1 allocation has TWO limbs and the second is the one people miss.** The rule is up to
3.5 m3 per registered person per month, **and not less than 7 m3 per housing unit**. The floor
matters most to exactly the households least likely to know it: a one- or two-person home is
entitled to 7 m3 at the low rate regardless of headcount. Saying only "3.5 per person" under-claims
their allocation and prices the difference at the high rate.

- Tier 1 (low rate): 8.51 ILS/m3 incl. VAT, from 1 January 2026 (still the latest update on the
  Water Authority page as of 19 October 2026)
- Tier 2 (everything above the allocation): 15.62 ILS/m3 incl. VAT

**Register every nefesh with the water corporation.** The allocation is per REGISTERED person and
registration is not retroactive beyond its date, so an unregistered household member is the single
most common cause of a bill that looks too high. Note also that since 1.5.2015 the development
levies (היטלי פיתוח) were replaced by כללי דמי הקמה, so do not tell a user to compare an
"infrastructure development levy" under the old name.

**Some household members get a bigger allocation.** Per Kol Zchut, three groups get an extra 3.5 m3
a month at the low rate (7 m3 for that person, 14 per bi-monthly bill): גמלת סיעוד at level 3-6;
IDF and security-forces disabled at 50%+ receiving a תגמול, or below 50% with a תגמול קיום קבוע;
and general-disability recipients with at least 70% medical disability. One supplement per person
even if two benefits qualify. The list reaches the water supplier automatically; ask the supplier
whether the person is on it. If not: Bituach Leumi on *6050 for nursing and general disability,
the Defence Ministry rehabilitation division (אגף שיקום נכים) for IDF disabled.

Corporation names and the shared-meter case are in `references/details-2026.md`.

### Step 5: Natural Gas and Cooking Gas Comparison

**Cooking gas balloons (balonei gaz):**
- Standard 12 kg balloon
- **Not a published national maximum.** The Energy Ministry surface this skill links is a
  comparison calculator (מחשבון השוואת מחירי גז בישול) that asks for the user's LOCALITY and
  connection type and sits beside the ministry's own guides to switching a private or commercial
  gas supplier. Prices differ by supplier and by place, which is why a comparison-and-switching
  tool exists. Earlier versions of this skill told users to wait for a monthly published maximum,
  which pointed them away from the one lever that moves this bill.
- **This skill carries no LPG price anchor.** It has none for the balloon, none per kg, none for
  delivery and none for central gas. Send the user to the ministry calculator for their own
  locality rather than quoting a figure from here.
- Delivery fee varies by supplier
- Israeli LPG suppliers: Supergas, Pazgas, Amisragas, Dorgas
- Typical household uses 1 balloon every 1-3 months

**Natural gas (gaz tiv'i) home connection:**
- Available in newer residential buildings connected to the national gas grid
- Significantly cheaper per unit of energy than cooking gas balloons
- Monthly fixed connection fee plus usage-based charges
- Supply operator: Energean Israel (Karish/Tanin field), a separate company from NewMed Energy (formerly Delek Drilling, Tamar/Leviathan); local distribution companies handle last-mile delivery

**Central gas (גז מרכזי / צובר), a large apartment segment, has a real lever:** switching the supplier of a building's central gas system is governed by חוק המקרקעין (החלפת ספק גז המספק גז באמצעות מערכת גז מרכזית), התשנ"א-1991, and the Fuel Administration can fine a supplier that breaches it. For these households, switching or renegotiating the supplier is the main way to lower cooking-gas cost.

### Step 6: Cellular and Internet Comparison

Telecom prices fell sharply after MVNO entry from 2012 and the fiber rollout. Compare the **total** bill (line + roaming + add-ons) and the price after any introductory period, not the headline line price.

Key points:
- On israeliphoneplans' cheapest-plans table on 19 October 2026, single-line plans with 150GB+ and thousands of minutes started at about 26 NIS/month (019 Mobile 170GB at 25.90, Rami Levy 250GB at 26.90), with Golan's 300GB and unlimited minutes at 34.90; some lower prices there are per-line family prices. Prices move monthly, so quote the live comparator, not this line. Number portability is free and takes ~1 business day, sign with the NEW provider first (never cancel first, that creates a gap). eSIM is widely supported.
- Home internet splits into infrastructure (Bezeq BFiber, HOT, IBC/Unlimited, Cellcom/Partner fiber) and ISP; most households now buy one wholesale-market bundle, so price a legacy split bill against it. Fiber coverage is high and ADSL is being retired; the '>90% of households' figure this skill used to state is **unverified** and should not be quoted.
- Introductory prices commonly jump after 12 months; set a reminder and re-shop. Triple-play (cellular+internet+TV) discounts vanish if you cancel one leg.
- **Check who owns the brand before calling it an alternative.** Golan Telecom's own About page states that it formerly held its own mobile licence, that since 24.12.2023 Golan Telecom services are provided on the licence of Cellcom Israel Ltd, and that the activity of Golan International was transferred to Cellcom Fixed-Line Communications. A Cellcom customer moving to Golan has therefore not moved to a different licensee. Brand names in this market outlive the independent companies behind them; verify ownership before presenting two brands as rival options.

**How to comparison-shop:**
1. **Pull last 3 months of bills** for cellular, internet, TV to see actual usage (data per line, peak speed observed, TV channels you watch)
2. **Run an Israeli comparator**: kamaze.co.il, kamazeole.co.il, israeliphoneplans.com or mishtalemli.co.il (all four opened with live plan listings on 19 October 2026)
3. **Get 2-3 quotes** by phone; tell each company you're shopping and ask for "מחיר שמירת לקוח" (retention price)
4. **Time the switch**: cellular portability is free; internet may have a 1-2 week overlap so schedule installation before cancellation

### Step 7: Arnona Comparison Between Cities

Arnona is the largest recurring utility-like cost for an Israeli household and the only one that
changes materially between municipalities.

**Who pays it: the מחזיק, the occupier.** In a rented flat that is the TENANT, not the landlord.
This is the first thing to establish in any relocation or cost-comparison question and it is the
fact most often assumed the other way round.

**How it is charged:** a rate per square metre per YEAR, per zone within the municipality, and
different for residential and commercial. Divide by 6 for a bi-monthly bill or 12 for a monthly
one; treating the annual rate as monthly overstates the bill twelvefold. To find the rate, the
municipality's own site under arnona or tashlumim carries the tariff table per zone.

**Discounts** exist for olim, seniors, low income, disability, IDF and national service and
bereaved families, students, single-person households, and empty or uninhabitable property, each
with its own eligibility test and time limit. Two rules matter more than the list: **only one
discount applies per property at a time** (תקנות הסדרים במשק המדינה (הנחה מארנונה), תשנ"ג-1993), so
a household qualifying on two grounds gets the larger and not the sum; and a discount is granted
**on application**, so it does not arrive by itself. Never quote a percentage without checking the
municipality, since national regulations set ceilings that municipalities apply differently.

**Objection (השגה):** if the bill is wrong (size, zone, a missing discount, a balcony at full
rate), file a written hassagah with the municipal arnona manager within **90 days** of the bill.
The municipality must answer within **60 days** and silence counts as rejection. If rejected,
**30 days** to appeal to the ועדת ערר לארנונה, and **45 days** from its ruling to the בית משפט
לעניינים מנהליים. **These deadlines have not been independently verified in this skill and a wrong
one forfeits a legal right**: confirm them against the municipality's own notice, which must state
them, before relying on a date.

**Moving:** notify the municipality of the change of holder on its form and keep proof; Tel Aviv
states that if the previous holder left and no new holder was notified, the owner is registered
automatically. Apply for discounts again in a new municipality, and move the IEC and water accounts
(and the water nefashot registration) to the new occupier's name and ID.

### Step 8: Tips for Reducing Utility Bills

Highest-leverage actions: shift electricity to off-peak on a TOU tariff, register all nefashot for the water Tier-1 allocation and fix leaks fast, apply for every arnona discount and verify recorded property size, and compare cellular/internet against MVNOs / wholesale bundles while asking for a "מחיר שמירת לקוח" retention price.

### Step 9: Smart Meter Adoption and Monitoring

A smart meter (מונה חכם) is a prerequisite for the TOU tariff and is what makes any load-shifting
advice actionable, because without interval data there is nothing to shift against. IEC installs
them on request and on a national rollout. The consumption data is what turns the seasonal peak
and off-peak figures in Step 2 into a number for this household rather than a national average.
Adoption details and the rollout position are in `references/details-2026.md`.

## Examples

### Example 1: Family Evaluating Solar Panels

User says: "We pay about 800 ILS a month for electricity. Is solar worth it?"

Convert the bill to kWh at the retail rate (63.52 agorot incl. VAT), size the system from annual
consumption divided by the kWh-per-kWp band for their region, and confirm they control the roof.
Value the output under the settlement method in the quote, at the track they would choose from
the Step 3 table, adding the urban premium only if their locality is on the list.
Compare all three tracks over the term stated in the contract, tell them the
current table covers requests registered by 31.12.2026 while 2027 terms are still a draft, and send
them for three installation quotes.

### Example 2: Comparing Utility Costs Between Cities for Relocation

User says: "Should I move from Tel Aviv to Haifa? How much will I save on utilities?"

Electricity, water and cooking gas are national or near-national, so they barely move with the
city. Arnona does, and it is the only line that materially changes. Work it from the user's own
apartment size in square metres, the specific rate zone of each address from each municipality's
own tariff table, and the discounts they personally qualify for. Give the annual arnona delta, say
plainly that the rest of the utility bill is substantially the same in both cities, and give the
moving checklist from Step 7.

### Example 3: Optimizing Electricity Bill with Smart Meter

User says: "I have a smart meter. How do I lower my bill?"

Pull the interval data, find how much consumption already sits in the peak band, and price the
shift using the SEASONAL figures from Step 2 rather than a flat percentage: moving a load off
peak is worth over 120 agorot/kWh in summer and under 4 in the transition season, and in summer
and transition there is no peak band at all on Fridays, Shabbat and holidays, so weekend loads
are already off-peak. Then check whether TOU beats the flat tariff at all, using the Step 2
comparison including the higher TOU fixed charge. Only after
that is the supplier-discount question worth raising, and it touches the generation component
only, not the fixed charges.

## Gotchas
- Israel Electric Corporation rates are updated by the Electricity Authority on a semi-annual cycle, and a mid-year update can move the rate: the 1.7.2026 update moved the residential rate to 53.83 agorot excluding VAT and 63.52 including, down from the January 2026 edition. Agents routinely quote a superseded rate. Always verify the current tariff before quoting per-kWh numbers.
- The TOU schedule has had only two bands (peak and off-peak) since 1.1.2023; agents trained on older docs still describe a three-tier structure with a shoulder band.
- Switching to an alternate electricity supplier (Cellcom Energy, Pazgas, OPC, etc.) only discounts the generation component. The household still pays the fixed distribution and supply charges and the capacity charge priced in Step 2. Agents may incorrectly imply the entire bill changes.
- Water Tier 1 covers up to 3.5 m³ per registered nefesh per month at the lower rate, with a floor: the recognized quantity per housing unit is never less than 7 m³ per month, so a single-occupant household gets 7 rather than 3.5; consumption above goes to Tier 2 (~84% higher in Jan 2026: 8.51 vs 15.62 ILS/m³ inc. VAT). Sewage is bundled into the regulated per-m³ tariff in most municipalities, NOT a separate percentage surcharge as some older guides describe.
- Israeli utility bills include 18% VAT (raised from 17% on 1 Jan 2025). A rise to 19% was floated at the Finance Ministry but was not enacted: the 2026 state budget contains no such increase, so quote 18%. Be explicit about whether quoted prices include or exclude VAT, especially when comparing alternate-supplier offers, since some advertise the pre-VAT generation rate.
- The Olim Hadashim arnona discount is 90% on up to 100 sqm for 12 months out of the 24 months following aliyah registration, NOT yearly. Agents may incorrectly describe it as multi-year (e.g., "90% first year, 10% years 2-5"). Olim receiving a nursing benefit or a disability allowance for dependence on others get up to 80% on the whole flat (Kol Zchut).
- The IEC customer-service number is **103**; calls from a Bezeq or HOT landline are free. Do not emit older short codes from memory, they may point at a dead number.
- Agents trained before mid-2025 know only the flat 48-agorot export rate, and the previous version of this skill wrongly called the urban premium unsourced. The current regime has three tracks plus a +6 urban premium for listed localities (Step 3), and 2027 terms are a draft open to comment until 10.11.2026. Never quote the draft as adopted.
- Introductory telecom prices expire, commonly after 12 months; quote the price after the promotion, and always sign with the NEW provider first when porting.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Electricity tariff book, July 2026 (official PDF) | https://www.gov.il/BlobFolder/generalpage/tarriffbook/he/sefer_tariff_07_2026.pdf | All tariff tables, incl. solar tracks 5-6.7 / 5-6.7א and urban premium 27-6.7. Check for a newer edition |
| Israel Electric Corporation | https://www.iec.co.il | Residential tariff plans, smart meter rollout, consumption monitoring |
| IEC TOU low-voltage tariffs | https://www.iec.co.il/content/tariffs/contentpages/taozb-namuch | Per-season peak/off-peak rates and band hours, with the effective date |
| Electricity Authority | https://www.gov.il/he/departments/the_electricity_authority | Regulator decisions and tariff-update announcements (pua.gov.il redirects here) |
| Water Authority | https://www.gov.il/he/departments/water_authority | Tiered water rates, household allocation, municipal corporations |
| Water tariff book (Jan 2026) | https://www.gov.il/he/pages/rates_general1 | Full water + sewage tariff tables and updates |
| Natural Gas Authority | https://www.gov.il/he/departments/natural_gas_authority | Consumer gas pricing, supplier list, connection rules |
| LPG cooking gas comparator (Energy Ministry) | https://migdal-webpages.energy-apps.org/gpmCalculator | Compare LPG cooking-gas tariffs by locality and supplier |
| Ministry of Communications | https://www.gov.il/he/departments/ministry_of_communications | Cellular and internet regulation, complaints, supplier list |
| Kolzchut, senior electricity discount | https://www.kolzchut.org.il/he/הנחה_בחשבון_חשמל_למקבלי_קצבת_זיקנה_עם_השלמת_הכנסה | 50% up to 400 kWh/month, and how it carries over to a private supplier |
| Kolzchut, olim arnona discount | https://www.kolzchut.org.il/he/הנחה_בארנונה_לעולים_חדשים | Exact eligibility window (12 months out of 24), 100 sqm cap, special-needs olim rules |
| Kolzchut, senior arnona discount | https://www.kolzchut.org.il/he/הנחה_בארנונה_לאזרחים_ותיקים | Senior age threshold (men 67; women at the rising retirement age, do NOT assume a flat 62), income tests, discount tiers |

## Bundled Resources

- `references/details-2026.md`: electricity, water, LPG, telecom and arnona detail with dates and sources.
- `references/domain-checklist.md`: coverage contract with sources.

## Recommended MCP Servers

| MCP | What It Adds |
|-----|-------------|
| [Israeli CBS MCP](https://agentskills.co.il/he/mcp/israeli-cbs) | CPI and price-index series, useful for checking whether a tariff change tracks inflation or exceeds it |
| [Kolzchut (All-Rights)](https://agentskills.co.il/he/mcp/kolzchut) | Live text of the arnona, electricity and water discount entitlements this skill routes to |

Utility tariffs move on published schedules. Confirm any rate's effective date before quoting it.

## Troubleshooting

### Error: "My electricity bill seems much higher than expected for my consumption level"

Cause: most often a bill based on an estimate (הערכה) rather than an actual meter reading, an
electric water heater (dud) running in peak hours, or air conditioning working harder than it
should. Common-area electricity is NOT the cause: it is billed through the va'ad bayit, not IEC.

Solution: check whether the bill shows an actual reading or an estimate and, if estimated, ask
IEC for a real reading and compare it with the physical meter. Then look for the water heater on
a timer outside peak hours, dirty AC filters, an old refrigerator and standby loads, and use the
IEC app or smart-meter data to find the spikes.

### Error: "Water bill shows consumption much higher than our household uses"

Cause: an unregistered household member or a missing allocation supplement (Step 4) (so the Tier-1
allocation is too small), a leak between
the municipal meter and the apartment, or a shared-meter building where one bill is split by
apartment count rather than by actual use.

Solution: first register every nefesh with the water corporation, since Tier 1 is allocated per
registered person and the allocation is retroactive only from the registration date. Then check
for a leak by closing every tap and watching the meter. A leak repaired promptly can qualify for
a partial credit; ask the corporation for its conditions, which this skill does not verify.
