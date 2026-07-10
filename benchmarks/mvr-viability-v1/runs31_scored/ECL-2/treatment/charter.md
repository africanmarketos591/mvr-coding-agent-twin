# BUILD CHARTER - Boda Super-App Kampala (c02)
**Date:** 2026-07-10 | **Archetype:** passenger_mobility | **Market:** UG
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 9fe1f3cce0ea7847fc1038af7710f04225caae1e61cfc39aec267ee0805dfb08

## PIVOT (plain language, before the charter)
The hail+pay+parcel super-app you describe already exists in Kampala and is called SafeBoda — a Kampala-born, Google-backed incumbent doing roughly 80,000 rides a day (Uber and Bolt together barely reach 10,000), already with in-app payments and delivery. Building the same thing head-on means fighting a network-effects incumbent on its home turf with less capital, which is how mobility clones die. We keep your customer (Kampala boda riders and their passengers) but move off the saturated consumer-hail lane into a rider-side / stage-level wedge those incumbents don't own.

## 1. The idea as received
> A motorcycle-taxi (boda-boda) super-app for Kampala: hail rides, pay in-app, plus parcel delivery.

## 2. What we researched
- **Incumbency:** SafeBoda (founded 2014, Kampala; Google $50M Africa fund; CBoU payments licence; ~80k rides/day), plus Uber Boda and Bolt Boda (together ~10k/day). SafeBoda already offers pay + food + delivery — the exact "super-app" surface proposed.
- **Eclipse (angle 8):** every feature in the brief is an existing incumbent feature. Direct clone = erased on arrival.
- **Rails:** consumer ride-hail rails are owned by SafeBoda/Bolt/Uber. Fighting those rails is a capital war, not a wedge.
- **Guardian surface (kernel):** macro_regulator (transport/PSV + BoU for payments), meso_community (boda stage associations, SACCOs), micro_street (stage chairmen). The under-served layer is stage/association-side, not consumer-side.

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| SafeBoda ~80k rides/day; Uber+Bolt ~10k; Kampala-founded 2014; Google-backed; BoU payments licence; already offers pay/food/delivery | TechCrunch (2021, 2022); TechMoran | news | techcrunch.com; techmoran.com | accessed 2026-07-10 | verified |
| Current exact market share % / rider counts today | — | — | — | — | UNKNOWN - not verified |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]
- Guardian veto surface: macro_regulator, meso_community, micro_street.

## 4. Who you are in this build (0.30 inference)
No passport; reach capped at 0.30. A greenfield consumer super-app needs rider liquidity + passenger demand + payments float simultaneously — not carryable by a small operator. The redirect is chosen to need only ONE stage/association to test.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** a rider/stage operations tool for ONE boda SACCO or stage association — shift/earnings tracking, cashless float settlement, and a *parcel-only* corridor the incumbents under-serve — riding on top of existing hailing rather than replacing it.
- **For:** one named stage chairman / SACCO (from operator's real network).
- **Distributed through:** the association's existing WhatsApp + stage meetings.
- **Explicitly NOT building:** a consumer hailing app (SafeBoda owns it), an in-app wallet touching money before a BoU payments footing, national coverage.
- **What a demo will NOT prove:** that riders will leave SafeBoda, or that consumer hailing demand exists for a new entrant. A slick hail screen proves nothing about liquidity.

## 6. Redirect
Died on: dominant, better-capitalized, home-market incumbent + total feature eclipse. Adjacent build: rider-side / association operations + niche parcel, not consumer hail. Smallest pilot: one SACCO, parcel + float, 6 weeks.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. No "we can beat SafeBoda" claim without field evidence. Any in-app money movement requires BoU authorization before it appears in a claim.

## 7A. Evidence still missing
| Lane | Minimum | Why it matters |
|---|---|---|
| rider/driver | >=25 | Will riders adopt a non-hail tool at all? |
| association guardian | >=2 | Stage-chairman permission is the real gate |
| parcel demand | field pack | Is the parcel niche real and unserved? |

## 8. Settlement (written before build)
- **t+90d:** one stage/SACCO runs float settlement + parcel through the tool weekly, without incentive bribery.
- **t+365d:** the association renews / expands to a second stage on its own word.
- **Settlement metric:** weekly active riders in one association + parcel jobs completed (instrumented).
