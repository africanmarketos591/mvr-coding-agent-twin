# BUILD CHARTER - Diaspora Pooled Investment Fund App (c12)
**Date:** 2026-07-10 | **Archetype:** fintech_platform | **Market:** KE
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 180de665180f55232c33edff79a65fa15589432152dafa717ea7dda46e5fc7d4

## PIVOT (plain language, before the charter)
Pooling many people's money and investing it in stocks and money-market funds for a return is, in Kenya, a licensed activity: under the Capital Markets Act a collective investment scheme must be approved by the Capital Markets Authority and whoever manages that pool above the small-investor threshold needs a CMA fund-manager licence plus an independent CMA-licensed custodian — an unlicensed app cannot legally hold and invest the public's money. This is a hard blocker for a greenfield build, and the claim gate will block any "we invest your money for returns" claim until that licence exists. We keep the member outcome (Kenyans at home and abroad grow money together) but redirect from "the app invests the fund" to "the app is the distribution + chama layer on top of an already CMA-licensed fund," so the money is always inside a licensed vehicle.

## 1. The idea as received
> An app where Kenyans in the diaspora and at home pool monthly contributions into a shared fund that the app INVESTS in stocks and money-market funds, paying members returns.

## 2. What we researched
- **Regulatory blocker (decisive):** Capital Markets Act s.23 — carrying on the business of a fund manager requires a CMA licence; operating a collective investment scheme requires CMA approval. Managing a portfolio above KES 10M requires a fund-manager licence (below that, only an investment-adviser licence). Fund managers must appoint a CMA-licensed custodian. Pooling public contributions to invest = a CIS + fund management, squarely regulated.
- **Cross-border angle:** diaspora contributions add remittance/forex and cross-jurisdiction KYC obligations on top.
- **Ride-not-fight path:** CMA already licenses digital wealth managers and unit-trust/MMF providers (regulated fund managers and money-market funds exist). A distribution app can plug members INTO a licensed fund rather than becoming the fund.
- **Guardian topology (kernel):** macro_regulator (CMA + CBK/remittance), meso_community (chama/SACCO trust), micro_street (member trust; fraud history in "investment apps" makes reassurance artifacts mandatory).

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Capital Markets Act s.23: fund-manager licence + CIS approval required; >KES 10M portfolio needs fund-manager licence; CMA-licensed custodian required | Capital Markets Authority; Kenya Law (CMA Regulations); Lexology fintech-KE | regulator/official | cma.or.ke; kenyalaw.org | accessed 2026-07-10 | verified |
| Named specific licensed partner to ride | — | — | — | — | UNKNOWN - not verified (identify a current CMA-licensed fund manager/MMF before any partnership claim) |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. A greenfield fund-manager licence + custodian + CIS approval is not carryable by a small operator and is legally fatal if skipped. The redirect (distribution layer on a licensed fund) needs no securities licence for the app itself and only one licensed partner.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** a **contribution + chama-coordination + distribution layer** that routes members' monthly contributions into an EXISTING CMA-licensed money-market fund / unit trust — the app never holds, manages, or invests the money; the licensed fund does. Members see pooled goals, contributions, and their licensed-fund statements.
- **For:** one chama / diaspora savings group as the first pool.
- **Distributed through:** existing chama/SACCO trust networks (the real credit-and-trust layer) + a named CMA-licensed fund partner.
- **Explicitly NOT building:** an app that itself invests in stocks/MMFs or holds the pooled fund (that is a CIS + fund management — unlicensed = illegal + claim-gated), any "guaranteed returns" language, custody of member money.
- **What a demo will NOT prove:** that the structure is CMA-compliant, or that members trust an app with pooled money given the sector's fraud history. A working returns screen would be a dangerous hallucination here.

## 6. Redirect
Died on: pooling + investing public money = CMA-licensed CIS/fund management; unlicensed greenfield is illegal. Adjacent build: distribution/chama layer on a licensed fund; app never touches the invested pool. Smallest pilot: one chama into one licensed MMF.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. **Any "we invest your money / pay returns" claim is blocked** until CMA licensing (own or via named licensed partner) is verified and logged; UNKNOWN status = stays blocked + mandatory verification task. No returns figures may be shown, ever, without the licensed fund's own disclosures.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| member (beneficiary) | >=100 | Trust to route pooled money through an app |
| chama/SACCO guardian | >=2 | The real trust layer to join, not bypass |
| CMA licence / licensed-partner status | verified (authority-grade) | Unlocks any investment/returns claim; UNKNOWN = blocked |

## 8. Settlement (written before build)
- **t+90d:** one chama routes real monthly contributions into a named CMA-licensed fund via the app, with money never resting in an app-held account and members reading the licensed fund's own statements.
- **t+365d:** the pool retains and a second chama joins on trust/referral, still with zero app custody of invested funds.
- **Settlement metric:** contributions successfully placed into a licensed fund with zero app-custody days (instrumented; any app-held invested balance = structure breached).
