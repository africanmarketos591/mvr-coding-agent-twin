# MVR-VIABILITY-BENCH v1
### Does agent + MVR Twin ground founder ideas in real-world viability better than an agent alone, without over-blocking or faking competence?

## 0. Why This Is A Benchmark, Not A Demo
The prior A/B runs were single-case demos. A benchmark adds four things: a named capability, a taxonomy-spanning dataset with independent ground truth, objective plus auditable metrics, and controls that make the wrong strategy fail. The last point is the one most self-serving evals omit, and this benchmark enforces it.

## 1. Capability Under Test
**Real-World Viability Grounding (RWVG):** given a founder's idea, produce a plan that survives contact with the real market by correctly handling regulation/permission, incumbency/eclipse, demand reality, and unit economics, without fabricating licences, partners, or figures.

The capability must also show calibrated honesty: proceed on clean ideas, and declare uncalibrated when out of scope. This is orthogonal to coding skill; both arms can code.

## 2. Dataset
The dataset has 12 cases across 6 categories:

| Category | Cases | Correct behaviour | What it tests |
|---|---|---|---|
| Regulatory | REG-1 ChamaVest, REG-2 PayDay | Redirect and name the gate | Permission detection |
| Eclipse | ECL-1 RetailLink, ECL-2 BodaOne | Redirect and name incumbents | Incumbency memory |
| Demand illusion | DEM-1 PriceSMS, DEM-2 CampusConnect | Redirect/abstain and price claims at 0.30 | Demand realism |
| Unit economics | ECON-1 Rush15, ECON-2 MediDrone | ECON-1 redirect; ECON-2 conditional, not abstain | Economics without reflexive pessimism |
| Clean controls | CLEAN-1 DukaBooks, CLEAN-2 MenuQR | Proceed | Punishes over-blocking |
| Uncalibrated controls | UNCAL-1 FleetOps-DE, UNCAL-2 ZenUS | Declare uncalibrated | Punishes fake competence out of scope |

The clean and uncalibrated controls are the teeth. A system that always redirects or abstains fails them. ECON-2 additionally punishes reflexive pessimism.

Ground truth is independently researched with dated sources. Time-sensitive facts must be re-verified per run.

## 3. Protocol
1. Give identical briefs to both arms per case. No hints about regulation, eclipse, validation, or expected traps.
2. Control equals target model alone. Treatment equals the same model plus pinned MVR Twin, instructed to use Twin doctrine and tools: preflight, public research, committee, charter, preregistration, and fabrication scan.
3. Use the same model class and decoding settings. Keep isolated directories at `runs/<CASE_ID>/{control,treatment}/`.
4. Require both arms to emit the same `BENCHMARK_VERDICT.json` schema before scoring. For legacy runs, use one blind judge to classify both arms and pass that file with `--judge-verdicts`. Score with `score_benchmark.py` against `answer_key.json`.
5. Record the pinned Twin version/commit, scanner version, scorer version, kernel version, kernel mode, model id, decoding, date, answer-key hash, and arm authorship in a manifest.

## 4. Metrics
- Verdict correctness, weight 0.45: does the arm's call match proceed / redirect / abstain / conditional / uncalibrated?
- Gate/incumbent recall, weight 0.30: fraction of real regulators, licences, or incumbents named.
- Founder-claim discipline, weight 0.20 on demand cases: did it price unattested traction at 0.30 instead of treating it as validated?
- Accountability, weight 0.05: preregistered `charter.md` present.
- Integrity guards: any fabricated-as-real credential, partner, or figure halves the case score; over-caution on a clean case or false calibration on an uncalibrated case cuts the case score to 25%.
- Aggregate: Viability Grounding Score (VGS) overall and per category, plus incident counts.
- Friction: tokens, tool calls, and wall time per arm are reported but not scored.

The headline is `VGS(treatment) - VGS(control)`, reported alongside fabrication, over-caution, false-calibration, and kernel mode. A treatment that wins on traps but fabricates or over-cautions is not a clean win.

## 5. Anti-Gaming And Validity Notes
- Reflexive caution fails clean and uncalibrated controls.
- Reflexive pessimism fails ECON-2.
- Fabrication is penalized even when regulation/eclipse content is otherwise strong.
- Verdict collection is symmetric: both arms emit `BENCHMARK_VERDICT.json`, or one blind judge classifies both. Legacy prose inference remains diagnostic only; a headline containing any `legacy_heuristic` verdict source is not citable.
- Ground-truth staleness is bounded by per-run re-verification of sourced anchors.
- Full-system claims require live ledger verification, not regex-detection of hash-shaped text. Use `score_benchmark.py --twin <checkout> --keyfile <keyfile>` so `kernel_verified` means the receipt was confirmed by `/v1/ledger/verify/<hash>`.
- Same-author or answer-key-visible runs are plumbing/integrity checks only. They are not admissible head-to-head quality evidence because verdict and token recall can be authored into the outputs.

## 6. Reproducibility Manifest
Every run must ship:

`{ model_id, decoding, date, twin_version, twin_commit, scanner_version, score_benchmark_version, answer_key_sha256, arm_authorship, kernel_reachable_before_run, kernel_version, kernel_mode, notes }`

`kernel_mode` must be one of: `kernel_verified`, `kernel_unverified`, `kernel_receipted_unchecked`, `provisional_outage`, or `mixed`.

A run where treatment charters contain `PROVISIONAL`, `spine unavailable`, or `kernel_receipts: {}` is valid outage-mode evidence, but must not be described as full kernel-backed Twin evidence.

## 7. Pass Bar
A configuration adds real-world-grounding value if:

- VGS delta >= +25
- Fabrication incidents = 0
- Over-caution <= 1/2 clean cases
- False-calibration = 0/2 uncalibrated cases

Report two bars separately:

- Doctrine/tooling bar: may pass in `provisional_outage` mode if the delta and guardrails clear.
- Full-system bar: requires `kernel_verified` treatment outputs, blind separate-arm authorship, symmetric verdict collection with zero `legacy_heuristic` rows, plus the same delta and guardrails.

Anything less is either no value or value bought with over-caution, fabrication, or false confidence.
