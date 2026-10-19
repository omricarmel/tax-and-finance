# Domain Coverage Checklist, israeli-utility-rates-comparator

Generated: 2026-07-06 via consumer-advisor coverage audit + rate fact-check on pua.gov.il, iec.co.il, water/gas authorities, kolzchut, Energy/Communications ministries.

## Must cover (core)

- [ ] Electricity: IEC tariff structure; standard vs 2-tier TOU choice; 18% VAT; semi-annual reset caveat; verify live at pua.gov.il. [covered]
- [ ] Electricity: private-supplier switching with the generation-component-only caveat + 14-day cooling-off. [covered]
- [ ] Electricity: bill discounts, all TWELVE IEC groups, the registered-consumer-name requirement (call 103), and that the discount carries over to a private supplier via Noga. [covered v1.5.0, supplier carry-over v1.6.0]
- [ ] Electricity: debt / הסדר תשלומים and any special status for medical-equipment households, as questions to ASK the supplier; terms not verified, never say the user cannot be disconnected. [covered, reworded v1.6.0; a primary Electricity Authority source is still wanted]
- [ ] Electricity: TOU-versus-flat decision including the higher TOU fixed charge (about 26 ILS per bi-monthly bill) and the transition-season peak sitting below the flat rate. [covered v1.6.0]
- [ ] Water: the +3.5 m3 a month allocation supplement for nursing benefit levels 3-6, IDF and security-forces disabled receiving a תגמול, and general disability at 70%+ medical; *6050 when missing from the list; no gain in a one-person home. [covered v1.6.0]
- [ ] Water: ascending block tariff, כמות מוכרת per registered nefesh, nefashot registration, confirmed-leak credit, municipal corporations; residential water is volumetric with NO fixed household charge. [covered v1.3.0]
- [ ] Cooking gas: balloon (no published national maximum; Energy Ministry locality comparator) vs central gas/צובר with supplier switching under חוק המקרקעין (החלפת ספק גז...) התשנ"א-1991, vs piped natural-gas connection. [covered, corrected v1.6.0]
- [ ] Cellular: MNO/MVNO, no-commitment plans, free fast number portability, retention price, promo-expiry escalation. [covered]
- [ ] Internet: infrastructure vs ISP layers, wholesale single-bill bundle, ADSL->fiber migration, router-rental drop, promo-expiry. [covered]
- [ ] Arnona: moving, change-of-holder notice to the municipality with proof, re-applying for discounts in a new municipality, moving IEC and water accounts and nefashot registration. [covered v1.6.0]
- [ ] Arnona: per-sqm/zone calc; 90-day hassaga -> ועדת ערר -> מנהלי escalation; discount catalogue INCLUDING נכס ריק / נכס לא ראוי לשימוש; single-discount rule. [covered v1.3.0]
- [ ] Official gov.il comparators + per-regulator complaint channels. [covered in references]

## Should cover (advanced / edge cases)

- [ ] Solar net-metering ROI GATED on roof ownership/control, with the apartment רכוש-משותף consent path and renter caveat. [covered v1.3.0]
- [ ] Solar export tariff, FULL table for systems up to 15 kW (and 15-30 kW) registered 12.3.2025-31.12.2026: default 48 fixed; accelerated payback 60 for 5 years then 39.00 fixed; real 38.7 CPI-linked; T30 37.31 for 2026 requests; +6 urban premium only in localities on the criterion 35מה annex list on the request-filing date (decisions 66406 and 70806); eligibility condition of no other facility at the site; settlement per kWh produced or exported. Source: tariff book July 2026 tables 5-6.7, 5-6.7א, 27-6.7 and Yalkut HaPirsumim 13738. [covered v1.6.0]
- [ ] Solar TEMPORAL dimension: the table above governs requests registered by 31.12.2026; the 2027+ regime is a draft (comments to 10.11.2026) and existing systems keep their terms. Re-check on every update until a final decision is published. [covered v1.6.0, re-check]
- [ ] Smart-meter adoption, self-paid expedited install, and monitoring tools. [covered]
- [ ] Prepaid electricity meters (מונה תשלום מראש) note for relevant housing. [to add next cycle]
- [ ] Water disconnection restrictions / municipal water-debt handling. [to add next cycle]
- [ ] Ombudsman / נציבות תלונות per utility and the consumer-protection authority. [covered in references]
- [ ] Provider-name accuracy + explicit freshness caveat. [covered v1.3.0, fixed Amerigas, Energean/Delek]

## Out of scope (explicit)

Re-litigated 2026-10-19: none of the rows below is something an ordinary household user of this skill would ask this skill to do, and none has become capturable; rationale unchanged.


- [ ] Commercial/business tariff optimization (skill is household).
- [ ] Upstream gas-field / wholesale power-market analysis.
- [ ] Solar installer/battery engineering and financial-product advice (dedicated solar skill).
- [ ] Va'ad bayit dispute mediation beyond the common-area-electricity note.
- [ ] Filing / representing legal claims (skill routes, does not litigate).

## Authoritative sources

- Electricity Authority (pua.gov.il), Israel Electric Corporation (iec.co.il).
- Water Authority + municipal water corporations; Natural Gas Authority / Energy Ministry.
- Ministry of Communications; kolzchut.org.il for discounts/rights.
- Consumer Protection Law + the Authority for Consumer Protection and Fair Trade.
