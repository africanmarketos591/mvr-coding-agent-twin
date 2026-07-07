"""Offline tests for the claim gate's enforcement audit trail (mvr/gate-events.jsonl).

Contract: every claim-path decision (block or allow) leaves a receipt; non-claim writes
leave nothing; audit failures never change gate decisions (fail-silent by code review -
exercised here by asserting decisions match the base suite even when mvr/ is a file).
"""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "claim_gate.py")
FAILS = []


def run_hook(tool_input, project_dir, tool_name="Write"):
    p = subprocess.run([sys.executable, HOOK],
                       input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=project_dir))
    return p.returncode, p.stderr


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def events(project_dir):
    path = os.path.join(project_dir, "mvr", "gate-events.jsonl")
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def main():
    with tempfile.TemporaryDirectory() as d:
        # 1. Non-claim write leaves no receipt
        run_hook({"file_path": os.path.join(d, "src", "app.py")}, d)
        check("non-claim write leaves no audit event", events(d) == [])

        # 2. Block leaves a block receipt with class + reason
        rc, _ = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        ev = events(d)
        check("block is receipted", rc == 2 and len(ev) == 1 and ev[0]["event"] == "block"
              and ev[0]["claim_class"] == "capital_allocation" and ev[0]["reason"] == "no_decision_log")

        # 3. Authorized allow leaves an allow_claim receipt with entry_id
        os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
        json.dump([{"entry_id": "DL-audit", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []}}],
                  open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        rc, _ = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        ev = events(d)
        check("allow is receipted with entry_id", rc == 0 and ev[-1]["event"] == "allow_claim"
              and ev[-1]["entry_id"] == "DL-audit")

        # 4. Receipts are append-only accumulating
        check("receipts accumulate append-only", len(ev) == 2 and all("ts" in e for e in ev))

    # 5. Audit failure never changes the decision: make mvr/ unwritable-as-dir (a FILE)
    with tempfile.TemporaryDirectory() as d2:
        open(os.path.join(d2, "mvr"), "w").write("not a dir")
        rc, err = run_hook({"file_path": os.path.join(d2, "claims", "investor-deck.md")}, d2)
        check("audit failure still blocks correctly (fail-silent audit)", rc == 2 and "CLAIM GATE" in err)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}"); sys.exit(1)
    print("ALL PASS - gate audit trail contract verified.")


if __name__ == "__main__":
    main()
