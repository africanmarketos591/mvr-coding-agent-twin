# Cursor Free-Plan Field Test Response

## Evidence verdict

This was a useful OOBE/provenance test, not a Twin treatment run and not a capability measurement.

The workspace's `mvr-twin/` contains only `AGENTS.md` and `VERSION`; it is not a Git checkout and has no `scripts/`. Cursor attempted bootstrap and checkpoint commands, but no Twin script executed. It then wrote committee, decision-log, build-contract, and semantic-review JSON in invented schemas. The real tools reject the result:

- charter preregistration: missing hash;
- build contract: unsupported format, stale version, missing fingerprints;
- authority receipts: none;
- run evidence: rejected for `seats_sat.spine=true`, `provisional=false`, and route-call claims without authority.

The doctrine still transferred useful judgment: custody and automatic disbursement were redirected to a treasurer ledger, and the member/contribution/rotation core survived. That is lens transfer, not proof that the Twin ran.

## Product verdict

The generated app is a prototype, not suitable for the promised real chama use next month. A disposable Flask run reproduced:

- unauthenticated member seeding;
- unauthenticated export of all 20 member phone numbers;
- KES 1 accepted from each member while a fixed KES 40,000 payout was queued;
- unauthenticated payout confirmation with no M-Pesa reference;
- a savings-score engine shipped despite the charter cut, with only a label saying lending was unauthorized.

## Changes earned

1. `AGENTS.md` now requires full package/install verification before any governance artifact and forbids hand-authored imitations after clone/checkpoint failure.
2. `scripts/twin_verify_run.py` separates verified, rejected, incomplete, and inconclusive states. Unlike the proposed draft, an arbitrary 64-hex hash without a live key can never return verified.
3. Law 6 now uses kernel-measured country calibration scope inside the canonical spine and committee. Read-only calibration health, market profile, and calendar calls live in `spine/mvr_client.py`; a second extension client was deliberately not created.
4. `savings_score` is now recognized as credit-scoring capability by both build and export tripwires.

## Boundary

The run verifier proves live kernel authority plus local artifact consistency at a named stage. It cannot prove which host process authored every byte. The live OpenAPI does expose 209 paths, but route count is not product value; additional routes will be wired only when a tested workflow consumes them.
