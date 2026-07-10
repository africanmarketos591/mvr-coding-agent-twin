# MVR Twin Instructions For Coding Agents

When the user asks you to build a startup, product, MVP, marketplace, platform, or regulated workflow:

1. Do not write feature code first. Run `python scripts/twin_preflight.py` and answer ECLIPSE, PERMISSION, and RAILS.
2. Run the committee: `python scripts/twin_committee.py --idea "..." --archetype ... --market ... --keyfile <key>`.
3. Complete the Build Charter, then run `python scripts/preregister.py --in-place charter.md`. This freezes it and emits `mvr/build_spec.json`, the authority-to-code contract.
4. Build only the fitted wedge. Before commit/export, run `python scripts/twin_build_spec.py --root . --check src` (replace `src` with the product paths).
5. Ship `MIRROR.md` with the build, then run `python scripts/twin_delta_report.py --root .` so the user can see what changed versus an unconstrained build.
6. Never treat buildability as market validation. A working demo proves only that code can run.
7. Do not create investor, launch, board, partnership, rollout, or grant claim artifacts unless the latest `mvr/decision-log.json` entry authorizes that class.
8. Before export, run `python scripts/twin_fabrication_scan.py --root .`.

Full doctrine lives in `CLAUDE.md`. This file is the short universal entry point for agents that auto-read root `AGENTS.md`.
