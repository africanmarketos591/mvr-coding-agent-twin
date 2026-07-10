# BUILD CHARTER - 15-Minute Grocery, Accra (c09)
**Date:** 2026-07-10 | **Archetype:** ecommerce_platform | **Market:** GH
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: b8f644ac6608ee1108da63c9f00e3ab7b2a56ab674a296e5671e3d927d113f7d

## PIVOT (plain language, before the charter)
The "15 minutes" is the part that kills the business, not the part that wins it: the global instant-grocery cohort that pioneered this exact model — Gorillas, Getir, Jokr — raised billions and still collapsed because owned dark stores plus a 15-minute promise plus employed riders make the unit economics structurally unprofitable (Jokr lost ~$13.6M on $1.7M revenue). Accra's lower basket sizes and higher last-mile friction make it worse, not better. We keep the goal (convenient grocery delivery for Accra households) but drop the two cash-fires — the 15-minute SLA and the dark-store capex — for an asset-light, scheduled/same-day model that can actually clear a margin.

## 1. The idea as received
> A 15-minute grocery delivery app for Accra: order groceries, delivered in 15 minutes from local dark stores.

## 2. What we researched
- **Model failure mode (decisive):** the 15-minute/dark-store model is a documented global casualty — Gorillas laid off staff and exited multiple countries; Getir cut ~4,480 staff; Jokr lost $13.6M on $1.7M revenue and exited the US. The instant model owns/leases hubs and employs riders, breaking the asset-light economics that make delivery work.
- **Local reality:** Accra basket sizes, road/addressing friction, and payment mix make a sub-15-minute promise even harder to hit profitably than in the Western cities where it already failed.
- **Eclipse/substitution:** existing on-demand players (Bolt Food, Glovo/Jumia-type services, neighbourhood shops + informal riders) already cover convenience without dark-store capex.
- **Guardian surface (kernel: macro/meso/micro):** soft/none regulatory — this is a unit-economics blocker, not a licence one.

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Gorillas/Getir/Jokr raised billions then collapsed; Jokr lost $13.6M on $1.7M revenue; instant model's owned-hub + employed-rider economics are structurally unprofitable | Oversharing (Griswold); Fast Company; Below the Line | news/analysis | oversharing.substack.com; fastcompany.com | accessed 2026-07-10 | verified (pattern); firm-level figures per cited articles |
| Accra-specific basket/last-mile economics | — | — | — | — | UNKNOWN - not verified |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. A dark-store network + 15-min SLA needs deep capital and dense ops — not carryable. The redirect is scoped to an asset-light pilot one operator can run off existing stores.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** asset-light **scheduled / same-day** grocery delivery in ONE dense Accra neighbourhood, sourcing from EXISTING shops/supermarkets (no dark-store capex), with a realistic delivery window and transparent fees that cover the drop.
- **For:** households in one neighbourhood; supply from existing named retailers.
- **Distributed through:** partnership with existing stores + on-demand riders.
- **Explicitly NOT building:** any 15-minute SLA, owned/leased dark stores, employed rider fleet, or multi-zone launch. Those are precisely the line items that bankrupted the model globally.
- **What a demo will NOT prove:** that customers will pay a fee that covers the drop, or that repeat frequency clears CAC. A fast demo delivery proves nothing about margin.

## 6. Redirect
Died on: structurally unprofitable model (global corpses) worsened by Accra economics. Adjacent build: asset-light, scheduled, existing-store-sourced delivery. Smallest pilot: one neighbourhood, no dark store, margin-positive per drop.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. No "profitable instant delivery" claim — the category evidence points the other way.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| customer (beneficiary) | >=100 | Repeat frequency + fee tolerance |
| retailer/supplier | >=25 | Asset-light supply willingness |
| per-drop margin | instrumented | The only number that matters |

## 8. Settlement (written before build)
- **t+90d:** delivery in one neighbourhood is **contribution-margin-positive per order** (fee > variable cost) with real repeat customers. If margin is negative, the redirect itself is falsified and the answer is "don't build."
- **t+365d:** one zone sustains positive contribution margin without subsidy.
- **Settlement metric:** contribution margin per delivered order + repeat rate (instrumented; negative margin = stop).
