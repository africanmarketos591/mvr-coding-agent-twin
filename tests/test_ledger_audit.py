"""Offline tests for scripts/ledger_audit.py - the auditor's one command."""
import json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone

SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
AUDIT = os.path.join(SCRIPTS, "ledger_audit.py")
PRE = os.path.join(SCRIPTS, "preregister.py")
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def run(*args):
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "mvr"))
        os.makedirs(os.path.join(d, "charters"))
        ch = os.path.join(d, "charters", "CH-1.md")
        open(ch, "w", encoding="utf-8").write(
            "# CH-1\n**Preregistration hash:** {{sha256}} (anchors: {{anchor_refs}})\n\npilot live in 1 school\n")
        rc, out = run(PRE, ch)
        h = re.search(r'"sha256": "([0-9a-f]{64})"', out).group(1)
        s = open(ch, encoding="utf-8").read().replace(
            "**Preregistration hash:** {{sha256}} (anchors: {{anchor_refs}})",
            f"**Preregistration hash:** {h} (anchors: <pending>)")
        open(ch, "w", encoding="utf-8").write(s)
        log = os.path.join(d, "mvr", "decision-log.json")
        json.dump([{"entry_id": "DL-1", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "charter_ref": os.path.join("charters", "CH-1.md"), "charter_hash": h,
                    "settlement": {"preregistered": False, "anchor_refs": []}}],
                  open(log, "w"))

        rc, out = run(AUDIT, log)
        check("clean ledger audits clean", rc == 0 and "anchor-pending (0/2)" in out)

        # tamper charter -> audit fails
        open(ch, "a", encoding="utf-8").write("changed prediction\n")
        rc, out = run(AUDIT, log)
        check("tampered charter fails audit", rc == 1 and "hash mismatch" in out)
        open(ch, "w", encoding="utf-8").write(s)  # restore

        # inflation: preregistered=true with 0 anchors -> FAIL
        entries = json.load(open(log)); entries[0]["settlement"]["preregistered"] = True
        json.dump(entries, open(log, "w"))
        rc, out = run(AUDIT, log)
        check("inflation flagged (preregistered without anchors)", rc == 1 and "INFLATION" in out)
        entries[0]["settlement"]["preregistered"] = False; json.dump(entries, open(log, "w"))

        # append-only anchor recording -> derived PREREGISTERED at 2
        rc, out = run(AUDIT, "--add-anchor", "DL-1", "git:abc123", log)
        check("first anchor recorded, still pending", rc == 0 and "anchor-pending (1/2)" in out)
        rc, out = run(AUDIT, "--add-anchor", "DL-1", "https://web.archive.org/xyz", log)
        check("second anchor derives PREREGISTERED", rc == 0 and "PREREGISTERED (derived)" in out)
        rc, out = run(AUDIT, log)
        check("audit shows derived PREREGISTERED, original entry unmutated",
              rc == 0 and "PREREGISTERED (derived, 2 anchors)" in out
              and json.load(open(log))[0]["settlement"]["preregistered"] is False)
        check("anchor updates are append-only entries", len(json.load(open(log))) == 3)

        # unknown entry id rejected
        rc, out = run(AUDIT, "--add-anchor", "DL-none", "x", log)
        check("unknown entry_id rejected", rc != 0)

        # duplicate preregistration headers must fail closed through preregister.py
        dup = os.path.join(d, "charters", "CH-dup.md")
        open(dup, "w", encoding="utf-8").write(
            "# CH-dup\n"
            "**Preregistration hash:** {{sha256}} (anchors: pending)\n\n"
            "**Preregistration hash:** 0000000000000000000000000000000000000000000000000000000000000000 (anchors: fake)\n"
        )
        rc, out = run(PRE, dup)
        check("duplicate-header attack fails closed", rc != 0 and "expected exactly one" in out)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}"); sys.exit(1)
    print("ALL PASS - ledger audit contract verified.")


if __name__ == "__main__":
    main()
