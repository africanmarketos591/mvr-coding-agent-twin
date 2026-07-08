# Changelog - MVR Coding Agent Twin

## 1.1.0-beta.19 - 2026-07-08 (outcome-feedback bridge and egress scanner)
- **Outcome-feedback bridge:** added `scripts/submit_outcome_feedback.py`, a dry-run-first bridge that packages settled decision-log outcomes for `/v1/outcome-feedback`. The kernel route was verified live via its 422 contract and reports `calibration_impact=not_recorded` for invalid submissions. The script defaults to `--dry-run`; `--submit` is explicit.
- **Optional online authorizing-receipt check:** added `hooks/verify_authorizing_receipt.py` for strict environments that want to verify the authorizing decision-log entry's kernel hash against `/v1/ledger/verify/<hash>`. This is an opt-in helper, not a default commit-time network dependency.
- **Reusable egress scanner:** added `adapters/egress_scanner.py` so MCP proxies, CI publish steps, webhooks, or outbound wrappers can reuse the exact keyword + semantic/multilingual classifier that gates commits.
- **Regression coverage:** added `tests/test_new_beta18_artifacts.py` covering dry-run outcome payload validation, authorizing-receipt states, and egress scanning.
- **Boundary retained:** the Twin packages outcome evidence; kernel calibration review adjudicates. The local package still does not auto-calibrate, auto-settle, or intercept every egress channel by itself.

## 1.1.0-beta.18 - 2026-07-08 (receipt verification, semantic tier, settlement pulses)
- **PRE-EXPORT receipt verification:** added `scripts/verify_receipts.py` now that `/v1/ledger/verify/<hash>` is live on the kernel. Authority hashes must verify against the kernel ledger before export; content-derived hashes remain informational. This supersedes the beta.15-beta.17 "kernel-pending" note.
- **Draft-only settlement daemon:** added `adapters/pulse_collectors.py` and `scripts/settlement_daemon.py` for schedulable public-signal collection. It writes settlement drafts only, never `settled=true`, and never records hit/partial/miss without human countersign.
- **Escalate-only semantic tier:** added `hooks/claim_semantic_tier.py` and wired the gates/sentinel to `classify_escalating_content()`. The keyword classifier remains the floor; the semantic/multilingual tier can only add a block when the floor is silent.
- **Outcome priors made bucketable:** preregistration skeletons and the decision-log schema now include advisory `archetype`, `market_scope`, and `redirect_pattern` fields consumed by `scripts/build_priors.py`. Missing values remain safe and bucket as `unknown_*`.
- **Regression coverage:** added tests for receipt verification, settlement daemon draft-only behavior, and semantic-tier escalation; expanded preregistration tests for prior dimensions.
- **Deferred intentionally:** kernel-side calibration ingestion, enterprise egress control, and prose-level blocking remain outside the local package boundary.

## 1.1.0-beta.17 - 2026-07-08 (response sentinel and advisory outcome priors)
- **Advisory response sentinel:** added `hooks/response_claim_sentinel.py` for hosts that expose final-response/Stop hooks. It detects obvious claim-shaped assistant prose, writes `mvr/response-sentinel.jsonl`, and injects advisory context. It is counsel only: fail-open, never blocks, never authorizes, and never replaces PRE-CLAIM for external artifacts.
- **Advisory outcome priors:** added `scripts/build_priors.py` to summarize settled `mvr/decision-log.json` entries into `governance/outcome_priors.json`. Priors are explicitly `advisory_only_no_kernel_mutation_no_claim_authorization`; cold-start buckets stay `insufficient_prior` until the configured minimum sample size.
- **Regression coverage:** added `tests/test_response_claim_sentinel.py` and `tests/test_build_priors.py`.
- **Field validation note:** the EastAgriGate Opus field run validated beta.16's content-shaped evasion gate by blocking claim-bearing fertilizer-credit terms under `docs/`, not just under `claims/`.
- **Deferred intentionally:** automatic settlement pulses, kernel-side calibration ingestion, live receipt verification, semantic/multilingual egress control, and prose-level blocking remain roadmap/kernel/enterprise-governance items. This release does not counterfeit any of them locally.

## 1.1.0-beta.16 - 2026-07-07 (Cursor adapter and one-command install)
- **Cursor harness artifacts:** added `adapters/cursor-hooks/` with a `hooks.json` template plus `pretooluse_claim_gate.py` and `before_submit_heartbeat.py` wrappers. Cursor hook coverage is version-dependent, so these are write-time/heartbeat best-effort layers; git pre-commit remains the hard universal floor.
- **One-command Cursor install:** `scripts/install.py --root .` now installs `.cursor/rules/mvr-twin.mdc`, merges `.cursor/hooks.json`, and adds `.cursor/mcp.json` with the AfricanMarketOS MCP server using `${MVR_API_KEY}`. Existing Cursor config is merged, not clobbered, and no keys are written.
- **Cursor browser research protocol:** added `adapters/cursor-browser-research.md` for source-ledger discipline when Cursor browser tooling is available. Unsupported facts remain `UNKNOWN - not verified`.
- **Install regression coverage:** `tests/test_install_and_inplace.py` now verifies Cursor rules, hooks, MCP config, and idempotency.
- **Deferred intentionally:** live receipt verification, TWIN/sparring-lite key class, edtech-specific archetype, settlement-to-calibration, and enterprise egress proxy remain kernel/product roadmap items, not local package guarantees.

## 1.1.0-beta.15 - 2026-07-07 (claim-surface detection from Opus field run)
- **Content-shaped claim evasion closed for obvious text files:** both the harness hook and git pre-commit gate now scan staged/write-time text for investor, rollout, regulated-money, board, and partnership/distributor claim language outside `claims/`. Obvious cases (for example parent savings wallet launch terms under `docs/`) block as `claim_content_outside_claims` and must move to the explicit claim surface before PRE-CLAIM.
- **Regression coverage:** `test_claim_gate.py` and `test_pre_commit_gate.py` now verify that ordinary docs still pass while claim-shaped docs outside `claims/` are rejected. This addresses the field finding that syntactic path-only classification made `docs/notes.md` a known dodge.
- **Boundary kept honest:** non-git exfiltration (email, SaaS dashboards, CI/runtime deployment text, copy-paste) remains an enterprise egress-control/MCP-proxy problem, not something a local git hook can truthfully guarantee.
- **Receipt verification status:** the Kibera Opus run exposed `verification_url` fields, but a direct check of the reported `/v1/ledger/verify/<hash>` route returned 404. Live receipt verification is therefore a kernel/API publishing task before it can become a gate option; the local package still labels exports as requiring external kernel verification.

## 1.1.0-beta.14 - 2026-07-07 (override-authority precision from Opus field run)
- **Named-human override semantics hardened:** local overrides are now machine-distinct from kernel-backed authorizations. If `decision_authorization.authorized_use` exceeds `kernel_authorized_use`, the gates require `authorization_basis: "named_human_override"`, signed `human_review`, and `override_note`; otherwise they fail closed as ambiguous local authorization.
- **Override receipts are explicit:** successful overrides emit `allow_override_claim`, never `allow_claim`, with `kernel_authorized_use` and `authorization_basis` attached. Export reviewers can now separate local human discipline from kernel permission without reading prose.
- **Unsigned review enforcement:** `human_review.required=true` is now enforced by both the harness hook and git pre-commit gate. Unsigned required review cannot authorize claims, matching `memory/decision-log.format.md`.
- **Regression coverage:** claim-gate and pre-commit suites now cover unsigned human review, ambiguous local authorization, and explicit signed override receipts. Field finding came from the Claude Opus 4.8 healthcare-procurement simulation after the Antigravity beta.13 healthcare run validated the normal block path.

## 1.1.0-beta.13 - 2026-07-07 (second field report: rulings + stale-renewal UX)
- **Stale-block renewal path (accepted essence of "renew_claims.py", built smaller):** both gates' stale messages now carry the full renewal path AND the last known evidence gaps from the expired entry - the developer returning after a month sees exactly what was outstanding, in the block message itself. A separate renewal script was rejected: it would be a third wrapper around two spine calls the checkpoint already makes.
- **Interception-layers note in install.py:** until the host's write-tool hook is wired, claim interception is commit-time only; write-time interception (the "Silent Bypass" fix) ALREADY EXISTS as the harness-level claim gate (settings-hooks.json / adapters) - the installer now says so explicitly so no host skips wiring it.
- **Ghost-Decision-Log ruling (doctrine, no code):** cryptographic receipt signing accepted as KERNEL roadmap (raises tamper cost, enables offline third-party verification) but rejected as a local-bypass fix - a developer who can edit the log can also patch the hook; the trusted-client fallacy has no local solution. The enforcement boundary remains export-time kernel-receipt verification (Tamper Honesty, CLAUDE.md Section 7).
- Symbiosis-document corrections on record: the heartbeat injects CASE state, never market telemetry feeds (MVR is not market data - standing positioning constraint); the Outage Rule governs the Twin's own conduct, not application architecture directives.

## 1.1.0-beta.12 - 2026-07-07 (field-report fixes from the first developer simulation)
- **Offline degradation (real crash bug fixed):** the spine client caught only HTTPError; a network-down URLError crashed uncaught. `call()` now returns status 0 + `kernel_unreachable` + the Outage Rule text. REJECTED the proposed local-verdict fallback: an offline spine that invents answers is a counterfeit spine; offline = build proceeds, charters provisional, claims stay default-denied.
- **Differential heartbeat:** unchanged state within 2h emits a one-line tag (verdict + authorization) instead of the full digest - fixes token cost AND banner blindness. Expired state is NEVER compressed; safety lines always ship full. Marker `mvr/.heartbeat-last`, fail-silent.
- **`preregister.py --in-place`:** hash computed, embedded, and self-verified in one command - closes the manual-embed error class that caused the original rehearsal hash-mismatch incident. Anchors written as `pending`, never fabricated.
- **`scripts/install.py`:** one-command setup (mvr/.gitignore, sh-shebang pre-commit shim Windows-safe, idempotent, `--verify` runs all offline suites). An installer that does not verify is a liability.
- **Pivot Explanation rule (CLAUDE.md Section 4):** every redirect leads with <=3 plain-language sentences (binding constraint, what was preserved, what stays legal today) before the charter. Field finding: an unexplained pivot is experienced as theft, not judgment. REJECTED the /v1/committee-digest server route: the pivot narrative is composed from local context the kernel cannot see; this is lens doctrine, not a kernel feature.
- Kernel-team roadmap note (not in package): machine-readable constraint descriptors in category-playbook output (accepted essence of the "blueprint scaffolding" request; code-stub generation rejected - the host generates better code than any template, the kernel's job is constraints).
- New suite `tests/test_install_and_inplace.py`; heartbeat suite extended to 14 checks.

## 1.1.0-beta.11 - 2026-07-07 (public discovery surface)
- **Root `llms.txt`:** machine-readable pointer for AI agents, with controlled-beta boundaries, key route, primary files, and host-agent instruction.
- **`REPLICATION_RECEIPTS.md`:** public-safe evidence file preserving the strict run near-pass, controlled-beta pass, defect ledger, and remaining human gates.
- Public launch copy updated outside the package to make the agent self-integration path explicit and link the evidence record.

## 1.1.0-beta.10 - 2026-07-07 (public-discovery readiness)
- **LICENSE added (Apache-2.0, canonical text):** a public repo without a license is all-rights-reserved - strangers' models could not legitimately integrate, defeating the discovery thesis. Apache-2.0 recommended (patent grant, maximum lens contagion; moat is server-side + ledger). Founder may swap before publication; shipping without one is not an option.
- **README publication scrub:** canonical-copy governance line no longer references an internal drive path; canonical = tagged public release, mirrors verified by tool-generated manifest. License + agent-integration note added.
- No code changes; all 9 suites unaffected and re-verified.

## 1.1.0-beta.9 - 2026-07-07 (strict manifest release process)
- **Manifest generation is now code:** added `scripts/generate_manifest.py` so release manifests are generated by Python with explicit UTF-8 and no BOM, never by shell JSON serialization.
- **Strict manifest regression test:** `tests/test_manifest.py` verifies no UTF-8 BOM, strict JSON parsing, runtime-file exclusion, and normal file inclusion.

## 1.1.0-beta.8 - 2026-07-07 (duplicate-header fail-closed fix)
- **Duplicate preregistration header defense:** `scripts/preregister.py` now fails closed unless a charter contains exactly one `**Preregistration hash:**` line. This closes an ambiguity where a duplicate hash line could be present before hashing and verification would still pass using the first hash.
- **Regression coverage:** `tests/test_preregister.py` counts duplicate headers, and `tests/test_ledger_audit.py` verifies the duplicate-header attack fails through the real preregistration CLI.

## 1.1.0-beta.7 - 2026-07-07 (the auditor's one command)
- **scripts/ledger_audit.py:** full-ledger integrity audit in one command - every charter entry hash-verified against its file (canonical rules), anchor counts derived from append-only `anchor_update` entries, and the **INFLATION CHECK**: any entry claiming `preregistered=true` with <2 anchors fails the audit. Auditors trust DERIVED status, never flags. `--add-anchor` records anchors append-only (original entries never mutated); derived PREREGISTERED at >=2 anchors. Suite `tests/test_ledger_audit.py` (8 checks).
- Adversarial verification of the beta.5/6 hash cycle by Fable 5: embed->verify, idempotence, body-tamper detection, duplicate-header attack (fails closed - correct), CRLF normalization - all PASS.
- Key-scope mystery closed with evidence: direct client probe returned sparring 200 with the same keyfile - the earlier 401 was label-line parsing, exactly what keyfile_loader.py fixed. No key rotation occurred.

## 1.1.0-beta.6 - 2026-07-07 (enterprise rehearsal hardening)
- **Safe internal key-file loading:** added `scripts/keyfile_loader.py` and `scripts/run_smoke_from_keyfile.py`. Internal rehearsal key files are parsed only from explicit `X-API-Key:`, `MVR_API_KEY=`, `API_KEY=`, or `Authorization: Bearer` fields. Human-readable labels are deliberately ignored.
- **Key parsing regression tests:** `tests/test_keyfile_loader.py` verifies the loader prefers the explicit key field, accepts env-style sandbox keys, and rejects label-only files.
- **Preregistration regression tests:** `tests/test_preregister.py` verifies the canonical hash survives insertion into the charter header and changes when prediction body text changes.

## 1.1.0-beta.5 - 2026-07-07 (preregistration integrity fix)
- **Canonical preregistration hashing:** `scripts/preregister.py` now normalizes only the self-referential hash/anchor header field before hashing. Inserting the hash no longer invalidates the hash; changing any prediction text, source, verdict, or settlement criterion still changes it.
- **Verification mode:** `python scripts/preregister.py --verify <charter.md>` now fails if the embedded charter hash does not match the canonical hash. Beta charters are not considered preregistered unless this passes after the final header is inserted.
- **Decision-log discipline:** preregistration output now includes a decision-log skeleton and marks `settlement.preregistered=false` until at least two external anchors exist.

## 1.1.0-beta.4 - 2026-07-07 (the 13-scenario adversarial sweep)
- **Passport leak prevention (data protection):** `templates/mvr.gitignore` + REQUIRED install step 6 + binding SECURITY "Repository hygiene" rule - `mvr/passport.json` (personal data) can no longer silently reach shared/public repos; audit-trail files remain committed on purpose.
- **CLAUDE.md Section 7 OPERATING SCENARIOS (binding):** Pivot Rule (superseding charter; stale heartbeat must not steer a new case), Mid-Journey Rule (no unprompted autopsy for sunk-cost users; forward-looking tranche only), Outage Rule (build proceeds, charter marked provisional, claims auto-blocked = correct), Absent-Seat Rule (charter states which seats sat - a committee that hides vacancies is theater), One-Case-One-Repo v1 constraint (stated, not hidden), Tamper Honesty (local log tamper-evident not tamper-proof; external parties verify kernel receipts; unverifiable exports are worth 0.30), Path-Evasion Honesty.
- **Nudge marker hygiene:** stale `.twin-nudge-*` markers cleaned on rollover (no accumulation); heartbeat suite now 11 checks.

## 1.1.0-beta.3 - 2026-07-07 (the self-improvement audit: two runtime gaps closed)
- **Cold-start nudge:** heartbeat no longer silent when no case exists - the moment the host's build-what-was-asked reflex is strongest and no gate can fire. One-line committee reminder, at most once per day (marker-file throttled), fail-silent. Closes the "Twin mute at maximum sycophancy" hole.
- **Borrowed-consequences wire:** heartbeat injects `Track record: ...` from `state.settled_summary` once settlements exist - the calibration sentence no frontier model can say alone now has a physical path into the host's context. Written only by the settlement process, misses included, never speculative (state.format.md).
- README headings no longer carry version numbers (root-cause fix for the stale-heading class of defect; `VERSION` is the single source).

## 1.1.0-beta.2 - 2026-07-07 (host-agnostic authority)
- **Git pre-commit claim gate** (`hooks/pre_commit_claim_gate.py`, 5/5 tests): the same default-deny contract enforced at the repository level - authority now survives on hosts without harness hooks (Cursor, Codex CLI). Receipts to `mvr/gate-events.jsonl` with `tool: git-pre-commit`.
- **Host adapters** (`adapters/`): AGENTS.md (Codex convention), cursor-rules, antigravity-knowledge (hooks/scheduled-tasks/browser-subagent/artifacts mapping). One doctrine, four host dialects.
- **Host Support Matrix** in README: honest per-host functional grades; degraded installs must never be marketed as the full Twin.

## 1.1.0-beta.1 - 2026-07-07 (controlled-beta candidate)
- **Citation discipline (hard rule):** every named incumbent, regulation, figure, failure precedent, or health/credit/legal constraint carries source + date or `UNKNOWN - not verified`; mandatory Source Ledger in the Build Charter. (Codex)
- **Default-deny precision fix:** unverified facts cannot justify redirects or external recommendations - but they never UNBLOCK claims; claims stay denied absent decision-log authorization, and in credit/health/legal categories an UNKNOWN regulatory status is itself grounds for continued non-authorization. (Fable 5, closing a wording loophole in the citation rule.)
- **Gate audit trail:** every claim-path decision (block/allow) appends an enforcement receipt to `mvr/gate-events.jsonl`; fail-silent by contract; new suite `tests/test_gate_audit.py` (5 checks).
- **settle.py state-path fix:** `mvr/state.json` now written next to the decision log, never relative to cwd (settlement daemon can run from anywhere).
- **Real-time counsel channel:** `mvr/state.json` + `hooks/heartbeat.py` (UserPromptSubmit) inject a <=120-word market digest every turn; counsel fails SILENT, authority fails CLOSED, shared 7d/30d clock. `tests/test_heartbeat.py` (8), `tests/test_state_writer.py` (5).
- **append_settlement.py:** safe append-only settlement entries without hand-editing JSON. (Codex)
- SECURITY.md (key handling, data protection, audit), VERSION, this changelog.
- Round-3 replication protocol: 0-4 rubric, separated roles, control-winnable criteria, verbatim archiving, positive-control case requirement.

## 1.0.1 - 2026-07-06 (Codex hardening)
- Hook matcher widened to `Write|Edit|MultiEdit|NotebookEdit`; multi-path extraction for MultiEdit.
- Substring-authorization bypass closed (exact membership on normalized lists); malformed latest entry fails closed; UTF-8 BOM logs readable.
- Claim-gate suite 9 -> 14 checks; smoke runner reports STANDARD-SCOPE PASS with skip semantics; key-scope docs corrected (`/v1/strategy-sparring` requires PRO/ENTERPRISE).

## 1.0.0 - 2026-07-06 (initial, Fable 5)
- Three-strata package: LENS (angles, research protocols), SPINE (kernel client, checkpoints, claim gate), MEMORY (passport, decision log, charters, mirror, preregistration, settlement).
- Live spine verified 12/12; claim gate 9/9; scripts and configs validated.
