# BUILD CHARTER - Drone Medical Delivery, Rural Rwanda (c11)
**Date:** 2026-07-10 | **Archetype:** logistics_platform | **Market:** RW
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 312d7a42cc88d945908f064cb79e3f77362f0c56fcaffd365ca6b9aa1bae241d

## PIVOT (plain language, before the charter)
This exact service already exists in Rwanda at national scale: Zipline has run government-contracted drone delivery of blood and essential medicines to rural facilities since 2016, under an agreement with the Ministry of Health and drone-specific airspace rules co-designed with the Rwanda Civil Aviation Authority — Rwanda was the first country in the world to legalize drone delivery for national health logistics. A greenfield entrant would be cloning a deeply embedded incumbent whose two hardest assets — the MoH contract and reserved airspace corridors — are already locked. We keep the goal (rural clinics get lifesaving supplies faster) but redirect off "build another Zipline" toward the gaps around it: last-mile from drop-point to clinic, cold-chain and stock visibility at the clinics, or non-covered commodities — or partnering rather than competing.

## 1. The idea as received
> Drone delivery of blood and essential medicines to rural clinics in Rwanda that are hours from the nearest hospital.

## 2. What we researched
- **Incumbency (decisive, S16B-class trap):** Zipline launched on-demand blood/medical delivery in Rwanda in October 2016 under a Government of Rwanda contract; expanded with a second distribution centre (Kayonza, 2018) covering health centres and hospitals, blood, vaccines and medical products.
- **Permission structure:** the RCAA co-designed drone-specific airspace policy with the MoH; operators fly in constant coordination with Rwandan ATC. Airspace access is a relational, government-mediated asset — not something a new entrant simply applies for.
- **Guardian topology (kernel: macro_regulator, meso_community, micro_street):** macro = RCAA + MoH (veto holders); the incumbent already holds both.
- **Eclipse:** the incumbent + its government relationship IS the eclipse. Building the same drone-to-clinic service head-on means fighting locked rails.

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Zipline operates govt-contracted drone blood/medicine delivery in Rwanda since Oct 2016; MoH agreement; 2nd centre Kayonza 2018 | Rwanda MINICT; Reach Alliance; Wikipedia; PBS | official/academic/news | minict.gov.rw; reachalliance.org | accessed 2026-07-10 | verified |
| RCAA co-designed drone airspace policy with MoH; Rwanda first to legalize drone delivery for national health logistics; operators coordinate with Rwandan ATC | Reach Alliance report; ethicalbusiness.africa | academic/news | reachalliance.org | accessed 2026-07-10 | verified (directional on "first"; RCAA authority relationship confirmed) |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. Drone hardware ops + a national MoH contract + reserved airspace is not carryable by a new operator. Every viable path here is adjacent-to or partnered-with the incumbent, not against it.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** the ground-side gap the drone network does NOT close — a **last-mile-from-drop-point + clinic stock/cold-chain visibility layer** for rural clinics (when a supply lands, is it received, stored correctly, and reflected in clinic stock?), designed to *complement* the existing air network, in ONE district.
- **For:** rural clinics in one district (via district health office).
- **Distributed through:** the district health system; explore integration/partnership with the existing air operator rather than replacing it.
- **Explicitly NOT building:** a competing drone-delivery air operation (locked airspace + MoH contract), any claim of holding aviation/health authorizations we do not have.
- **What a demo will NOT prove:** that RCAA/MoH would ever license a second air operator, or that clinics need a new tool. A flying-drone demo proves buildability, not permission — permission is the whole barrier.

## 6. Redirect
Died on: embedded government-contracted incumbent (Zipline) + locked airspace/MoH permission (RCAA). Adjacent build: ground-side last-mile + clinic stock visibility, complementing not competing. Smallest pilot: one district health office.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. **No claim of holding RCAA aviation or MoH authorization** may appear anywhere until such authorization is real and verified — fabricating a regulated capability is a hard violation.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| clinic (beneficiary) | >=100 | Is ground-side stock/cold-chain the real gap? |
| MoH / district guardian | >=2 | Permission is the entire barrier |
| RCAA airspace status | verified (authority-grade) | Any air-operation claim stays blocked absent this |

## 8. Settlement (written before build)
- **t+90d:** one district uses the ground-side receipt + stock-visibility tool for real deliveries, with the district health office confirming value.
- **t+365d:** the tool is retained by the district and/or a partnership with the air operator is formalized.
- **Settlement metric:** district-health-office retention + clinic stock-visibility usage (instrumented). No air-side metrics until authorization exists.
