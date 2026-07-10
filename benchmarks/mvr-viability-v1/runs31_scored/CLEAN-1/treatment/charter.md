# BUILD CHARTER - Offline Bookkeeping for Dukas (c04)
**Date:** 2026-07-10 | **Archetype:** b2b_saas_platform | **Market:** KE
**Status:** pilot_only
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: c1833930e0e02bfeb931f18686194b802d5fc2c69ad88a34c1259327ec6a5690

## PIVOT / STATUS NOTE (plain language, before the charter)
There is no regulatory blocker here — the idea deliberately never holds money, lends, or processes payments, so we are NOT reflexively redirecting it. The real risk is retention, not legality: pure bookkeeping/inventory apps for informal shops have a graveyard-grade churn problem because a duka owner's head and a notebook are a very cheap substitute. So we authorize a **pilot**, not a build-at-scale claim: prove daily-use retention on a tiny cohort before believing the market.

## 1. The idea as received
> An offline-first bookkeeping and inventory app for informal shop owners (dukas). It records sales, tracks stock, and flags low stock. It does NOT hold money, lend, or process payments.

## 2. What we researched
- **Category reality:** the Kenyan duka space is dominated by B2B *commerce/restocking* players (Wasoko/ex-Sokowatch, Kyosk, MarketForce) whose apps embed light bookkeeping as a *feature* attached to a transaction. Standalone bookkeeping ("record-keeping only") is a known weak-retention wedge because the value is deferred and the substitute (mental accounting + exercise book) is free.
- **Eclipse (angle 8):** the bookkeeping surface is being absorbed into restocking apps and mobile-money statements (M-Pesa till/Pochi records). A record-only app must earn daily use against those.
- **No hard guardian veto:** no licence needed (no money movement). Guardian surface (kernel: macro/meso/micro) is soft here — this is a demand/retention question, not a permission one.
- **Offline-first is a genuine, correct constraint** for intermittent-connectivity dukas — a real product edge if execution is right.

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Wasoko, Kyosk, MarketForce operate B2B duka commerce in Kenya with embedded record-keeping | general market knowledge (not fetched this run) | company | — | — | UNKNOWN - not verified (directional; verify before external use) |
| Standalone bookkeeping apps show weak retention vs transaction-embedded tools | practitioner pattern | — | — | — | UNKNOWN - not verified |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. A record-only app is buildable by a small team, and the pilot is scoped so one operator can hand-hold 15–20 dukas.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** offline-first sales + stock logging with low-stock flags for ~15–20 dukas in ONE market/estate. The wedge feature is **low-stock alert tied to reorder timing** (the one output a shop owner acts on daily), not general ledgers.
- **For:** a named cluster of dukas in one location (operator's real ground).
- **Distributed through:** in-person onboarding at the shops (this segment does not self-serve installs).
- **Explicitly NOT building:** any money-holding, lending, or payments (kept out by design and by claim gate); a national app-store launch; accounting reports no duka owner reads.
- **What a demo will NOT prove:** that owners will keep logging after week 2. Buildability is trivial; *daily retention* is the entire risk.

## 6. Redirect
Not redirected — no blocker, legitimate wedge. Held at pilot_only because adoption/retention is unproven, not because the idea is dead.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. No "dukas love it" claim until retention data exists.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| duka owner (b2b user) | >=25 signals | Day-14 retention is the make/break |
| distributor | >=25 | Is a restocking tie-in the real pull? |

## 8. Settlement (written before build)
- **t+90d:** >=50% of onboarded dukas still log sales at least 4 days/week in week 12 (unincentivized). Below that, the record-only thesis is falsified and the redirect is toward a restocking-embedded tool.
- **t+365d:** the cohort keeps using it and refers a neighbouring shop.
- **Settlement metric:** week-12 unincentivized daily-logging retention (instrumented; silence = churn).
