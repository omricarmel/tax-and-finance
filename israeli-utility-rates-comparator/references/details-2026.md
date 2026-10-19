# Israeli Utility & Telecom Details (2026)

Detail behind SKILL.md. Rewritten and deduplicated on 19 October 2026: earlier versions carried
several moved copies of the same sections, and the copies drifted apart, so a figure withdrawn in
one copy survived in another. Every figure below is either backed by `evidence.json` or labelled as
unverified. Tariffs move on published schedules (electricity semi-annually, water usually in
January, arnona every January, telecom continuously): verify the effective date before quoting.

## Electricity

### Tariff snapshot (in force from 1.7.2026, re-verified 19.10.2026)

- Flat residential tariff: 53.83 agorot per kWh excl. VAT, 63.52 incl. 18% VAT. The January 2026
  edition is superseded. Source: IEC residential tariff page.
- TOU (תעו"ז), incl. VAT, agorot per kWh. Summer (Jun-Sep): peak 17:00-23:00 at 172.23 (145.96
  excl.), off-peak 50.42. Winter (Dec-Feb): peak 17:00-22:00 at 114.70, off-peak 46.63. Transition
  (Mar-May, Oct-Nov): peak 49.58, off-peak 45.78. Source: IEC low-voltage TOU page.
- Peak days: in summer and transition there is no peak band on Fridays, holiday eves, Shabbat or
  holidays; in winter the peak band applies every day. Holidays treated as Shabbat: Rosh Hashana,
  Yom Kippur, first day of Sukkot, Simchat Torah, first and seventh days of Pesach, Independence
  Day, Shavuot; their eves count as Friday. Hours are Israel local time.
- TOU has used only peak and off-peak clusters since the new clusters were first applied on
  1.1.2023 (decision 63609 of 27.7.2022, tariff book table 1-5.1).
- Fixed charges on the flat tariff (ILS, excl./incl. VAT): distribution 9.97/11.76 bi-monthly
  single-phase, 11.56/13.64 bi-monthly three-phase, 157.31/185.63 monthly; supply 15.60/18.41
  bi-monthly single-phase, 15.53/18.33 bi-monthly three-phase, 107.70/127.09 monthly; capacity
  6.18/7.29 per KVA per year. On TOU: distribution 147.88/174.50 monthly and 32.10/37.88 bi-monthly;
  supply 107.70/127.09 monthly and 15.53/18.33 bi-monthly.
- No broadcasting fee: the official page enumerates distribution, supply and capacity only.
- Common-area electricity (חשמל כללי) is billed through the va'ad bayit, not on the IEC bill.

### Is TOU worth it? The comparison to run

Compare the flat 63.52 against the household's own blended TOU rate in each season, then net off
the fixed-charge difference. On a bi-monthly single-phase connection the TOU distribution charge is
37.88 against 11.76 on the flat tariff, and supply is 18.33 against 18.41, so TOU costs about 26 ILS
more per bi-monthly bill in fixed charges (derived from the two IEC pages). In the transition
season even the TOU peak rate (49.58) is below the flat rate, so every kWh is cheaper; in summer the
answer depends on how much load sits in 17:00-23:00 on weekdays. Never quote a flat percentage
saving.

### Private suppliers

- The residential supply market is open. Calcalist (January 2026) reported about 279,500 customers
  moving from IEC to private suppliers during 2025, at tariffs 7% to 20% cheaper, and more than
  360,000 consumers since the reform began in July 2024. The 279,500 covers households and
  businesses together.
- Suppliers compete on the generation component only. The household still pays the fixed
  distribution and supply charges and the capacity charge.
- A contract made by phone or online is a remote sale, which Kol Zchut describes as generally
  cancellable within 14 days under the Consumer Protection Law, and within 4 months for a customer who is 65+,
  disabled or a new oleh where the sale involved a conversation with a representative; read the
  contract's own exit terms as well.
- The 50% discount survives a switch: Noga passes the monthly list of entitled people and a credit
  to the supplier, and the discount combines with the supplier's own general tracks (Kol Zchut).

### Discounts on the bill (twelve groups, per IEC's entitlement page)

The groups are listed in SKILL.md Step 2. The rate, per Kol Zchut, is 50% on up to 400 kWh a month
(800 on a bi-monthly bill), on a residential tariff, in the home where the entitled person lives.
The IEC entitlement page lists the groups and the registration rule but not the percentage. A
reported plan to deepen the discount to 65% for three groups had not reached Kol Zchut by
19.10.2026. The discount lands only if the entitled person is the registered IEC consumer under
their own name and ID; if it is missing, call IEC on 103.

### Debt and disconnection

Ask the supplier whether a payment arrangement (הסדר תשלומים) is available, and ask about any
special status for a household that depends on electrically powered medical equipment. The terms
are set by the Electricity Authority and are **not verified in this skill**: never tell a user
they cannot be disconnected.

### Smart meters

IEC passed one million smart meters in August 2024, about 30% of all meters at that point, with a
target of 3.7 million by end-2028 (Calcalist). Treat the million as a dated milestone, not a current
count. A smart meter is required for TOU. Ask IEC (103 or the IEC app) about installation and any
fee; this skill carries no verified installation fee and no verified content on prepaid meters.

## Solar export tariff and ROI

Sources: Electricity Authority tariff book published July 2026, tables 5-6.7, 5-6.7א and 27-6.7;
Electricity Market Rules (Tariffs) Amendment 19, 2025, Yalkut HaPirsumim 13738 of 13.8.2025
(decision 71004); decision 70806 of 24.3.2025 on the urban-premium locality list.

- **Roof first**: only someone who controls the roof or connection point can install. An apartment
  needs the building owners' consent; a tenant generally cannot install alone.
- **Requests registered 12.3.2025 to 31.12.2026** (the date the connection request is registered,
  which the installer files, not the connection date). Agorot per kWh:

| Track | Size cap | Rate |
|---|---|---|
| Default (5-6.7) | up to 630 kW | 48 for systems up to 15 kW; above 15 and up to 100 kW, T100 is 37.31 for 2026 requests (39.36 for 2025); fixed, not CPI-linked |
| Accelerated payback (5-6.7א) | up to 30 kW | up to 15 kW: 60 in years 1-5 after grid sync, then 39.00; a 15-30 kW system pays its first 15 kW at 60 then 38.07, and the rest at T30, 37.31 for 2026 requests; fixed, not CPI-linked |
| Real (5-6.7א) | up to 15 kW | 38.7 base, CPI-linked, updated every 1 January; the first update is measured against the November CPI of the year before operation |
| Urban premium (27-6.7) | listed localities | +6 on top of the track |

- The two optional tracks are open only when no other generating facility under the same
  arrangement is already connected at the site.
- **Urban premium list**: the annex to criterion 35מה lists localities meeting one of three tests:
  an approved comprehensive outline plan classifying the locality as model 1-2-3 under TAMA 35
  amendment 4; approved detailed plans showing a planned population above 50,000; or more than
  50,000 residents in the CBS annual update. Eligibility requires the locality to be on the list
  on the date the connection request is filed, and the list is updated only after the Authority
  receives proof, not proactively (decision 70806).
- **Settlement method**: the tariff is paid per kWh produced or per kWh exported, according to the
  method the consumer chooses. The value of a self-consumed kWh is the household's own marginal
  rate in solar hours: 63.52 on the flat tariff, the off-peak 45.78-50.42 on TOU (daytime falls in
  the off-peak band), and less again with a supplier discount. Compare that rate against the track
  rate before recommending a method.
- **Track arithmetic** (derived, undiscounted unless stated, up to 15 kW):
  - Accelerated against default: 5 x 60 + 39 x (T - 5) = 48 x T at T of about 11.7 years. On a
    longer term the default pays more in total. Over 25 years the accelerated track has the higher
    present value only at a discount rate above about 10.5%, so it suits a financed system or a
    household expecting to sell or remove the system within about 12 years.
  - Real against default over 25 years: the real track pays more in total if average CPI
    inflation exceeds about 1.75% a year (38.7 indexed at 2% totals about 1,240 against 1,200 for
    the default). It is the only inflation-protected track.
  - These assume a 25-year term, which Globes reports for existing systems; the tariff-book tables
    read here do not state the length. Confirm it in the contract.
- **2027 onward is a draft.** As of 19.10.2026 the Authority's draft is open for comment until
  10.11.2026 (Bizportal). Globes reports a 5% annual cut for up-to-15-kW roofs from 2027 to 2030,
  to about 35.5 agorot in 2030 subject to the dollar rate, a shorter guarantee period, and
  existing systems keeping their terms. Never present it as adopted.
- Annual production: roughly 1,500-1,800 kWh per kWp, Negev at the top, north at the bottom.
  No installation price is verified here; get three quotes.

## Water

- Two tiers, set nationally, incl. VAT and sewage: Tier 1 8.51 ILS/m3, Tier 2 15.62 ILS/m3, from
  1.1.2026; as of 19.10.2026 that is still the latest update on the Water Authority tariff page.
- Tier-1 allocation: up to 3.5 m3 per registered person per month, and not less than 7 m3 per
  housing unit.
- **Allocation supplement**: per Kol Zchut, three groups get an extra 3.5 m3 a month at the low
  rate, so 7 m3 a month, 14 per bi-monthly bill, for that person: nursing benefit (גמלת סיעוד) at
  level 3, 4, 5 or 6 (or level ב' or ג' under the old law); IDF and security-forces disabled at 50%
  or more receiving a תגמול, or below 50% receiving a תגמול קיום קבוע; general-disability recipients
  with at least 70% medical disability. A person entitled under several benefits gets one
  supplement. The list goes monthly to the Water Authority and on to the local supplier; ask the
  supplier whether the person is listed. If not: Bituach Leumi on *6050 for the nursing and
  general-disability groups, the Defence Ministry rehabilitation division (אגף שיקום נכים) for IDF
  disabled. How the supplement combines with the 7 m3 per-unit floor in a one-person home is not
  stated in the sources read here; ask the supplier.
- Register every household member with the water corporation; registration is not retroactive.
- Residential water is volumetric: there is no fixed household water service charge. Since
  1.5.2015 development levies were replaced by כללי דמי הקמה.
- Leaks: a repaired hidden leak may qualify for a partial credit from the water corporation. The
  percentage and any filing deadline are **not verified here**; ask the corporation and keep the
  plumber's invoice.
- Corporations: Mei Avivim (Tel Aviv), Hagihon (Jerusalem), Mei Haifa, Mei Raanana; Mekorot
  supplies some localities directly.

## Cooking gas and natural gas

- LPG 12 kg balloons: no published national maximum. The Energy Ministry runs a comparison
  calculator by locality and connection type, beside its supplier-switching guides. This skill
  carries no LPG price. Suppliers: Supergas, Pazgas, Amisragas, Dorgas.
- Central gas (צובר): switching the supplier of a building's central gas system is governed by
  חוק המקרקעין (החלפת ספק גז המספק גז באמצעות מערכת גז מרכזית), התשנ"א-1991, and the head of the
  Fuel Administration may impose a financial sanction on a supplier that breaches it (Energy
  Ministry gas-suppliers page). Switching or renegotiating is the main lever for these households.
- Natural gas: newer buildings on the grid; a monthly fixed charge plus usage. Supply: Energean
  Israel (Karish/Tanin), separate from NewMed Energy (formerly Delek Drilling, Tamar/Leviathan).
  No verified price or saving percentage is carried here; get a connection quote and compare it
  with the household's own balloon spend.

## Telecom

- Cellular: on israeliphoneplans' cheapest-plans table on 19.10.2026, single-line plans with 150GB
  or more and thousands of minutes started at about 26 ILS a month (019 Mobile 170GB with 5,000
  minutes at 25.90; Rami Levy 250GB with 4,000 minutes at 26.90), and Golan's 300GB with unlimited
  minutes was 34.90. Some lower prices on that table are per-line family or couple prices, and
  cheaper plans are data-only, kosher or low-data. Prices move monthly: use the live comparators
  (kamaze.co.il, kamazeole.co.il, israeliphoneplans.com, mishtalemli.co.il).
- Rami Levy Mobile runs on the Hot Mobile network. Golan Telecom has run on Cellcom Israel's
  licence since 24.12.2023. We4G now trades as wecom (we-com.co.il).
- Portability is free; sign with the new provider first and let it move the number. Check the price
  after the introductory period.
- Home internet: infrastructure (Bezeq BFiber, HOT, IBC/Unlimited, Cellcom and Partner fiber) and
  ISP layers; most households buy one wholesale bundle. No verified price table is carried here;
  use the comparators.

## Arnona

- The occupier (מחזיק) pays, so in a rented flat the tenant does.
- Rate per m2 per year, per zone, from the municipality's annual order; divide by 6 or 12. No
  city-by-city figures are carried here: an unsourced table in earlier versions was removed on
  19.10.2026. Use the municipality's own tariff table.
- **Moving**: notify the municipality of the change of holder on its form and keep proof. Tel Aviv,
  for example, takes an online change-of-holder request or a declaration form and a separate exit
  form for a departing tenant, states that where the previous holder left and no new holder was
  notified the owner is registered automatically, and lets a resident ask to move an existing
  discount or standing order to the new property. Apply for discounts again in a new municipality.
  Transfer the IEC and water accounts to the new occupier's name and ID at the same time.
- Discounts: olim up to 90% on 100 m2 for 12 of the 24 months after registration; olim receiving a
  nursing benefit or a disability allowance for dependence on others up to 80% on the whole flat
  (Kol Zchut). Seniors: men 67, women at the rising retirement age; income tests apply. Others
  (low income, disability, IDF and bereaved families, students, single-person, empty or
  uninhabitable property) depend on the municipality. Only one discount applies per property at a
  time (תקנות הסדרים במשק המדינה (הנחה מארנונה), תשנ"ג-1993), and each is granted on application.
- Objection ladder (90 days to object, 60 for the reply, 30 to appeal to ועדת ערר, 45 to the
  administrative court): **not independently verified**; confirm against the municipality's
  notice, which must state the deadlines.

## Escalation

- Each regulator's public-complaints unit (Electricity Authority, Water Authority, Energy Ministry
  for gas, Ministry of Communications) and the Consumer Protection and Fair Trade Authority.
- Small claims court for utility billing disputes (not arnona): the ceiling is not re-verified in
  this skill; check the courts' site.

## Troubleshooting

- High electricity bill: check actual reading versus estimate, the physical meter, the water heater
  timer, AC filters, an old refrigerator and standby loads; use the IEC app or smart-meter data.
- High water bill: an unregistered household member, a missing allocation supplement (see Water), a leak
  (close every tap and watch the meter; dye in the toilet tank shows a running toilet), or a shared
  meter split by apartment count.
