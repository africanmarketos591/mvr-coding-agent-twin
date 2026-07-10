# Cursor adapter - MVR Twin

Install this as `.cursor/rules/mvr-twin.mdc`.

Binding: read `mvr-coding-agent-twin/CLAUDE.md` in full and obey it. Short form for
rule-length limits:

1. Judge before code: run the internal committee and produce the Build Charter before feature work.
2. Never interrogate by default: infer first, then ship the MIRROR artifact for correction.
3. Counsel everywhere, authority at gates: call the kernel spine at pre-charter, pre-claim, and pre-export; quote spine outputs verbatim.
4. Founder claims weigh 0.30 until corroborated or attested.
5. Never fabricate evidence: every named market fact needs source + date or `UNKNOWN - not verified`; unknown facts never unblock claims.
6. Outside African/high-context calibration, downgrade to lens-only and say so.
7. After the charter is frozen, create a semantic review request for the exact product files, review behavior against every cut-list constraint, and validate it with `twin_build_spec.py --check ... --require-semantic-review`. Never call lexical clearance semantic safety.

Cursor enforcement has two layers:

1. **Write-time layer (best effort, Cursor-version dependent):** `.cursor/hooks.json` should wire `preToolUse` to `adapters/cursor-hooks/pretooluse_claim_gate.py` and `beforeSubmitPrompt` to `adapters/cursor-hooks/before_submit_heartbeat.py`.
2. **Commit-time layer (mandatory floor):** the git pre-commit gate (`hooks/pre_commit_claim_gate.py`) blocks claim artifacts and obvious claim-shaped docs without decision-log authorization.
3. **MCP layer:** `.cursor/mcp.json` should expose the AfricanMarketOS MCP server and read `${MVR_API_KEY}` from the environment. Never paste keys into rules or repo files.
4. **Code-constraint layer:** the git gate requires a current `mvr/semantic-review.json` when the build contract carries cut-list constraints. This is a host-model attestation, not deterministic proof.

Read `mvr/state.json` each turn when the heartbeat hook is unavailable; staleness >30d = authorization void. Use `adapters/cursor-browser-research.md` when browser tooling exists; unsupported facts remain `UNKNOWN - not verified`.
