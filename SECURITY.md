# SECURITY & DATA PROTECTION — MVR Coding Agent Twin

## API keys
- Keys live ONLY in the `MVR_API_KEY` environment variable. Never in chat, prompts, repos, logs, charters, mirrors, or `mvr/` files. The spine client refuses to run without the env var and never prints the key; keep it that way.
- Scope classes: STANDARD (sandbox; public routes only — no strategy-sparring/Skeptic), PRO/ENTERPRISE (full committee), TWIN-scoped (planned; founder decision pending). Beta users receive TWIN-scoped or enterprise-scope eval keys — never ship the Skepticless STANDARD experience under the Twin's name.
- Rotate immediately on suspicion of exposure; request rotation via https://africanmarketos.com/get-api-key. Leak scans (secret + prior-record) are part of every replication and every release — keep them in the checklist.

## Personal data (Operator Passport)
The passport is personal data. Non-negotiables:
- **Consent basis recorded** (`consent.consent_basis`) before storage; storage and per-run disclosure are separate consents (`disclosure_per_run`).
- **Role labels, not personal names**, for counterparties unless the counterparty consented (passport schema: `label` is role-level by default). Attestation requests to counterparties are themselves consent-first (`/v1/field-signal` privacy rules: plain-language consent, data minimization, aggregate-before-board-safe).
- The passport is user-owned and portable; delete on request, fully — settlement records may retain the *aggregate* fact that a charter existed and settled, never the personal reach data.
- Jurisdictional floor for beta (Kenya/Uganda operators): Kenya Data Protection Act 2019 and Uganda Data Protection and Privacy Act 2019 both require consent-or-lawful-basis, purpose limitation, and data-subject deletion rights — the schema fields above exist to satisfy exactly that. Cite the specific act in any beta agreement; do not paraphrase compliance.

## Repository hygiene (data-leak prevention — REQUIRED)
`mvr/passport.json` is personal data and MUST NEVER be committed: a shared or public repo would publish the operator's counterparty relationships. Install `templates/mvr.gitignore` as `mvr/.gitignore` before the first commit (install step 6). Committed on purpose: `decision-log.json`, `gate-events.jsonl`, charters, mirrors — they are the audit trail. Local-only: `passport.json`, `state.json` (cache), nudge markers.

## Audit & integrity
- `mvr/gate-events.jsonl`: append-only enforcement receipts (event, claim class, path, reason, entry_id, timestamp). Contains file paths, never secrets or personal data. Part of the case record; ships with exported case audits.
- `mvr/decision-log.json`: append-only; corrections are new entries. The claim gate fails CLOSED on unreadable or malformed logs — a broken log never authorizes.
- Named-human overrides are local-only controls, not kernel authorization. Any override that extends local `authorized_use` beyond `kernel_authorized_use` must be signed in `human_review`, explain itself in `override_note`, and will be receipted as `allow_override_claim` for external review.
- Obvious claim-shaped text outside `claims/` is blocked as path evasion, but local hooks cannot police every exfiltration path. Email, SaaS dashboards, CI systems, and deployed runtime copy need enterprise egress controls or an MCP/API proxy if they become beta requirements.
- Charters are hashed and externally anchored (≥2 anchors) before they count as preregistered; settlement writes are made only by the settlement process, never the authoring agent.

## Reporting
Report vulnerabilities or suspected key/data exposure privately to info@africanmarketos.com before any public disclosure. Include the `gate-events.jsonl` excerpt and charter hash if the issue touches a live case.
