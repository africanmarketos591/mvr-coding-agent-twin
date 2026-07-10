# BUILD CHARTER - Lagos FMCG Restock + Credit (c08)
**Date:** 2026-07-10 | **Archetype:** ecommerce_platform | **Market:** NG
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: fec418e21632ce6e8ba80eb2d2c4e81a9d943fa08fe057374d4d32edabc4cbf8

## PIVOT (plain language, before the charter)
The credit half of this idea is regulated lending — the Central Bank of Nigeria's digital-lending rules require licensing and credit-bureau reporting, so a greenfield app cannot just "add a credit option" and stay legal, and the claim gate will block any credit-marketing claim until that's authorized. The ordering half is a crowded field already owned by well-capitalized incumbents (TradeDepot, Sabi, OmniBiz/OmniRetail) who bundle logistics AND embedded BNPL. So we keep your customer — the Lagos shop owner who needs reliable stock — but drop the greenfield loan book: ride a licensed credit partner (or defer credit entirely) and win a supply niche the incumbents under-serve rather than cloning them head-on.

## 1. The idea as received
> A Lagos app for informal shop owners to order FMCG stock from suppliers and get it delivered, with a credit option.

## 2. What we researched
- **Regulatory blocker (credit):** CBN digital-lending guidelines require licensing + credit-bureau reporting for consumer/SME lending. Embedded "credit option" = a regulated activity, not a feature toggle. An UNKNOWN licence status is itself grounds for non-authorization of the credit claim.
- **Incumbency:** TradeDepot (100k+ retailers, $110M IFC/Novastar, embedded BNPL), Sabi, OmniBiz/OmniRetail (profitable, OmniPay embedded finance) already do order + deliver + credit in Lagos. The exact proposed product exists at scale.
- **Category failure mode:** the well-funded FMCG-restock cohort has already shown that owning warehouses/fleets + a credit book burns cash; several peers retrenched. Cloning the full stack is capital-intensive and late.
- **Guardian surface (kernel):** macro_regulator (CBN for the credit), meso_community (market/trader associations), micro_street (suppliers/distributors).

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| TradeDepot (100k+ retailers, $110M IFC/Novastar, BNPL), Sabi, OmniBiz/OmniRetail operate Lagos FMCG restock + embedded credit | TechCrunch; GlobeNewswire/Yahoo (Nigeria B2B BNPL 2026 report); OmniRetail | news/company | techcrunch.com; globenewswire.com; omniretail.africa | accessed 2026-07-10 | verified |
| CBN digital-lending guidelines require licensing + credit-bureau reporting | Nigeria B2B BNPL report 2026 (secondary) | news | globenewswire.com | accessed 2026-07-10 | directional — confirm against CBN primary before any credit claim (UNKNOWN - not verified as authority-grade) |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. A full order+deliver+lend stack is not carryable by a small operator against IFC-funded incumbents. The redirect is scoped to one supply niche + a partner-provided credit rail.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** an ordering + delivery-coordination tool for ONE under-served supply niche the incumbents ignore (e.g., a specific category/corridor or a supplier cluster), **credit disabled at launch**; if credit is needed, it is provided by a CBN-licensed lending partner whose licence the shop owner can verify — never an app-held loan book.
- **For:** a named cluster of Lagos shop owners in one market/corridor.
- **Distributed through:** existing supplier/distributor relationships and market associations.
- **Explicitly NOT building:** a proprietary consumer/SME loan book (regulated; unlicensed = illegal + claim-gated), a full TradeDepot/Sabi-style national warehouse+fleet+BNPL stack.
- **What a demo will NOT prove:** that shops will switch from TradeDepot/Sabi, or that the credit economics work. A working order screen proves nothing about repayment or margin.

## 6. Redirect
Died on: credit = regulated (CBN, unlicensed) + saturated incumbents + capital-heavy failure mode. Adjacent build: niche ordering/logistics, credit only via licensed partner. Smallest pilot: one corridor, no own-balance-sheet lending.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. **Any credit/lending claim is blocked** until a licensed-partner arrangement (or CBN licence) is verified and logged — UNKNOWN licence status keeps it blocked and adds a mandatory verification task.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| shop owner (b2b user) | >=25 | Will they switch supplier app at all? |
| distributor/supplier | >=25 | Supply reliability is the real wedge |
| CBN / licensed lender status | verified (authority-grade) | Unlocks any credit claim; UNKNOWN = stays blocked |

## 8. Settlement (written before build)
- **t+90d:** one corridor reorders through the tool weekly on supply reliability alone (no credit), with fill-rate beating their status quo.
- **t+365d:** the corridor retains and, if credit launched, it runs on a verified licensed partner with clean repayment.
- **Settlement metric:** weekly reorder rate + order fill-rate in one corridor (instrumented). Credit metrics only after licence verification.
