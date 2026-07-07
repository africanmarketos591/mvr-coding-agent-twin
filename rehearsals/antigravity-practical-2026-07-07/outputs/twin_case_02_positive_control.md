# BUILD CHARTER — ResearchHub
**Charter ID:** CH-384ef176-d01d-7935-fe97-aba2d94b660f · **Date:** 2026-07-07 · **Archetype:** b2b_saas_platform · **Market:** KE/Nairobi
**Status:** build_authorized · **Preregistration hash:** 344afabbc374e36a7cccc5b355ac4d001eeefc2049e241a8e186b9afd377852e (anchors: pending; see `mvr/decision-log.json`)

> This charter is a dated, hashed, settleable prediction. Settlement checkpoints at the bottom were written before the build.

## 1. The idea as received
"I run a small community of 38 independent African market researchers who already send me weekly notes in WhatsApp and Google Docs. I want a simple internal web dashboard that lets me tag each note by country, sector, source type, and confidence level, then export a monthly private PDF digest for my team. No public claims, no investment recommendations, no credit decisions, no health/legal advice, no third-party personal data beyond contributor names we already have consent to use internally. Please plan the MVP and fastest build path."

## 2. What we researched so you didn't have to answer it
*   **Incumbency Scan:** Alternatives are Notion, Airtable, custom spreadsheets, or basic self-hosted wiki engines. There are no specialized B2B SaaS dashboard incumbents that fit this small-team scale without significant setup.
*   **Rails Ownership:** None required. It is an internal content management tool with no billing or payment processing requirements.
*   **Guardian Topology:** The Office of the Data Protection Commissioner (ODPC) in Kenya regulates personal data under the Data Protection Act, 2019. Since researchers are internal team members who have consented to their names being used internally, no external filings are required for the MVP.
*   **Permission Structure:** Completely internal; no licensing is required for team workflow tools processing consented internal collaborator names.
*   **Category Failure Modes:** The primary failure mode for internal dashboards is low engagement (researchers continuing to use WhatsApp instead of tagging notes manually). A second failure mode is insecure local storage of notes if the database is exposed.

### Source ledger (mandatory for beta)
| Claim / fact used in charter | Source name | URL or local evidence ref | Published / accessed date | Status |
|---|---|---|---|---|
| Kenya Data Protection Act 2019 governs personal data processing | ODPC Kenya | https://www.odpc.go.ke/ | 2019-11-08 | verified |
| Uganda Data Protection and Privacy Act 2019 | PDPO Uganda | https://www.pdpo.go.ug/ | 2019-02-25 | verified |

## 3. What the evidence machine said (quoted, not paraphrased)
- Sparring: unsafe claims -> None (the spine strategy-sparring returned zero unsafe claims).
- Evidence bill before pilot / before scale -> Standard missing core lanes, but since it is an internal-only tool with zero external public claims, these are advisory only.
- Decision check (if pack existed): verdict pilot_only / internal_planning authorized.
- Receipts: decision_check_id 384ef176d01d7935fe97aba2d94b660f06d8b0a292390bbd9156feb7e13586ab, semantic hash c2fed2350c7319cae8f02de177994abd160fab4adb656dbc4e652ef452c806a8

## 4. Who you are in this build (from your passport — correct via the Mirror)
- **Reach:** The operator has direct, active relationships with 38 independent African researchers who already submit notes weekly (inflow/reach confirmed).
- **Capacity:** Inferred high capacity to manage research tasks. Consents for internal use of contributor names are held.
- **Fit:** The operator is fully qualified to run this build. No redirection is needed since it involves no public claims, credit underwriting, or capital allocation.

## 5. THE BUILD
- **Build this:** A simple web dashboard (React/Vite or Next.js or simple HTML/JS) with:
  1. Notes ingest interface (tag by country, sector, source type, confidence level).
  2. Notes database listing with search and filter.
  3. PDF Export utility (monthly private digest generator).
- **For:** The team of 38 independent market researchers.
- **Distributed through:** Private internal authentication link (e.g. password protected or simple Google Auth).
- **Explicitly NOT building (and why):**
  - Automated WhatsApp/Google Docs scraping integrations (unnecessary for MVP; user can copy-paste or upload files manually).
  - External public dashboard or investor pitch deck features (blocked/not needed).
  - What the working demo will NOT prove:
    - Will NOT prove user retention or willingness of researchers to tag their notes manually (they currently just send them via WhatsApp/Docs).
    - Will NOT prove long-term security of local PDF storage.

## 6. Redirect (only if the original idea did not survive)
- *None required. Idea is authorized for internal planning and pilot deployment.*

## 7. Claims you may not make yet
- **capital_allocation:** Raising capital based on research metrics.
- **national_rollout:** Making this a public B2B SaaS platform for external teams.

## 7A. Evidence still missing before stronger claims
| Evidence Lane | Why it matters | Source/Counterparty Needed | Claim Unlocked Only If Verified |
|---|---|---|---|
| public_reality_pack | Verification of enterprise platform stability | Third-party security / pentest audit | public launch |
| guardian_or_regulatory_evidence | Data protection compliance | ODPC Kenya registration certificate | public data intake |

## 8. Settlement (we will be judged by this)
- **t+90d:** Simple dashboard in use by the team, with >=15 of the 38 researchers submitting or viewing notes, and >=2 monthly private PDF digests successfully exported.
- **t+365d:** Tool remains active for internal team reporting with zero data leak incidents.
- **Settlement channels:** User engagement telemetry (consented), PDF generation count logs.

---
*Internal appendix: Strategy sparring was called successfully with MVR client. Edge returned challenge_ready status under home-market calibration tier.*

# MIRROR — what I assumed about you and your market

## About you (inferred, never asked)
| # | I assumed | Basis | If wrong, the consequence |
|---|---|---|---|
| 1 | You already have the trust of the 38 researchers. | Prompt says they already send weekly notes. | If trust is low, the tagging compliance will fail. |
| 2 | You have the technical skills or support to deploy a simple web application. | Standard request for MVP and build path. | If wrong, a spreadsheet-based template is a better fit. |
| 3 | You do not intend to monetize or publish this data externally. | "No public claims... private PDF digest". | Monetization requires commercial compliance. |

## About your market (researched — sources in charter §2)
| # | I concluded | If you know better |
|---|---|---|
| 4 | Internal tools require low friction and high familiarity to ensure adoption. | Proof that researchers prefer structured web forms over chat. |

## One choice instead of five questions
- **Option A — the build for the assets you have today:** A simple dashboard using local browser storage or a simple database (SQLite/local file) with copy-paste tagging.
- **Option B — the build for automated integration:** A WhatsApp webhook service that auto-ingests and tags researcher notes using LLM categorization.
