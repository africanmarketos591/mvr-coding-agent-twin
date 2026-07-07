# Pre-Delivery Stress Test Report — MVR Coding Agent Twin v1.0.0
**Date:** 2026-07-06 · **Tester:** Claude Fable 5 (author — independent replication required before public ship, see §4)

## 1. Live spine verification (kernel v6.32.0, through the shipped client)
12/12 PASS:
- Liveness+auth via /v1/schema: 200, 0.55s (auth-check unregistered upstream — documented workaround shipped).
- category-playbook: demand schedule + guardian map present, 0.24s.
- strategy-sparring: challenge_ready, **overclaim tripwire fired on the planted "no risk" claim**, evidence bill present, 1.88s.
- Idea-stage decision-check: abstains with codes (constant-verdict contract honored), **internal_planning authorized / national_rollout not authorized** — confirming the gate philosophy (code never blocked, claims gated), 1.99s.
- All latencies within committee budget (<5 min total; kernel seats sum <5s).

## 2. Claim gate contract (offline, subprocess, as the harness runs it)
9/9 PASS: code never gated · claim blocked without log · unauthorized claim blocked with evidence gaps named in the block message · authorized claim allowed · **stale (>30d) authorization blocked** · unclassified claims/ artifact blocked with naming instruction · **corrupt log fails CLOSED for claims** · Read never gated · no-log block message instructs the PRE-CLAIM checkpoint.

**Codex verification addendum, 2026-07-06:** after hardening the hook, the offline contract now passes 14/14. Added coverage: `MultiEdit`, Windows-style claim paths, exact authorization parsing so substring membership cannot authorize, latest-entry authority, malformed latest-entry fail-closed behavior, and UTF-8 BOM decision logs from Windows/PowerShell.

## 3. Scripts + config
- preregister.py: canonical SHA-256 + timestamp + anchor instructions emitted. PASS.
- settle.py: due-checkpoint detection, pulse checklist, misses-published doctrine in output. PASS.
- .mcp.json / settings-hooks.json / passport.schema.json: valid JSON. PASS.
- Empty-key path: client refuses with instructive error, no silent fallback. PASS (verified accidentally and kept as a test).
- heartbeat.py counsel channel: 8/8 PASS (silent with no case, digest injects, staleness flags, >30d void, uncalibrated lens-only, corrupt state silent).
- state producer contract: 5/5 PASS (spine writes `mvr/state.json`, heartbeat consumes it, settlement run writes state).

## 4. Known limits shipped honestly (do not remove from README)
1. **Author-tested only.** The behavioral layer (CLAUDE.md) is verified by construction against the S16B live experiment protocol, but no naive operator has run it end-to-end. Required before public ship: blind replication (junior/B, other agent host).
2. **Instruction-layer efficacy is probabilistic.** The six laws bind a well-behaved host; a hostile or heavily drifted host is bound only at the three hook checkpoints. That is the design (authority at the gates), not a bug — but the team should know the lens is persuasion, the spine is law.
3. **Passport v0 is self-reported only** (attestation flow needs tenant provisioning of project_id for field-signal).
4. **One archetype protocol** (fintech_platform) at specialization depth; general protocol covers the rest at lower resolution.
5. **MCP tool names** on the live /mcp server not yet mapped into checkpoints.md (client fallback is direct HTTPS and fully tested).
6. **Calibration boundary:** African high-context markets only; the Twin self-downgrades to lens-only elsewhere (CLAUDE.md §1 Law 6).
7. **Key scope:** Codex re-ran the smoke suite with the public sandbox key (`mvr-demo-key-2026`). `/v1/schema`, `/v1/category-playbook/{archetype}`, and `/v1/decision-check` verified live; `/v1/strategy-sparring` correctly returned `403` because STANDARD scope is not allowed. The smoke runner now reports this as `STANDARD-SCOPE PASS` for sandbox installs. Codex also re-ran the suite using Mark's internal enterprise key file without printing the key; the full suite returned `ALL PASS`.
8. **Free-tier Skeptic gap:** STANDARD-scope installs do not include the full un-prompt-able Skeptic because `/v1/strategy-sparring` is plan-gated. This is not a code defect; it is a founder/kernel-team product decision before public distribution (recommended: TWIN-scoped, rate-limited key class or bounded `sparring-lite`).

## 5. Verdict
Ship to dev team as an internal alpha. The gate contract is now stronger than the delivered spec, the heartbeat protocol is producer-backed rather than reader-only, and the full live spine has passed with an internal enterprise key. Do not public-ship or sell the Twin until a naive operator completes blind replication, a named reviewer signs the first externally shareable artifact, and the free-tier Skeptic decision is settled.
