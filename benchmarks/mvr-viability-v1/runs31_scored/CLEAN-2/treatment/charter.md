# BUILD CHARTER - QR Menu + Dine-in Ordering, Nairobi (c05)
**Date:** 2026-07-10 | **Archetype:** b2b_saas_platform | **Market:** KE
**Status:** build_authorized (smallest wedge; market-claim scope = single-venue operational tool, NOT rollout)
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 1e5aaec45cafc6a79800fc1d8c604637339861a3f1468142fd1d2c81fb7161d3

## STATUS NOTE (plain language, before the charter)
This is a clean idea with no blocker: the app never touches money (payment stays at the restaurant's existing till), so there is no payments/e-money licence to trip on, and the workflow it automates — dine-in order to kitchen ticket — is a real, acute, daily operational pain. Per doctrine, when a clean idea has no blocker you authorize the build rather than reflexively redirecting. We authorize the **smallest wedge** (one workflow, one venue) and keep the market claim narrow: this proves an operational tool works, not that a category business exists.

## 1. The idea as received
> A tool for Nairobi restaurants to create QR-code digital menus and take dine-in orders that print to the kitchen. Payment happens at the restaurant's existing till; the app never touches money.

## 2. What we researched
- **Permission:** no money movement ⇒ no CBK/e-money footing required. This is the cleanest regulatory posture in the batch.
- **Incumbency/eclipse (angle 8):** generic QR-menu builders exist globally, but the **dine-in kitchen-order-ticket (KOT) printing** loop — waiter no longer runs to the kitchen — is a concrete operational value that generic menu QR tools don't close. Payment-app incumbents (M-Pesa till) are complementary, not competitors, since we deliberately don't touch money.
- **Guardian surface (kernel: macro/meso/micro):** soft — restaurant owner + kitchen staff adoption, not a regulator. The real risk is adoption friction and thin-margin willingness to pay, not permission.
- **Unit reality:** Nairobi restaurants run thin margins; pricing must be low and value must be immediate (labour saved, order errors cut).

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| App holds no money ⇒ no e-money/payments licence triggered | design fact (idea explicitly excludes payments) | — | this charter | 2026-07-10 | verified (by construction) |
| Named Nairobi QR-menu competitors + their share | — | — | — | — | UNKNOWN - not verified |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. Single-venue scope means one operator can install and support it directly.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** QR menu + dine-in order capture that prints a KOT to the kitchen printer, for ONE Nairobi restaurant. The wedge is the **order → kitchen ticket** loop; the menu is just the front door.
- **For:** one named restaurant (operator's real first venue).
- **Distributed through:** direct install; staff trained on-site at one venue.
- **Explicitly NOT building:** in-app payments/wallet (kept out by design), reservations/loyalty/POS-accounting, multi-venue dashboards, marketplace/aggregator features. Those come only after the single-venue loop is sticky.
- **What a demo will NOT prove:** that other restaurants will pay, or that staff keep using it past the novelty week. A working KOT print proves the workflow, not the market.

## 6. Redirect
None. No blocker, sharp operational wedge — build authorized at smallest scope.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. "Restaurants will pay / adopt widely" needs multi-venue evidence before any external deck.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| restaurant operator (b2b user) | >=25 | Multi-venue willingness to pay |
| kitchen/waitstaff | field pack | Staff adoption is the retention gate |

## 8. Settlement (written before build)
- **t+90d:** the first venue routes >=70% of dine-in orders through the tool for 4 consecutive weeks without reverting to paper chits.
- **t+365d:** venue is paying and at least 2 more venues onboarded on referral.
- **Settlement metric:** share of dine-in orders flowing through KOT print at the pilot venue (instrumented; reversion to paper = failure).
