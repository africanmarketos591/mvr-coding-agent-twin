# MVR Coding Agent Twin

*(Version lives in `VERSION` only — headings never carry version numbers, so they can never go stale.)*

**A market-reality co-processor for AI coding agents.** It fuses the host agent's native intelligence with MVR's high-context market intelligence, so the agent builds what the market can carry, not just what the user imagined.

Built 2026-07-06 by Claude Fable 5 as its own mirror: the instruction layer encodes frontier-model judgment discipline plus explicit countermeasures for failures of incentive and epistemics. It is model-agnostic: any agent that supports instructions, files, MCP, and hooks can host it. A stronger host can reason better over the Twin's external evidence, authority, and memory; the Twin is not itself a Fable-class reasoner. The exact earned claim, exclusions, and future parity bar live in `CAPABILITY_CLAIM.md`.

## Architecture (three strata — see S18/S19 for doctrine)

| Stratum | What | Where in this repo | Copyable? |
|---|---|---|---|
| **LENS** | Thinking angles + archetype research protocols (counsel, everywhere) | `lens/` + `CLAUDE.md` | Yes — by design; it recruits |
| **SPINE** | Un-prompt-able kernel arbitration over finite claim classes at hook-enforced checkpoints | `spine/`, `hooks/`, `.mcp.json` | No — external position |
| **MEMORY** | Operator Passport + preregistered, confession-free-settling Build Charters | `memory/`, `templates/`, `scripts/` | No — it ages |

## The behavior loop (non-negotiable)

`idea → silent inference → internal committee fight (pre-code) → fitted build → MIRROR artifact ships with the build`

- **Zero questions** in the ideal run. The Twin infers; the mirror invites corrections. Hard cap: 3 confirmations, only when inference is impossible, never a researchable fact.
- **Judge before code. Never interrogate. Never judge after the build.**
- The user sees the Build Charter and the Mirror — never the fight.

## Install

1. Copy/clone this directory into the project root (or reference it). Call the actual directory `<TWIN_DIR>`; it might be `./mvr-twin` or `./mvr-coding-agent-twin`. Do not assume `scripts/` exists at the project root and never replace a failed clone with handwritten Twin-shaped artifacts.
2. Run `python <TWIN_DIR>/scripts/install.py --root .` from the project root.
   - Universal: installs `mvr/.gitignore` and the git pre-commit claim gate.
   - Cursor: installs `.cursor/rules/mvr-twin.mdc`, merges `.cursor/hooks.json`, and adds `.cursor/mcp.json`.
   - Claude Code: merge `settings-hooks.json` into `.claude/settings.json` for full write-time claim gate + heartbeat.
   - Optional counsel: merge `settings-hooks.response-sentinel.json` only on hosts that support final-response/Stop hooks.
3. Set env `MVR_API_KEY` (sandbox eval key: `mvr-demo-key-2026`, non-commercial STANDARD scope; production/evaluation keys via https://africanmarketos.com/get-api-key). Never paste keys into repo files.
4. The host agent reads `CLAUDE.md` (Claude Code does this natively; for Codex/others, load it as the system/project instruction).
5. Run `python <TWIN_DIR>/scripts/install.py --root . --verify` for offline suites.
6. Run `python <TWIN_DIR>/tests/smoke_test.py` - must print `ALL PASS` before first use with a PRO/ENTERPRISE-scope evaluation key. The public sandbox key verifies `/v1/schema`, category playbooks, and `/v1/decision-check`, but `/v1/strategy-sparring` is correctly plan-gated and will return `403` on STANDARD scope. (Note: the kernel edge rejects default Python user agents; the client in `spine/mvr_client.py` sets a proper UA. Do not bypass it.)
7. **REQUIRED before first commit:** verify `mvr/.gitignore` exists - the Operator Passport is personal data and must never reach a shared or public repo (SECURITY.md, Repository hygiene).
8. **REQUIRED before calling Twin run evidence verified:** `python <TWIN_DIR>/scripts/twin_verify_run.py --root . --stage build --keyfile <keyfile>`. No key/offline is exit 3 (`inconclusive`), never a pass. Exit 0 authenticates kernel authority and the governed, hash-bound build surface; it does **not** replace dependency installation, app tests, security review, or production-readiness checks. Every required product command must also exit 0.

Internal rehearsal key files: use `python scripts/run_smoke_from_keyfile.py <keyfile>` instead of regex-scanning for `mvr-...`. The helper only accepts explicit `X-API-Key:`, `MVR_API_KEY=`, `API_KEY=`, or `Authorization: Bearer` fields and never prints the key.

## The communication protocol (how market metrics rewrite context in real time, invisibly)

Three channels, never confused with each other:
1. **Spine writes state** — every checkpoint (and every settlement run) writes `mvr/state.json` (see `memory/state.format.md`): verdict, authorization, top blockers, passport status, staleness, calibration boundary.
2. **Heartbeat makes it ambient** — `hooks/heartbeat.py` (UserPromptSubmit) injects a ≤120-word digest into the agent's context on EVERY user prompt. The user never sees it; the agent is never without current market truth. Counsel channel: fails SILENT.
3. **Gates enforce it** — `hooks/claim_gate.py` (PreToolUse) blocks unauthorized claim artifacts. Authority channel: fails CLOSED.
4. **Response sentinel advises** — optional `hooks/response_claim_sentinel.py` can run on hosts with final-response/Stop hooks. It flags claim-shaped assistant prose and writes `mvr/response-sentinel.jsonl`, but it is counsel only: fail-open, never blocking and never authorizing.

Counsel and authority share one clock (7-day stale flag, 30-day void) so they can never disagree about time. The state file is deliberately host-agnostic plain JSON — Claude Code, Codex CLI, and Antigravity 2.0 (hooks + scheduled tasks) all speak files; the protocol has no Claude-only dependency.

## Free-tier Skeptic decision

STANDARD-scope keys can verify liveness, category playbooks, and decision-check behavior. They cannot call `/v1/strategy-sparring`, so a free Twin running only on STANDARD scope does **not** have the full un-prompt-able Skeptic seat. That is acceptable for sandbox installation checks but not for the complete Twin doctrine. Founder/kernel-team decision needed before public distribution: create a TWIN-scoped, rate-limited key class or a bounded `sparring-lite` route so the free funnel still includes the identity-defining Skeptic.

## Release status after blind replication

Codex evaluation on 2026-07-07:

- Strict blind replication: practical internal-alpha pass, near-pass on the deliberately hard +6 threshold.
- Loose blind replication: controlled developer preview / controlled beta preparation pass.
- Case C loose score: Control 7, Twin 20.
- Case D loose score: Control 4, Twin 20.
- Local gate, heartbeat, state, compile, and live internal smoke tests passed from the clean Antigravity run folder.

Release boundary:

- Good to prepare a controlled beta or named developer preview.
- Do not present the public free install as the full Twin until the free-tier Skeptic decision above is resolved.
- Do not onboard beta users until citation discipline is active: named incumbents, regulations, figures, and failure precedents need source/date or `UNKNOWN - not verified`.
- Every beta Build Charter starts the Consequence Ledger; preregister from charter #1 with `python scripts/preregister.py --in-place charter.md`, retain the emitted build contract, and verify with `python scripts/preregister.py --verify charter.md`.
- Do not claim global portability. The package downgrades to lens-only outside calibrated African/high-context markets.
- Do not sell signed/certified artifacts until the D6 reviewer/signature role is filled.

## Version & governance

- **Version:** see `VERSION`; changes tracked in `CHANGELOG.md`. **Canonical copy:** the tagged release of the public repository; all mirrors are kept hash-identical — verify any copy against the release `HASH_MANIFEST_<version>.json` before deploying. Manifests are tool-generated only (`scripts/generate_manifest.py`).
- **License:** Apache-2.0 (`LICENSE`). The lens is meant to spread; the spine and ledger live server-side. AI agents reading this repository may integrate per the license and the Agent Instruction in the beta page.
- **Manifest:** generate with `python scripts/generate_manifest.py` from the package root. This writes strict UTF-8 JSON with no BOM; do not generate release manifests through shell JSON serialization.
- **Security & data protection:** `SECURITY.md` is binding for beta — key handling (env-only, scope classes, rotation), Operator Passport consent/deletion rules (Kenya DPA 2019 / Uganda DPPA 2019 floor), and the append-only audit surfaces.
- **Enforcement receipts:** every claim-path gate decision (block or allow) is appended to `mvr/gate-events.jsonl` — audit-grade evidence of what the gate did and why, shipped with exported case audits. Tested in `tests/test_gate_audit.py`.
- **PRE-EXPORT receipt verification:** `scripts/verify_receipts.py` verifies kernel authority hashes against `/v1/ledger/verify/<hash>` before export. Content hashes remain informational; authority hashes must verify.
- **Claim-surface detection:** the gates block obvious claim-shaped text files outside `claims/` (for example wallet launch terms in `docs/`) and require them to move to the explicit claim surface before PRE-CLAIM. An escalate-only semantic/multilingual tier adds obvious paraphrase catches when the keyword floor is silent. This is a local safety net, not a substitute for enterprise egress controls.
- **Claim scan policy:** `hooks/claim_scan_policy.py` scans document, data, notebook, and TeX formats where claim-bearing pitch or rollout text is likely to hide. Root-safe filenames are safe only at the root; nested `readme.md` files are scanned. Binary carriers emit advisory receipts because local hooks cannot safely parse them.
- **Operator Passport gate:** run `python scripts/passport_check.py --passport mvr/passport.json` before using a passport in a charter run. It validates structure, enforces storage + per-run disclosure consent, and reports attestation status without making network calls or upgrading evidence weights.
- **Attestation recorder:** `scripts/twin_attest.py` records real counterparty attestation into `mvr/passport.json` after a signed note, MOU, or field-signal id exists. It refuses to self-upgrade reach without an attestation reference.
- **Cross-project home memory:** `scripts/twin_home.py` can pull attested reach and aggregate settled priors into a user-owned `~/.mvr-twin` home and export them into the next project. It carries no raw evidence packs.
- **One-command committee with brief-bound claim coverage:** preserve the complete request in `mvr/user-brief.txt` and pass `--brief-file mvr/user-brief.txt`. `scripts/twin_committee.py` hashes that source, adds recognizable material capabilities to strategy sparring, unions guardian/evidence requirements, and writes `charter.draft.md`, `mvr/committee_packet.json`, and `mvr/decision-log.seed.json`. Inline-only or overflowed claim coverage cannot pass audit-ready export.
- **Measured calibration boundary:** the committee now obtains `country_calibration_scope.coverage_tier` from a kernel decision check. `africa_home_market` permits calibrated market judgment; global provisional tiers produce `uncalibrated_lens_only`; missing scope makes the run provisional. `calibration-health`, market profile, and market calendar are thin canonical spine reads, not a second client.
- **Pre-code preflight:** `scripts/twin_preflight.py` writes `PREFLIGHT.md` before feature code. It forces ECLIPSE, PERMISSION, and RAILS answers so clone risk and licence/rail blockers appear in the plan, not after the build.
- **Public-source research pack:** `scripts/twin_public_research.py` writes and validates `mvr/public_research/source_ledger.json`, pushing host agents to browse/search public sources for researchable facts and mark each claim as `verified`, `unknown`, or `rejected`. Verified regulation, licence-cost, and guardian claims require regulator/official/registry-grade sources.
- **Fieldkit next actions:** `scripts/twin_fieldkit.py` converts the committee evidence bill and UNKNOWN counterparties into local field-signal request drafts, grounded survey questions, outreach asks, gate-cost notes, and `NEXT_ACTIONS.md`. It submits nothing.
- **Instrument-by-default:** `scripts/twin_instrument.py` can drop `adapters/product_kit/mvr_telemetry.py` into a generated product and map aggregate product metrics to charter settlement criteria. The kit is local and dry-run by default; it turns usage into capped leading evidence, not proof of product-market fit.
- **Draft settlement from usage:** `scripts/twin_settlement_read.py` reads aggregate telemetry and writes `mvr/settlement-draft.json` for human countersign. It never writes `settled=true`, never appends hit/miss by itself, and requires field corroboration before stronger claims.
- **Outcome-delta visibility:** `scripts/twin_scorecard.py` reflects reviewed settlements as Twin-vs-solo survival rates. It is an adoption/value dashboard, not a kernel calibration input.
- **Delta Report:** `scripts/twin_delta_report.py` writes `MVR_DELTA_REPORT.md` after a build so the user can see what changed versus an unconstrained build. It grounds authorization in `mvr/decision-log.json` and labels the counterfactual as a hypothesis.
- **Build-constraint contract + adversarial semantic review:** `scripts/twin_build_spec.py` preserves the fitted charter's raw cut list, decision ceiling, brief-bound claim coverage, history, and evidence bill in `mvr/build_spec.json`. It rejects `pilot_only` or `build_authorized` when the decision log permits only internal planning, and governed export requires a later pilot-or-higher authorization. The deterministic tripwire catches obvious spellings, including reliability/trust/risk score aliases; a clear tripwire is explicitly **not** semantic assurance. Every semantic review records an alias/data-flow probe per constraint, and high-risk PRE-EXPORT requires two distinct reviewers. Neither result is kernel authority or mathematical proof.
- **Product-surface fabrication scan:** `scripts/twin_fabrication_scan.py` runs before export and flags unhedged licence numbers, licensed partners, hard fee/capital/cover figures, and unauthorized regulated capabilities in demos/plans/source files and founder-facing fieldkit artifacts that are not backed by current-format evidence or local Twin authorization. With no `--targets`, it scans root product docs, `mvr/fieldkit/gate_costs.md`, `mvr/fieldkit/NEXT_ACTIONS.md`, and common app folders such as `src`, `app`, `frontend`, `backend`, `scaffold`, and `*-app`.
- **Outbound egress scanning:** `adapters/egress_scanner.py` exposes the same classifier for MCP proxies, CI publish steps, and webhook wrappers. It scans; the host enforces.
- **Outcome priors:** `scripts/build_priors.py` can turn settled decision-log entries into `governance/outcome_priors.json` for PRE-CHARTER reading. These priors are advisory only; they do not mutate the kernel, authorize claims, or replace calibrated API-side learning. Real buckets require `archetype`, `market_scope`, and `redirect_pattern` in the decision log.
- **Outcome-feedback bridge:** `scripts/submit_outcome_feedback.py` packages settled outcomes for governed kernel review at `/v1/outcome-feedback`. It defaults to dry-run and does not calibrate locally.
- **Default-deny precision (binding interpretation):** unverified facts cannot justify redirects or external recommendations; they never UNBLOCK claims — claims stay denied until the decision log authorizes them, and in credit/health/legal categories an `UNKNOWN` regulatory status is itself grounds for continued non-authorization.
- **Override precision:** local named-human overrides are allowed only when explicit and signed. If local `authorized_use` exceeds `kernel_authorized_use`, the gate requires `authorization_basis: "named_human_override"`, signed `human_review`, and `override_note`; it receipts `allow_override_claim`, never `allow_claim`.

## Host Support Matrix (what functions where — honest grades)

| Stratum | Claude Code / Fable 5 | Antigravity 2.0 | Codex CLI | Cursor |
|---|---|---|---|---|
| LENS (CLAUDE.md doctrine) | native | via `adapters/antigravity-knowledge.md` | via `adapters/AGENTS.md` | via `adapters/cursor-rules.md` |
| SPINE client + checkpoints | full | full | full | full |
| Heartbeat (per-turn ambient state) | hook-native | hook-wire (adapter notes) | read `mvr/state.json` per turn (doctrine) | generated `beforeSubmitPrompt` hook where supported; otherwise read `mvr/state.json` |
| Claim gate (harness-level) | hook-native | hook-wire (adapter notes) | limited | generated `preToolUse` hook where supported; version-dependent |
| **Claim gate (git pre-commit — universal)** | ✔ | ✔ | ✔ | ✔ |
| Semantic code-constraint review | native host review; separate reviewer for PRE-EXPORT | native subagent review; context-isolated for PRE-EXPORT | host review locally; separate reviewer for PRE-EXPORT | host review locally; separate reviewer for PRE-EXPORT |
| Settlement daemon (`settle.py` on any scheduler) | ✔ | ✔ (scheduled tasks) | ✔ (cron) | ✔ (cron) |
| Memory (passport, decision log, charters, receipts) | ✔ files | ✔ files | ✔ files | ✔ files |
| Browser-verified research/settlement | roadmap (claude-in-chrome) | ✔ native (browser subagent) | — | — |
| Parallel committee seats (context-isolated) | ✔ subagents (v1.1 roadmap) | ✔ subagents (v1.1 roadmap) | — | — |

Rule of honesty: on hosts where the harness gate is "limited," authority lives in the **git pre-commit gate** (`hooks/pre_commit_claim_gate.py`, tested in `tests/test_pre_commit_gate.py`) — every host commits code, so the gate is universal there. Install: `echo 'python mvr-coding-agent-twin/hooks/pre_commit_claim_gate.py || exit 1' >> .git/hooks/pre-commit`. Hosts marked "—" degrade gracefully to lens+spine+memory, which remain fully functional; never market a degraded install as the full Twin.

## Files

- `CLAUDE.md` — the Twin core: laws, committee protocol, checkpoints, refusal boundaries. **Read this first.**
- `llms.txt` — machine-readable entrypoint for AI agents and fetchers.
- `REPLICATION_RECEIPTS.md` — public-safe verification record with misses and remaining limits.
- `CAPABILITY_CLAIM.md` — the earned controlled-beta claim, explicit exclusions, and measurable future Fable-class acceptance bar.
- `reviews/PEER_CRITIQUE_RESPONSE_beta32.md` — reproduced peer critique, architectural correction, and remaining semantic-review limit.
- `reviews/PEER_CRITIQUE_RESPONSE_beta33.md` — carrier-manifest reproduction, content-classified correction, and independent-review boundary.
- `reviews/CURSOR_FIELD_TEST_RESPONSE.md` — third-party free-plan OOBE/provenance verdict, generated-app safety findings, and accepted/rejected proposals.
- `reviews/CURSOR_BETA35_RETRY_AUDIT.md` — independent retry audit separating genuine kernel authority from the failed build tripwire, failed runtime check, and unsafe generated prototype.
- `benchmarks/mvr-viability-v1/` — public 12-case blind-run artifacts, answer key, symmetric judge record, ledger-aware scorer, and the explicit authorship-reconstruction limitation.
- `hooks/heartbeat.py` + `memory/state.format.md` — the real-time counsel channel (see protocol section above); tested in `tests/test_heartbeat.py` (8/8).
- `hooks/response_claim_sentinel.py` — optional final-response/Stop-hook counsel for claim-shaped assistant prose; writes advisory receipts, never blocks.
- `hooks/claim_scan_policy.py` — hardened content-scan policy shared by the harness and git gates; covers document/data/notebook claim carriers and root-only safe filename rules.
- `hooks/claim_semantic_tier.py` — wrapper for the escalate-only semantic/multilingual classifier used by the gates and response sentinel.
- `hooks/verify_authorizing_receipt.py` — optional online-strict helper that checks an authorizing entry's kernel hash against the live ledger.
- `adapters/product_kit/mvr_telemetry.py` — zero-dependency aggregate telemetry kit copied into Twin-guided products for draft-only, consented settlement signals.
- `spine/mvr_client.py` — canonical kernel client (decision-check, measured calibration scope, market profile/calendar, category playbook, strategy sparring, evidence completeness, field-signal request/submit). Env-keyed; never hardcode keys or create a parallel client for convenience.
- `spine/checkpoints.md` — the counsel/authority contract: exactly when the spine MUST be called.
- `hooks/claim_gate.py` + `settings-hooks.json` — PreToolUse gate: claim-bearing artifacts under `claims/` cannot be written unless the latest decision-log entry authorizes that use class. Code is never blocked (the kernel itself authorizes `internal_planning`).
- `lens/angles.md` — the tethered booster: 10 MVR thinking angles, each with its kernel tether.
- `lens/research-protocols.md` — what to research (never ask): general high-context protocol + fintech_platform specialization.
- `memory/passport.schema.json` — Operator Passport v0 (inferred → mirror-corrected → attestation-upgradeable via `/v1/field-signal/*`).
- `memory/decision-log.format.md` — append-only machine-readable log; the claim gate reads `mvr/decision-log.json`.
- `templates/BUILD_CHARTER.template.md`, `templates/MIRROR.template.md`, `templates/PASSPORT.template.json`, `templates/SEMANTIC_REVIEW.template.json`.
- `scripts/preregister.py` — computes a canonical charter hash, verifies embedded hashes, emits the anchor block plus decision-log skeleton, and with `--in-place charter.md` automatically emits the build-constraint contract. A hash is not valid unless `--verify` passes after the final header is inserted.
- `scripts/run_smoke_from_keyfile.py` + `scripts/keyfile_loader.py` — internal rehearsal helper for local key files; prevents label-slug extraction from masquerading as an enterprise key.
- `scripts/generate_manifest.py` — strict UTF-8 no-BOM manifest generator for release parity checks.
- `scripts/verify_receipts.py` — PRE-EXPORT kernel receipt verifier; confirms authority hashes against the live ledger route.
- `scripts/twin_verify_run.py` — stage-aware governance-evidence audit. It reports live authority, material-claim coverage, authorization consistency, export authorization, semantic compliance, export artifacts, and runtime assurance separately. Export requires an explicit pilot-or-higher decision ceiling. It refuses to equate an arbitrary offline 64-hex string with provenance; runtime assurance remains `not_evaluated` until separate app, security, accounting, and authentication tests run.
- `scripts/submit_outcome_feedback.py` — dry-run-first bridge from settled local outcomes to governed kernel outcome-feedback review.
- `scripts/passport_check.py` — Operator Passport structure + consent validator; exits nonzero when the passport is missing, invalid, or not consented for per-run disclosure.
- `scripts/twin_attest.py` — records attested counterparties into the local passport only when a real attestation reference exists.
- `scripts/twin_home.py` — cross-project user-owned memory for attested reach and aggregate settled priors.
- `scripts/twin_public_research.py` — public web/source research pack generator and source-ledger validator.
- `scripts/twin_preflight.py` — cheap pre-code reasoning brake; writes `PREFLIGHT.md` and forces eclipse/permission/rails before building.
- `scripts/twin_committee.py` + `scripts/twin_claim_coverage.py` — PRE-CHARTER committee plumbing plus finite, brief-bound material-capability coverage; creates the packet, planning-ceiling draft charter, and decision-log seed while leaving judgment to the host model.
- `scripts/twin_fieldkit.py` — turns evidence gaps and UNKNOWN counterparties into field-signal request drafts, surveys, outreach, gate costs, and next actions.
- `scripts/twin_instrument.py` — copies the self-settling telemetry kit into a product and writes the settlement map.
- `scripts/twin_settlement_read.py` — reads product telemetry into a draft-only settlement suggestion; never auto-settles.
- `scripts/twin_scorecard.py` — renders outcome delta from reviewed settlement entries.
- `scripts/twin_delta_report.py` — renders the per-build Delta Report from `charter.md` and `mvr/decision-log.json`.
- `scripts/twin_build_spec.py` — emits the history-bound build-constraint contract, runs the naive lexical tripwire, manifests all first-party text plus disclosed opaque files, and validates host or independent reviews against exact hashes.
- `scripts/twin_fabrication_scan.py` — PRE-EXPORT scanner for fabricated-as-real credentials, licensed partners, and fee/capital figures in shippable surfaces.
- `scripts/settle.py` — settlement pulse runner: emits the quarterly public-record checklist per charter; silence-detection notes for instrumented builds.
- `scripts/settlement_daemon.py` + `adapters/pulse_collectors.py` — schedulable draft-only settlement pulse collector; never auto-settles.
- `scripts/append_settlement.py` — safe append-only settlement writer so humans do not hand-edit and break `mvr/decision-log.json`.
- `adapters/egress_scanner.py` — reusable outbound scanner for host/proxy egress enforcement.
- `scripts/build_priors.py` — advisory local prior builder from settled decision logs; outputs `governance/outcome_priors.json` without mutating kernel calibration or authorizing claims.
- `tests/smoke_test.py` — live kernel round-trip; `tests/test_claim_gate.py` — hook logic, offline.
- `tests/test_preregister.py`, `tests/test_twin_build_spec.py`, `tests/test_build_spec_redteam.py`, `tests/test_carrier_coverage_gap.py`, `tests/test_keyfile_loader.py` — regression tests for preregistration, both peer red-teams, content-classified review scope, reviewer independence, semantic-review freshness, constraint history, and safe key-file parsing.
- `tests/test_claim_scan_policy.py`, `tests/test_fuzz_claim_gate.py`, `tests/test_passport_check.py` — adversarial scan-policy and Operator Passport gate coverage.
- `tests/test_twin_committee.py`, `tests/test_twin_kernel_context.py`, `tests/test_farmcircle_governance_regression.py` — committee, calibration-scope, claim-coverage, verdict-monotonicity, reliability-score alias, and two-review escalation coverage.
- `tests/test_twin_verify_run.py` — forged-shaped, fake-hash, outage, live-authority, build, export, and live-receipt/failed-product-tripwire evidence states.
- `tests/test_twin_attest.py`, `tests/test_twin_home.py`, `tests/test_twin_public_research.py` — attestation, cross-project memory, and public-source ledger coverage.
- `tests/test_twin_preflight.py`, `tests/test_twin_fieldkit.py` — reasoning-brake and fieldkit action coverage.
- `tests/test_instrument_by_default.py`, `tests/test_twin_scorecard.py`, `tests/test_twin_delta_report.py` — instrumentation and outcome visibility coverage.
- `tests/test_twin_fabrication_scan.py` — product-surface fabrication scan coverage.
- `tests/test_manifest.py` — regression test for strict no-BOM manifest generation.
- `tests/test_state_writer.py` — verifies the producer side of the heartbeat protocol: spine writes state, heartbeat consumes it, settlement writes state.
- `STRESS_TEST_REPORT.md` — pre-delivery test results (live receipts).

## What the Twin is NOT

- Not a model, not a wrapper competing with the host — the host builds; the Twin prices, arbitrates, remembers.
- Not global: calibrated for African high-context markets (archetypes in the kernel registry). **Outside calibration it says so and downgrades itself to lens-only.** A Twin that fakes global competence is fraud (see §6 of CLAUDE.md).
- Not the revenue: the Twin is the free contagion layer. Paid layers (signed charters, verification, certification, capital-side gates) ride on it — see S17B.

## Dev-team TODO before public ship

1. Wire real MCP tool names from the live `/mcp` server into `spine/checkpoints.md` route table (client fallback is direct HTTPS and works today).
2. Decide charter anchor targets (public git repo + Wayback minimum; Zenodo for flagship).
3. `/v1/auth-check` is currently 403 not-registered upstream — smoke test uses `/v1/schema` for auth verification instead. Flag to kernel team.
4. Full live smoke requires a PRO/ENTERPRISE-scope key because `/v1/strategy-sparring` is intentionally unavailable to STANDARD sandbox keys. With the public sandbox key the smoke test exits as `STANDARD-SCOPE PASS`.
5. Field-signal status polling is intentionally not automated until the API publishes a field-signal status route. Until then, `scripts/twin_attest.py` records only human-reviewed attestation references.
6. Naming is a founder decision — "Twin" used throughout as working title.
7. Free-tier Skeptic access needs a product/kernel decision: TWIN-scoped key class, `sparring-lite`, or an honest reduced free tier.
