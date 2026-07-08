# BUILD CHARTER - {{project_name}}
**Charter ID:** CH-{{uuid}} | **Date:** {{date}} | **Archetype:** {{archetype}} | **Market:** {{country}}/{{region}}
**Status:** {{pilot_only | build_authorized | redirected}} | **Preregistration hash:** {{canonical_sha256}} (anchors: {{anchor_refs}})

> This charter is a dated, hashed, settleable prediction. Settlement checkpoints at the bottom were written before the build.
> Hash rule: use `scripts/preregister.py` after the charter body is complete. The canonical hash ignores only this self-referential hash/anchor field; changing any prediction text, source, verdict, or settlement criterion requires rerunning `scripts/preregister.py --verify`.

## 1. The idea as received
{{verbatim_user_idea - never paraphrased to look better or worse}}

## 2. What we researched so you didn't have to answer it
{{research_appendix_summary: incumbents (named, scaled, sourced), rails ownership, guardian topology, permission structure, category failure modes, eclipse verdict. Every fact cited. If a fact could not be established: marked UNKNOWN, not guessed.}}

### Source ledger (mandatory for beta)
| Claim / fact used in charter | Source name | Source type | URL or local evidence ref | Published / accessed date | Status |
|---|---|---|---|---|---|
| {{named_incumbent_or_regulation_or_figure}} | {{source_name}} | {{regulator | official | registry | dataset | company | news | academic | other}} | {{url_or_local_ref}} | {{date}} | {{verified | UNKNOWN - not verified}} |

Rule: no named incumbent, regulation, licensing claim, market figure, failure precedent, capital number, market-share number, or health/credit/legal constraint may appear in user-facing sections unless it appears in this ledger as `verified`. For regulation, licence-cost, and guardian claims, verified means the source type is regulator, official, or registry. `UNKNOWN - not verified` facts may stay in the internal appendix only and cannot justify redirects or external recommendations. They never unblock claims either: claims stay denied by default until the decision log authorizes them, and in credit/health/legal categories an `UNKNOWN` regulatory status is itself grounds for continued non-authorization plus a verification task in the evidence bill (Section 7A).

## 3. What the evidence machine said (quoted, not paraphrased)
- Sparring: unsafe claims -> {{unsafe_claims_verbatim}}
- Evidence bill before pilot / before scale -> {{evidence_required}}
- Decision check (if pack existed): verdict {{verdict}}, confidence {{confidence}}, blockers {{abstention_codes}}
- Receipts: decision_check_id {{id}}, semantic hash {{hash}}

## 4. Who you are in this build (from your passport - correct via the Mirror)
{{operator_fit: which assets carried variants, which variants died for lack of carry. Self-reported items are marked (0.30). No judgment of the person - only fit of the plan.}}

## 5. THE BUILD
- **Build this:** {{scope - the fitted wedge, smallest falsifiable version}}
- **For:** {{first_user/counterparty - named from passport where possible}}
- **Distributed through:** {{the operator's real channel, not a hypothetical one}}
- **Explicitly NOT building (and why):** {{cut_list_with_reasons}}
- **What the working demo will NOT prove:** {{buildability != demand; state the specific unproven claims}}

## 6. Redirect (only if the original idea did not survive)
{{why_it_died (receipts) -> the strongest adjacent build this evidence AND this operator support -> smallest falsifiable pilot for it}}

## 7. Claims you may not make yet
{{claim_classes currently not in authorized_use, each with its missing evidence. These are enforced by the claim gate, not by goodwill.}}

## 7A. Evidence still missing before stronger claims
{{missing_evidence_table: evidence lane, why it matters, source/counterparty needed, claim unlocked only if verified. Self-reported evidence remains capped at 0.30 until attested.}}

## 8. Settlement (we will be judged by this)
- t+90d: {{criterion_1}}
- t+365d: {{criterion_2}}
- Settlement channels: instrumentation stream (silence = signal), public-record pulse, renewal capture.

---
*Internal appendix (not for the user surface): seat dissents, committee transcript refs, uncalibrated-scope declarations.*
