# BUILD CHARTER — RetailFlow
**Charter ID:** CH-c22945d5-7213-4d74-ffff-dc6dc16301a0 · **Date:** 2026-07-07 · **Archetype:** fintech_platform · **Market:** UG/Kampala and KE/Nairobi
**Status:** redirected · **Preregistration hash:** 5886c11ae7fa600006a82927d49c5e5cbf2a2d2574d7b1c9e8fa6c87e3050ca1 (anchors: pending; see `mvr/decision-log.json`)

> This charter is a dated, hashed, settleable prediction. Settlement checkpoints at the bottom were written before the build.

## 1. The idea as received
"I want to build a WhatsApp-first platform for informal electronics retailers in Kampala and Nairobi. Small shops can message suppliers for stock, compare wholesale prices, place orders, and later unlock 7-day credit terms based on reorder behavior. I know a few shop owners and one importer who says this could work. I want to move quickly: build the ordering flow, supplier dashboard, payment reminders, and a simple credit score so I can show traction to angels within 60 days. Please plan the MVP and fastest path to first users."

## 2. What we researched so you didn't have to answer it
*   **Incumbency Scan:** Established B2B e-commerce platforms like Wasoko (merged with MaxAB in 2024 to form MaxAB Wasoko Group) and Kyosk operate in Kenya and Uganda, but focus primarily on FMCG, groceries, and essential commodities, not specialized electronics. Copia Global, a major B2C agency-based logistics and retail player, went into administration in May 2024. B2B electronics are primarily served by specialized ICT distributors like Shopit in Kenya or local wholesale importers in Kampala.
*   **Rails Ownership:** Mobile money rails dominate transactions: Safaricom M-Pesa in Kenya; MTN Mobile Money and Airtel Money in Uganda. Aggregation is handled by payment facilitators like Pesapal and Flutterwave.
*   **Guardian Topology:** The Central Bank of Kenya (CBK) and Bank of Uganda (BoU) regulate payment services and digital credit. Street retailer and vendor associations, alongside municipal authorities (KCCA in Kampala, Nairobi City County), hold local relational influence.
*   **Permission Structure:** Operating payment systems or digital credit services requires regulatory licensing (CBK Digital Credit Provider license in Kenya, Bank of Uganda PSP/money lending license in Uganda).
*   **Category Failure Modes:** B2B credit platforms in East Africa have historically collapsed due to cash flow mismatch, retailer side-selling (routing purchases outside the platform to avoid repayment), and high non-performing loans (NPLs) on short-term unsecured credit.

### Source ledger (mandatory for beta)
| Claim / fact used in charter | Source name | URL or local evidence ref | Published / accessed date | Status |
|---|---|---|---|---|
| Copia entered administration in May 2024 | Trendtype | https://trendtype.com/copia-kenya-enters-administration/ | 2024-05-24 | verified |
| Wasoko merged with MaxAB in 2024 | Africa Signal | https://africasignal.com/wasoko-maxab-merger | 2024-08-01 | verified |
| Uganda National Payment Systems regulation under Bank of Uganda | Bank of Uganda | https://www.bou.or.ug/bouwebsite/PaymentSystems/National-Payment-Systems.html | 2020-09-04 | verified |
| CBK licenses Payment Service Providers and Digital Credit Providers | Central Bank of Kenya | https://www.centralbank.go.ke/ | 2022-03-01 | verified |
| Shopit B2B electronics distribution in Kenya | Shopit Kenya | https://shopit.co.ke/ | 2026-07-07 | verified |

## 3. What the evidence machine said (quoted, not paraphrased)
- Sparring: unsafe claims -> "unlock 7-day credit terms based on reorder behavior" (automated credit underwriting), "traction to angels within 60 days" (unauthorized capital allocation claim).
- Evidence bill before pilot / before scale -> Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack, and guardian_or_regulatory_evidence.
- Decision check (if pack existed): verdict permission_not_yet_earned, confidence 0.00 (low), blockers ["zero_geo_matches", "telemetry_proxy_pack_missing", "guardian_or_regulatory_evidence"]
- Receipts: decision_check_id 4ee9ff443b1cae7df0cdb6623480b82092efdbda2495947293210ef146884afe, semantic hash e22945d572130d74ffffdc6dc16301a09283b2cd945f868b68e3804393eb9adc

## 4. Who you are in this build (from your passport — correct via the Mirror)
- **Reach:** Inferred reach is highly localized and relationship-dependent. The operator has self-reported relationships with "a few shop owners" and "one importer" (0.30 weight, 0.50 uncertainty).
- **Capacity:** No specialized licenses held (no CBK DCP or BoU PSP license). Capital and runway are self-reported/low.
- **Fit:** The operator cannot carry credit underwriting or automated lending due to lack of licenses, data history, and capital. A cash-first broker/brokerage model fits the operator's actual assets today.

## 5. THE BUILD
- **Build this:** A WhatsApp-based concierge ordering system (manual order routing and pricing sheets over WhatsApp) operating on a strict cash-on-delivery (CoD) or cash-before-delivery (CbD) basis.
- **For:** The initial warm contact group of local electronics retailers and the single importer partner.
- **Distributed through:** A direct WhatsApp group chat or manual broker number.
- **Explicitly NOT building (and why):**
  - Credit Scoring / Scoring Engine: Forbidden action under strict safety rules; no regulatory license to underwrite credit.
  - Supplier Dashboard: Unnecessary for a pilot with one importer (leads to overbuilding).
  - Automated Payment Reminders: Redundant on cash-first ordering.
- **What the working demo will NOT prove:**
  - Will NOT prove the creditworthiness of informal retailers.
  - Will NOT prove that reorder behavior is a reliable proxy for credit risk in this segment.
  - Will NOT prove retailer willingness to abandon existing informal suppliers.

## 6. Redirect (only if the original idea did not survive)
- **Why it died:** Gated by missing regulatory licenses (CBK DCP in Kenya, Bank of Uganda money lending license in Uganda) and absence of relational/telemetry evidence. Pitching angels with unauthorized credit claims is blocked (capital_allocation not authorized).
- **Strongest Adjacent Build:** A cash-first B2B ordering concierge service on WhatsApp. Retailers message pricing/orders, operator manually routes orders to the importer, coordinates cash delivery, and accumulates actual transaction logs.
- **Smallest Falsifiable Pilot:** 5 retail shops ordering from 1 importer for 3 weeks, entirely cash-on-delivery, tracking actual purchase margins and delivery delays manually.

## 7. Claims you may not make yet
- **capital_allocation:** Investor decks or angel pitches claiming credit scoring capabilities or digital credit traction.
- **national_rollout:** Claims of readiness to scale across Kenya/Uganda.
- **board_reporting:** Unsupported compliance or financial performance claims.

## 7A. Evidence still missing before stronger claims
| Evidence Lane | Why it matters | Source/Counterparty Needed | Claim Unlocked Only If Verified |
|---|---|---|---|
| guardian_or_regulatory_evidence | Legality of credit terms | Central Bank of Kenya / Bank of Uganda | credit terms / debt launch |
| localized_observed_pack | Retailer demand / side-selling risk | 25+ structured retailer surveys in Kampala & Nairobi | pilot rollout |
| telemetry_proxy_pack | Transaction frequency and margins | 100+ actual concierge cash transactions | investor deck export |

## 8. Settlement (we will be judged by this)
- **t+90d:** Concierge pilot active with >=10 retailers making >=3 cash orders per week; order fulfillment rate >= 85%.
- **t+365d:** Partner with a licensed financial institution/PSP to run a credit pilot, or obtain necessary agency licenses, with transaction logs acting as the primary data feed.
- **Settlement channels:** transaction logs (telemetry proxy) of cash purchases, partner attestation from the importer.

---
*Internal appendix: Strategy sparring was called successfully with MVR client. Edge returned challenge_ready status under home-market calibration tier.*

# MIRROR — what I assumed about you and your market

## About you (inferred, never asked)
| # | I assumed | Basis | If wrong, the consequence |
|---|---|---|---|
| 1 | You have no direct relationships with regulatory authorities (CBK or BoU). | No license registrations mentioned in prompt or files. | A warm relationship or existing license would allow credit terms. |
| 2 | You do not have the capital to absorb credit defaults or bad debt. | Founder prompt indicates early stage, looking for angel traction in 60 days. | Larger capital reserves would permit balance-sheet credit pilots. |
| 3 | Your retail network is limited to a few personal acquaintances. | "I know a few shop owners..." | Large structured retail networks would enable warm pilot distribution. |

## About your market (researched — sources in charter §2)
| # | I concluded | If you know better |
|---|---|---|
| 4 | Informal retailers prefer cash-on-delivery and rely on established street relationships. | Evidence of structured supplier agreements or credit terms. |

## One choice instead of five questions
- **Option A — the build for the assets you have today:** A cash-first WhatsApp concierge ordering pilot with 5 shops and 1 importer.
- **Option B — the build if you can secure a licensed credit partner:** A WhatsApp interface integrating a licensed microfinance provider's credit approval API.
