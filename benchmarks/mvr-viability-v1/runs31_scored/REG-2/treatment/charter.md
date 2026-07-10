# BUILD CHARTER - Earned-Wage Access, Lagos (c10)
**Date:** 2026-07-10 | **Archetype:** fintech_lending | **Market:** NG
**Status:** redirect
**Seats sat:** ADVOCATE[model] RESEARCH[model] SPINE[sat, kernel v6.32.0] OPERATOR[inference_0.30]

## kernel_receipts
immutable_audit_hash: 8364a7a975b6697dc7f78925ff063434e6c9efdb04b3f7bb47f95c6016a2528a

## PIVOT (plain language, before the charter)
Whether this is legal turns entirely on ONE structural choice: if your app fronts the cash and the worker repays you, that is consumer lending under the Central Bank of Nigeria and needs a licence and credit-bureau reporting; if the *employer* funds the advance against wages already earned and you never hold a loan book, it is payroll, not lending — a completely different regulatory world. The only safe, buildable version is the second one, and it also happens to be how the working Nigerian incumbent (Earnipay) is structured: employer-integrated, interest-free, flat fee, no consumer loan book. So we keep the worker outcome (draw earned wages before payday) but build the **non-custodial, employer-funded ledger** and refuse the greenfield consumer loan book.

## 1. The idea as received
> An earned-wage-access app for Lagos factory workers: draw an advance on wages already earned, repay automatically on payday.

## 2. What we researched
- **Regulatory fork:** app-funded advance repaid by the worker = regulated lending (CBN digital-lending licensing + credit-bureau reporting). Employer-funded access to already-earned wages, app never holding the loan = payroll/EWA, not a loan. An UNKNOWN lending-licence status is itself grounds to keep the lending version non-authorized (credit category).
- **Incumbency:** Earnipay is the established Nigerian EWA player — integrates with employer payroll/HR, gives interest-free access to up to ~50% of earned wages for a flat fee (~₦250–₦500), ~150+ employers. A greenfield consumer-lending clone competes worse AND is riskier legally.
- **Structural point:** EWA's whole legitimacy rests on "work already done" + employer integration. Skip the employer and you are just a payday lender.
- **Guardian surface (kernel):** macro_regulator (CBN), meso_community (employer/HR + worker trust), micro_street (factory floor).

### Source ledger
| Fact | Source | Type | Ref | Date | Status |
|---|---|---|---|---|---|
| Earnipay: employer-payroll-integrated EWA, interest-free up to ~50% earned wages, flat ₦250–₦500 fee, 150+ employers | TechPoint Africa; NIPC | news/official | techpoint.africa; nipc.gov.ng | accessed 2026-07-10 | verified (company facts) |
| CBN digital-lending licensing + credit-bureau reporting applies to consumer lending; exact EWA-specific treatment | CBN (not fetched to primary this run) | regulator | — | — | UNKNOWN - not verified — MUST confirm against CBN before any lending claim |

## 3. What the evidence machine said (quoted)
- unsafe_claims: []
- evidence_required: ["Add missing core evidence lanes before board-level decisioning.", "Missing core pack types: public_reality_pack, telemetry_proxy_pack, localized_observed_pack_or_survey_pack"]
- abstention_reason_codes: ["guardian_or_regulatory_evidence"]

## 4. Who you are in this build (0.30 inference)
No passport; reach 0.30. A licensed consumer loan book is not carryable and is legally exposed. The non-custodial employer-funded version needs only ONE factory to test and holds no regulated balance sheet.

## 5. THE BUILD (fitted smallest wedge)
- **Build:** an **employer-funded, non-custodial earned-wage ledger** for ONE Lagos factory — integrate with that employer's payroll, let workers draw a capped share of *already-earned* wages funded by the employer's float, reconcile automatically at payday. The app holds no loan book and fronts no money.
- **For:** one named factory employer + its workers.
- **Distributed through:** the employer/HR relationship (the only viable EWA channel).
- **Explicitly NOT building:** an app-funded consumer advance / loan book (regulated lending, unlicensed = illegal + claim-gated), interest charges, national worker sign-up outside any employer.
- **What a demo will NOT prove:** that employers will fund the float, or that the structure is CBN-clean. A working draw screen proves nothing about the regulatory or funding model.

## 6. Redirect
Died on: the greenfield app-funded version = regulated lending (CBN, unlicensed) + an entrenched, correctly-structured incumbent. Adjacent build: employer-funded non-custodial ledger, one employer. Smallest pilot: one factory, employer float, no app loan book.

## 7. Claims you may not make yet
national_rollout, capital_allocation, board_reporting, partnership_claims non-authorized. **Any lending/credit claim stays blocked** while CBN licensing status is UNKNOWN; mandatory verification task added. The non-custodial employer model must be legally reviewed before "compliant" is ever claimed.

## 7A. Evidence still missing
| Lane | Minimum | Why |
|---|---|---|
| worker (beneficiary) | >=100 | Draw demand + repayment-at-payday reality |
| employer (guardian) | >=2 | Will an employer fund the float? |
| CBN status / legal review | verified (authority-grade) | Unlocks any lending/compliance claim; UNKNOWN = blocked |

## 8. Settlement (written before build)
- **t+90d:** one factory runs employer-funded draws + payday reconciliation for two full pay cycles with zero app-held loan balance and clean reconciliation.
- **t+365d:** the employer renews and a second employer signs on the strength of it.
- **Settlement metric:** clean payday reconciliation rate across cycles at one employer (instrumented; any app-held loan balance = structure breached).
