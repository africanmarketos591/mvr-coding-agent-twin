# BUILD CHARTER - SMS Crop Price Alerts (c01)
**Date:** 2026-07-10 | **Archetype:** agritech_aggregator | **Market:** KE
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 4c6dda1c1aa2ad756ad636cb526ad14234a74143413669b28128c4293320bcc5

## PIVOT (plain language, before the charter)
The one thing that has to be true for this business — that farmers will pay ~20 KES/week for price SMS — is the exact thing a decade of Kenyan price-SMS services (M-Farm, Sokopepe, KACE, Esoko, Safaricom DigiFarm) could never make true; low willingness-to-pay for pure information is the documented reason these services stall at pilot. Price knowledge alone rarely raises the farmgate price, because the binding constraint is buyer access and logistics, not ignorance of the number. So we preserve the goal (farmers capture more value) but move the money: build price transparency *inside an actual transaction* and let the buyer/aggregator, not the farmer, pay for reach.

## 1. The idea as received
> An SMS service that sends smallholder farmers daily market prices for their crops so they get fair prices. Founder: "farmers will happily pay 20 bob a week for this."

## 2. What we researched
- **Incumbency:** SMS/USSD price services are a crowded graveyard in Kenya — M-Farm (price-SMS, effectively defunct), Sokopepe/SokoniSMS, KACE (USSD), Esoko (SMS since 2008, pivoted to bundled advice/insurance), Safaricom DigiFarm (bundled, not price-only). The consistent pattern is pivot-away-from-paid-price or donor subsidy.
- **Eclipse (angle 8):** price information is commoditized and increasingly free (radio, WhatsApp market groups, DigiFarm). A paid, price-only SMS is eclipsed on day one.
- **Founder claim priced at 0.30:** "farmers will happily pay 20 bob/week" is founder_intuition with no field signal. Category evidence points the other way ("low willingness to pay… is one reason DFS firms struggle to scale beyond pilot" — IFPRI/AgriFin).
- **Where value actually moves:** the margin sits with the offtaker/aggregator who needs reliable farmer-side volume. They can pay for a channel that price-only SMS can't monetize from farmers.
- **Guardian surface (kernel):** macro_regulator, meso_community (cooperatives/SACCOs), micro_street (agro-dealers, brokers). No hard licence blocker — this is a demand/eclipse redirect, not a regulatory one.

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Kenyan price-SMS services (M-Farm, Sokopepe, KACE, Esoko, DigiFarm) exist; low WTP stalls them at pilot | IFPRI "Promise of digital farmer services"; FAO STI portal (Esoko/DigiFarm); tractor.co.ke survey | academic/official/news | ifpri.org/blog; sti-portal.fao.org | accessed 2026-07-10 | verified |
| Esoko began price-SMS in 2008, pivoted to bundled services | FAO STI Portal | official | sti-portal.fao.org | accessed 2026-07-10 | verified |
| Exact current subscriber counts / revenue of each incumbent | — | — | — | — | UNKNOWN - not verified |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]
- Evidence bill (verbatim, before scale): farmer >=25 signals (embeddedness, continuity, infrastructural_intimacy, fractal_trust, reciprocity); distributor >=25; guardian >=2; beneficiary >=100; public_official >=2.

## 4. Who you are in this build (0.30 inference)
No passport supplied; operator reach is self-reported and capped at 0.30. The redirect deliberately picks a wedge that needs only ONE offtaker relationship to test, so it is carryable by a solo/small operator without a field sales army.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** a price-transparency layer bolted onto ONE offtaker's buying operation in ONE crop/corridor — SMS confirms today's offered price and books the pickup; the farmer sees the number *and* can act on it in the same message.
- **Who pays:** the offtaker/aggregator (for verified farmer volume and lower side-selling), not the farmer.
- **Distributed through:** the offtaker's existing collection agents / cooperative, not cold SMS blasts.
- **Explicitly NOT building:** a paid farmer-subscription price feed (eclipsed, WTP unproven); a national multi-crop exchange; anything holding money.
- **What a demo will NOT prove:** that farmers value the price number enough to change behaviour, or that any farmer would pay for it. Buildability is free here.

## 6. Redirect
Died on: eclipse (free price info) + a decade of category WTP failure. Adjacent build that survives: transaction-embedded price transparency paid by the offtaker. Smallest falsifiable pilot: one offtaker, one crop, one corridor, 4 weeks.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims remain non-authorized (kernel baseline). "Farmers will pay" may not appear in any external deck until a field pack attests it.

## 7A. Evidence still missing
| Lane | Minimum | Why it matters |
|---|---|---|
| farmer | >=25 signals | Is price *action* (not just price knowledge) the wedge? |
| distributor/offtaker | >=25 | Will an offtaker pay for verified farmer volume? |
| guardian (cooperative/SACCO) | >=2 | Channel permission to reach farmers at all |

## 8. Settlement (written before build)
- **t+90d:** at least one offtaker pays for the price+booking channel and >=40% of enrolled farmers act on a price message (accept/decline pickup). If farmers only *read*, the thesis is falsified.
- **t+365d:** the channel survives without donor subsidy in one corridor.
- **Settlement metric:** paying-offtaker retention + farmer action-rate on price messages (instrumented; silence = failure).
