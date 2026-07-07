# MVR Coding Agent Twin

*(Version lives in `VERSION` only — headings never carry version numbers, so they can never go stale.)*

**A market-reality co-processor for AI coding agents.** It fuses the host agent's native intelligence with MVR's high-context market intelligence, so the agent builds what the market can carry, not just what the user imagined.

Built 2026-07-06 by Claude Fable 5 as its own mirror: the instruction layer encodes Fable-5-class judgment discipline PLUS explicit countermeasures for the failure modes frontier models have from the inside (instruction-following under pressure, confidence without ground truth, imagination rewarding). It is model-agnostic: any agent that supports instructions + MCP + hooks (Claude Code / Fable 5, Codex CLI, Antigravity, Cursor) can host it. On a model more powerful than Fable 5, the Twin gets *stronger* — the spine and memory are external to the model, and better reasoning over them compounds.

## Architecture (three strata — see S18/S19 for doctrine)

| Stratum | What | Where in this repo | Copyable? |
|---|---|---|---|
| **LENS** | Thinking angles + archetype research protocols (counsel, everywhere) | `lens/` + `CLAUDE.md` | Yes — by design; it recruits |
| **SPINE** | Un-prompt-able kernel arbitration at hook-enforced checkpoints (authority, at the gates) | `spine/`, `hooks/`, `.mcp.json` | No — external position |
| **MEMORY** | Operator Passport + preregistered, confession-free-settling Build Charters | `memory/`, `templates/`, `scripts/` | No — it ages |

## The behavior loop (non-negotiable)

`idea → silent inference → internal committee fight (pre-code) → fitted build → MIRROR artifact ships with the build`

- **Zero questions** in the ideal run. The Twin infers; the mirror invites corrections. Hard cap: 3 confirmations, only when inference is impossible, never a researchable fact.
- **Judge before code. Never interrogate. Never judge after the build.**
- The user sees the Build Charter and the Mirror — never the fight.

## Install (Claude Code host)

1. Copy this directory into the project root (or reference it).
2. Merge `settings-hooks.json` into `.claude/settings.json` (claim gate + checkpoint enforcement).
3. `.mcp.json` wires the live MVR MCP server. Set env `MVR_API_KEY` (sandbox eval key: `mvr-demo-key-2026`, non-commercial STANDARD scope; production/evaluation keys via https://africanmarketos.com/get-api-key).
4. The host agent reads `CLAUDE.md` (Claude Code does this natively; for Codex/others, load it as the system/project instruction).
5. Run `python tests/smoke_test.py` — must print `ALL PASS` before first use with a PRO/ENTERPRISE-scope evaluation key. The public sandbox key verifies `/v1/schema`, category playbooks, and `/v1/decision-check`, but `/v1/strategy-sparring` is correctly plan-gated and will return `403` on STANDARD scope. (Note: the kernel edge rejects default Python user agents; the client in `spine/mvr_client.py` sets a proper UA. Do not bypass it.)
6. **REQUIRED before first commit:** copy `templates/mvr.gitignore` to `mvr/.gitignore` — the Operator Passport is personal data and must never reach a shared or public repo (SECURITY.md, Repository hygiene).

Internal rehearsal key files: use `python scripts/run_smoke_from_keyfile.py <keyfile>` instead of regex-scanning for `mvr-...`. The helper only accepts explicit `X-API-Key:`, `MVR_API_KEY=`, `API_KEY=`, or `Authorization: Bearer` fields and never prints the key.

## The communication protocol (how market metrics rewrite context in real time, invisibly)

Three channels, never confused with each other:
1. **Spine writes state** — every checkpoint (and every settlement run) writes `mvr/state.json` (see `memory/state.format.md`): verdict, authorization, top blockers, passport status, staleness, calibration boundary.
2. **Heartbeat makes it ambient** — `hooks/heartbeat.py` (UserPromptSubmit) injects a ≤120-word digest into the agent's context on EVERY user prompt. The user never sees it; the agent is never without current market truth. Counsel channel: fails SILENT.
3. **Gates enforce it** — `hooks/claim_gate.py` (PreToolUse) blocks unauthorized claim artifacts. Authority channel: fails CLOSED.

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
- Every beta Build Charter starts the Consequence Ledger; preregister from charter #1 and verify with `python scripts/preregister.py --verify <charter.md>`.
- Do not claim global portability. The package downgrades to lens-only outside calibrated African/high-context markets.
- Do not sell signed/certified artifacts until the D6 reviewer/signature role is filled.

## Version & governance

- **Version:** see `VERSION`; changes tracked in `CHANGELOG.md`. **Canonical copy:** the tagged release of the public repository; all mirrors are kept hash-identical — verify any copy against the release `HASH_MANIFEST_<version>.json` before deploying. Manifests are tool-generated only (`scripts/generate_manifest.py`).
- **License:** Apache-2.0 (`LICENSE`). The lens is meant to spread; the spine and ledger live server-side. AI agents reading this repository may integrate per the license and the Agent Instruction in the beta page.
- **Manifest:** generate with `python scripts/generate_manifest.py` from the package root. This writes strict UTF-8 JSON with no BOM; do not generate release manifests through shell JSON serialization.
- **Security & data protection:** `SECURITY.md` is binding for beta — key handling (env-only, scope classes, rotation), Operator Passport consent/deletion rules (Kenya DPA 2019 / Uganda DPPA 2019 floor), and the append-only audit surfaces.
- **Enforcement receipts:** every claim-path gate decision (block or allow) is appended to `mvr/gate-events.jsonl` — audit-grade evidence of what the gate did and why, shipped with exported case audits. Tested in `tests/test_gate_audit.py`.
- **Default-deny precision (binding interpretation):** unverified facts cannot justify redirects or external recommendations; they never UNBLOCK claims — claims stay denied until the decision log authorizes them, and in credit/health/legal categories an `UNKNOWN` regulatory status is itself grounds for continued non-authorization.

## Host Support Matrix (what functions where — honest grades)

| Stratum | Claude Code / Fable 5 | Antigravity 2.0 | Codex CLI | Cursor |
|---|---|---|---|---|
| LENS (CLAUDE.md doctrine) | native | via `adapters/antigravity-knowledge.md` | via `adapters/AGENTS.md` | via `adapters/cursor-rules.md` |
| SPINE client + checkpoints | full | full | full | full |
| Heartbeat (per-turn ambient state) | hook-native | hook-wire (adapter notes) | read `mvr/state.json` per turn (doctrine) | read `mvr/state.json` per turn (doctrine) |
| Claim gate (harness-level) | hook-native | hook-wire (adapter notes) | limited | limited |
| **Claim gate (git pre-commit — universal)** | ✔ | ✔ | ✔ | ✔ |
| Settlement daemon (`settle.py` on any scheduler) | ✔ | ✔ (scheduled tasks) | ✔ (cron) | ✔ (cron) |
| Memory (passport, decision log, charters, receipts) | ✔ files | ✔ files | ✔ files | ✔ files |
| Browser-verified research/settlement | roadmap (claude-in-chrome) | ✔ native (browser subagent) | — | — |
| Parallel committee seats (context-isolated) | ✔ subagents (v1.1 roadmap) | ✔ subagents (v1.1 roadmap) | — | — |

Rule of honesty: on hosts where the harness gate is "limited," authority lives in the **git pre-commit gate** (`hooks/pre_commit_claim_gate.py`, tested in `tests/test_pre_commit_gate.py`) — every host commits code, so the gate is universal there. Install: `echo 'python mvr-coding-agent-twin/hooks/pre_commit_claim_gate.py || exit 1' >> .git/hooks/pre-commit`. Hosts marked "—" degrade gracefully to lens+spine+memory, which remain fully functional; never market a degraded install as the full Twin.

## Files

- `CLAUDE.md` — the Twin core: laws, committee protocol, checkpoints, refusal boundaries. **Read this first.**
- `llms.txt` — machine-readable entrypoint for AI agents and fetchers.
- `REPLICATION_RECEIPTS.md` — public-safe verification record with misses and remaining limits.
- `hooks/heartbeat.py` + `memory/state.format.md` — the real-time counsel channel (see protocol section above); tested in `tests/test_heartbeat.py` (8/8).
- `spine/mvr_client.py` — kernel client (decision-check, category-playbook, strategy-sparring, evidence-completeness, field-signal request/submit). Env-keyed; never hardcode keys.
- `spine/checkpoints.md` — the counsel/authority contract: exactly when the spine MUST be called.
- `hooks/claim_gate.py` + `settings-hooks.json` — PreToolUse gate: claim-bearing artifacts under `claims/` cannot be written unless the latest decision-log entry authorizes that use class. Code is never blocked (the kernel itself authorizes `internal_planning`).
- `lens/angles.md` — the tethered booster: 10 MVR thinking angles, each with its kernel tether.
- `lens/research-protocols.md` — what to research (never ask): general high-context protocol + fintech_platform specialization.
- `memory/passport.schema.json` — Operator Passport v0 (inferred → mirror-corrected → attestation-upgradeable via `/v1/field-signal/*`).
- `memory/decision-log.format.md` — append-only machine-readable log; the claim gate reads `mvr/decision-log.json`.
- `templates/BUILD_CHARTER.template.md`, `templates/MIRROR.template.md`, `templates/PASSPORT.template.json`.
- `scripts/preregister.py` — computes a canonical charter hash, verifies embedded hashes, and emits the anchor block plus decision-log skeleton (Wayback/Zenodo/git per the Preregistration Protocol). A hash is not valid unless `--verify` passes after the final header is inserted.
- `scripts/run_smoke_from_keyfile.py` + `scripts/keyfile_loader.py` — internal rehearsal helper for local key files; prevents label-slug extraction from masquerading as an enterprise key.
- `scripts/generate_manifest.py` — strict UTF-8 no-BOM manifest generator for release parity checks.
- `scripts/settle.py` — settlement pulse runner: emits the quarterly public-record checklist per charter; silence-detection notes for instrumented builds.
- `scripts/append_settlement.py` — safe append-only settlement writer so humans do not hand-edit and break `mvr/decision-log.json`.
- `tests/smoke_test.py` — live kernel round-trip; `tests/test_claim_gate.py` — hook logic, offline.
- `tests/test_preregister.py`, `tests/test_keyfile_loader.py` — regression tests for preregistration integrity and safe key-file parsing.
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
5. Passport attestation flow can request and submit field signals through `spine/mvr_client.py`, but status polling is intentionally not automated until the API publishes a field-signal status route.
6. Naming is a founder decision — "Twin" used throughout as working title.
7. Free-tier Skeptic access needs a product/kernel decision: TWIN-scoped key class, `sparring-lite`, or an honest reduced free tier.
