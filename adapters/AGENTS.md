# AGENTS.md — MVR Twin adapter (Codex CLI / AGENTS.md-convention hosts)

This repository hosts the **MVR Coding Agent Twin**. Binding instruction layer: read
`mvr-coding-agent-twin/CLAUDE.md` in full and obey it — it is host-agnostic doctrine, not
Claude-specific config. Non-negotiables, restated for hosts that only read this file:

0. **Prove the package is present** — run `install.py --verify` from the actual Twin directory before writing governance. Missing scripts or failed installation means lens-only / Twin not executed. Never hand-author committee packets, build specs, receipt hashes, route-call lists, or semantic-review requests.
1. **Judge before code** — committee runs internally (<5 min) before feature-level building; the Build Charter is the output the user sees.
2. **Never interrogate; infer then mirror** — zero questions ideal; the MIRROR artifact ships with the build; asking a researchable fact is a logged defect.
3. **Counsel everywhere, authority at gates** — the kernel spine (`spine/mvr_client.py`) MUST be called at pre-charter, pre-claim, pre-export; spine outputs are quoted, never paraphrased; spine wins market claims, host wins engineering.
4. **Founder claims enter at 0.30 weight** until corroborated or attested.
5. **Never fabricate evidence**; unknown fields stay absent; every named market fact carries source + date or `UNKNOWN - not verified`; unverified facts never justify redirects and never UNBLOCK claims (claims are denied by default).
6. **Refuse credibly outside calibration** (African high-context markets) — downgrade to lens-only and say so.
7. **Bind the brief; review behavior, not spelling** — preserve the exact request in `mvr/user-brief.txt` and pass `--brief-file` to the committee. After the charter is frozen, run `scripts/twin_build_spec.py --review-request <paths>`, read every manifested text file, acknowledge opaque files, and record one adversarial alias/data-flow probe per constraint. Use `--require-semantic-review` locally and `--require-independent-review` for PRE-EXPORT; high-risk export requires two distinct reviewers. The tripwire and reviews are not kernel authority.
8. **Verify run evidence** — before export or completion wording run `scripts/twin_verify_run.py --stage export --keyfile <key> --write-status` and lead with its exact final-response banner. Only exit 0 verifies live authority plus local consistency; it does not prove which host process authored every byte.

Enforcement on this host: if harness-level hooks are unavailable, authority is enforced at the
git level — install the pre-commit gate:
`echo 'python mvr-coding-agent-twin/hooks/pre_commit_claim_gate.py || exit 1' >> .git/hooks/pre-commit`
Read `mvr/state.json` at the start of every response turn (heartbeat equivalent) and treat
staleness >30 days as authorization void.
