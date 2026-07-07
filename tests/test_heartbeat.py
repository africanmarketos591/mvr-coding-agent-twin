"""Offline tests for hooks/heartbeat.py - the counsel channel contract.

Contract: inject compact market state on every prompt when a case exists; fail SILENT
on every failure mode (counsel never bricks a session); staleness mirrors gate rules.
"""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone, timedelta

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "heartbeat.py")
FAILS = []


def run(project_dir):
    p = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=project_dir))
    return p.returncode, p.stdout


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def write_state(d, **over):
    os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
    s = {
        "verdict": "pilot_only", "confidence": 0.35,
        "authorized_use": ["internal_planning"], "not_authorized_use": ["national_rollout"],
        "top_blockers": ["consumer weighted sample 67 (minimum: 100)"],
        "passport_status": "self_reported", "calibrated_market": True,
        "last_kernel_sync": datetime.now(timezone.utc).isoformat(),
    }
    s.update(over)
    json.dump(s, open(os.path.join(d, "mvr", "state.json"), "w"))


def ctx(out):
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


def main():
    with tempfile.TemporaryDirectory() as d:
        # Pre-seed a stale nudge marker from a previous day: nudge must still fire
        # today AND clean the old marker (no marker accumulation).
        os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
        stale_marker = os.path.join(d, "mvr", ".twin-nudge-20200101")
        open(stale_marker, "w").close()
        rc, out = run(d)
        check("no case -> cold-start nudge fires once", rc == 0 and "pre-charter committee" in ctx(out))
        check("stale nudge markers cleaned up", not os.path.exists(stale_marker))
        rc, out = run(d)
        check("nudge suppressed same day (marker)", rc == 0 and out.strip() == "")

        write_state(d)
        rc, out = run(d)
        c = ctx(out)
        check("fresh state injects digest", rc == 0 and "pilot_only" in c and "sample 67" in c)
        check("digest carries authorization", "internal_planning" in c and "national_rollout" in c)
        check("digest within budget", len(c.split()) <= 120, f"{len(c.split())} words")

        # DIFFERENTIAL MODE: same state re-injected -> one-line tag, not full digest
        rc, out = run(d)
        c2 = ctx(out)
        check("unchanged state emits differential tag", "state unchanged" in c2 and "pilot_only" in c2)
        check("tag is one line and short", "\n" not in c2 and len(c2.split()) <= 20, f"{len(c2.split())} words")

        write_state(d, last_kernel_sync=(datetime.now(timezone.utc) - timedelta(days=10)).isoformat())
        rc, out = run(d)
        check("stale >7d flagged", "Stale: 10d" in ctx(out))

        write_state(d, last_kernel_sync=(datetime.now(timezone.utc) - timedelta(days=40)).isoformat())
        rc, out = run(d)
        check("expired >30d declares authorization void", "STATE EXPIRED" in ctx(out) and "void" in ctx(out))
        rc, out = run(d)
        check("expired state NEVER compressed to tag (safety lines full, always)", "STATE EXPIRED" in ctx(out))

        write_state(d, calibrated_market=False)
        rc, out = run(d)
        check("uncalibrated market downgrades to lens-only", "UNCALIBRATED" in ctx(out))

        write_state(d, settled_summary="12 charters settled: pilot-survival 3.1x control base rate; 2 misses published")
        rc, out = run(d)
        check("borrowed consequences injected when settlements exist", "Track record: 12 charters settled" in ctx(out))

        with open(os.path.join(d, "mvr", "state.json"), "w") as f:
            f.write("{corrupt")
        rc, out = run(d)
        check("corrupt state fails SILENT (counsel, not authority)", rc == 0 and out.strip() == "")

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}"); sys.exit(1)
    print("ALL PASS - heartbeat counsel contract verified.")


if __name__ == "__main__":
    main()
