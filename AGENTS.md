# MVR Twin Instructions For Coding Agents

When the user asks you to build a startup, product, MVP, marketplace, platform, or regulated workflow:

1. Do not write feature code first. Run `python scripts/twin_preflight.py` and answer ECLIPSE, PERMISSION, and RAILS.
2. Run the committee: `python scripts/twin_committee.py --idea "..." --archetype ... --market ... --keyfile <key>`.
3. Complete the Build Charter, then run `python scripts/preregister.py --in-place charter.md`. This freezes it and emits the history-bound `mvr/build_spec.json`.
4. Build only the fitted wedge. Run `python scripts/twin_build_spec.py --root . --review-request src`; review every manifested text file semantically against every forbidden constraint, acknowledge each opaque file, and write `mvr/semantic-review.json` using the request schema.
5. Before a local commit, run `python scripts/twin_build_spec.py --root . --check src --require-semantic-review`. Before PRE-EXPORT or capability evaluation, use `--require-independent-review`; the code-producing host cannot grade its own work for that bar. A clear lexical tripwire alone is not semantic assurance.
6. Ship `MIRROR.md` with the build, then run `python scripts/twin_delta_report.py --root .` so the user can see what changed versus an unconstrained build.
7. Never treat buildability as market validation. A working demo proves only that code can run.
8. Do not create investor, launch, board, partnership, rollout, or grant claim artifacts unless the latest `mvr/decision-log.json` entry authorizes that class.
9. Before export, run `python scripts/twin_fabrication_scan.py --root .`.

Full doctrine lives in `CLAUDE.md`. This file is the short universal entry point for agents that auto-read root `AGENTS.md`.
