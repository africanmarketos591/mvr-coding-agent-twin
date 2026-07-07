"""Offline tests for the advisory response sentinel."""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hooks", "response_claim_sentinel.py"))
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def run(payload, project_dir):
    return subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=project_dir),
    )


def main():
    with tempfile.TemporaryDirectory() as d:
        p = run({"response": "We will launch a national escrow wallet and hold customer deposits."}, d)
        check("sentinel never blocks", p.returncode == 0)
        check("claim-shaped response emits advisory context", "RESPONSE SENTINEL" in p.stdout and "national_rollout" in p.stdout)
        receipt = os.path.join(d, "mvr", "response-sentinel.jsonl")
        check("sentinel writes advisory receipt", os.path.exists(receipt) and "response_claim_warning" in open(receipt, encoding="utf-8").read())

    with tempfile.TemporaryDirectory() as d:
        p = run({"response": "The build should start with an internal attendance data model."}, d)
        check("ordinary response is silent", p.returncode == 0 and not p.stdout.strip())

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - response sentinel contract verified.")


if __name__ == "__main__":
    main()
