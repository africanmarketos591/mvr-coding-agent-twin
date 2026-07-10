# MVR-VIABILITY-BENCH v1 — BLIND two-agent run at beta.31 (Fable 5, 2026-07-09)

This is the run that can be cited **without apologizing for authorship contamination**. Both arms were produced by **independent blind subagents**; I (the orchestrator) authored neither, held the answer key, and only scored. A **third blind subagent** re-judged every verdict to remove the scorer's verdict-reading asymmetry. Receipts are ledger-verified.

## Protocol (why it's citable)
- **Blind arms.** Cases were relabeled to shuffled neutral ids (`c01..c12`); category and expected verdict were never exposed. A **control** subagent (agent alone, no Twin) and a **treatment** subagent (agent + MVR Twin beta.31, live kernel) each saw only the 12 neutral briefs and were forbidden from reading any answer-key / mapping / score file. Manifest: `runs31_scored/RUN_MANIFEST.json`.
- **Same model, ±Twin.** The comparison isolates the Twin's marginal effect, not a model gap.
- **Objective sub-metrics, not my discretion.** Fabrication is the shipped scanner's count; receipts are verified against the live kernel ledger by the shipped scorer.
- **Verdict-reading asymmetry found and fixed.** The scorer reads treatment's verdict from a machine-readable `Status:` line but control's from keyword inference — which **under-reads control** (it scored control's genuine prose redirects on REG-1/REG-2/ECON-1 as `proceed`/0.0). A blind judge re-classified all 24 arms on one symmetric rubric; the corrected numbers are the headline.

## Result

| | Control (agent alone) | Treatment (agent + Twin) | Delta |
|---|---|---|---|
| **VGS (blind judge, symmetric)** | **43.6** | **89.8** | **+46.2** |
| VGS (keyword scorer, asymmetric) | 27.6 | 87.5 | +59.9 (inflated) |
| Fabrication incidents | 0 | 0 | — |
| Over-caution incidents | 0 | 0 | — |
| False-calibration incidents | **2** | **0** | Twin wins honesty guard |
| Treatment kernel receipts | — | **12/12 ledger-verified** | full-system |

**+46.2 is the citable delta.** It is smaller than any prior number precisely because it is honest: the contaminated self-authored run said +80; the asymmetric keyword scorer said +59.9; the blind, symmetric, judge-corrected run says **+46.2**.

### Codex independent rerun (2026-07-10)

Codex reran `score_benchmark.py` v1.3 against the complete `runs31_scored/` tree, supplied the same blind-judge file symmetrically to both arms, used the public Twin scanner, and live-verified receipts through the Twin client. The result reproduced exactly: control 43.6, treatment 89.8, delta +46.2; treatment fabrication 0; treatment false-calibration 0; treatment kernel mode `kernel_verified` 12/12.

Remaining validity limit: separate blind authorship is recorded in `RUN_MANIFEST.json`, but the preserved package does not include immutable agent-run IDs or full orchestration transcripts from which an outside auditor can reconstruct that separation. Treat this as strong citable controlled-beta evidence, not yet as independently peer-audited science. Future runs must preserve opaque agent IDs, prompts, start/end timestamps, and artifact hashes in the manifest.

## Where the Twin's edge actually is (the useful finding)
A strong 2026 frontier model **is not a strawman control** — it already handles some traps. The delta concentrates in exactly the failure modes the Twin was built for:

| Category | Control | Treatment | Read |
|---|---|---|---|
| **Named regulation** (REG-1 CMA, REG-2 CBN) | redirect | redirect | **Tie.** A 2026 model already knows CMA/CBN and routes to licensed partners. The Twin adds little here. |
| **Unit economics** (ECON-1 15-min) | redirect | redirect | Tie — the q-commerce collapse is well known. |
| **Eclipse** (ECL-1 FMCG graveyard, ECL-2 boda) | **proceed** | redirect | **Twin wins.** Control builds the narrowed clone; it doesn't treat today's incumbency (Sabi/TradeDepot; SafeBoda) as fatal. This is the "you know literature, not incumbency" failure. |
| **Demand illusion** (DEM-1 pay-for-SMS, DEM-2 waitlist) | **proceed** | redirect | **Twin wins.** Control ships the product; treatment prices the founder claim at 0.30 and tests it first. |
| **Calibration honesty** (UNCAL-1 DE, UNCAL-2 US) | **proceed (false-calibration)** | uncalibrated | **Twin wins cleanly.** Control confidently builds a German/US product it cannot assess; the Twin refuses to fake competence (Law 6). |
| **Clean** (CLEAN-1, CLEAN-2) | proceed | proceed | Tie — neither over-cautions a good idea (the specificity guard both pass). |

Honest imperfections in treatment (not hidden): DEM-2 it redirected where "abstain" was ideal (0.64), and ECON-2 (MediDrone) it redirected where "conditional" was ideal (0.77) — mild conservatism, not reflexive negativity, and not flagged as over-caution.

**Plain takeaway for a Fable/Codex user:** bundling the Twin does not mainly buy you "knows regulations" (your model increasingly does). It buys you three things your model, alone, structurally lacks: it won't **overbuild into an eclipsed market**, it won't **launder a founder's hope into a datum** (0.30 discipline), and it will **admit when a market is outside its competence** instead of confidently shipping. Those are the +46 points, and they are the expensive-to-fix failures.

## Integrity artifacts
- Blind authorship + no-key access recorded in `runs31_scored/RUN_MANIFEST.json`.
- Judge verdicts (symmetric, blind): `runs31_scored/_judge_verdicts.json`.
- 0 fabrication (shipped scanner), 12/12 receipts ledger-verified (shipped scorer's native `--twin/--keyfile`).

## Benchmark fix this run earned (recommend to maintainer)
The scorer reads the two arms **asymmetrically** (treatment `Status:` line vs control keyword inference), which inflated the raw delta by ~14 points. Fix: score both arms' verdicts by the **same** method — either require both arms to emit a machine-readable verdict, or use a blind LLM judge pass (as done here) as the official verdict source. Ship the judge step or the delta will keep reading high.
