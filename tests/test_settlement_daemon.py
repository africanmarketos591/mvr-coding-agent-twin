"""Offline tests for settlement_daemon.py and pulse_collectors.py."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "adapters")))
import pulse_collectors as pulse  # noqa: E402


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def main():
    dead = [{"signal": "domain_resolves", "value": False}, {"signal": "url_alive", "value": False}]
    mixed = [{"signal": "domain_resolves", "value": False}, {"signal": "url_alive", "value": "unknown"}]
    alive = [{"signal": "domain_resolves", "value": True}]
    check("presumed_dead true when all dead", pulse.presumed_dead(dead) is True)
    check("presumed_dead false when any unknown", pulse.presumed_dead(mixed) is False)
    check("presumed_dead false when alive", pulse.presumed_dead(alive) is False)
    check("presumed_dead false when no signals", pulse.presumed_dead([]) is False)

    with tempfile.TemporaryDirectory() as d:
        mvr = os.path.join(d, "mvr")
        os.makedirs(mvr)
        log = os.path.join(mvr, "decision-log.json")
        with open(log, "w", encoding="utf-8") as handle:
            json.dump(
                [
                    {
                        "entry_id": "DL-1",
                        "charter_ref": "charter.md",
                        "settlement": {
                            "settled": None,
                            "checkpoints": [{"at": "2020-01-01", "criterion": "pilot alive"}],
                        },
                    }
                ],
                handle,
            )
        script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "settlement_daemon.py"))
        proc = subprocess.run([sys.executable, script, "--log", log], capture_output=True, text=True)
        check("daemon exits clean", proc.returncode == 0, proc.stderr[:120])
        drafts = os.path.join(mvr, "settlement-drafts")
        files = os.listdir(drafts) if os.path.isdir(drafts) else []
        check("a draft was written", len(files) == 1)
        if files:
            draft = json.load(open(os.path.join(drafts, files[0]), encoding="utf-8"))
            check("draft never settles", draft["settled"] is None and draft["draft"] is True)
            check("draft is observation-only", "no_auto_settlement" in draft["policy"])

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - settlement daemon is draft-only, no auto-settlement.")


if __name__ == "__main__":
    main()
