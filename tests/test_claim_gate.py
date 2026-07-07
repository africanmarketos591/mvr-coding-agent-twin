"""Offline tests for hooks/claim_gate.py - exercises the authority-at-the-gates contract.

Runs the hook as a subprocess exactly as the harness would (JSON on stdin), against a
temp project dir with controlled decision logs. No network required.
"""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone, timedelta

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "claim_gate.py")
FAILS = []


def run_hook(tool_input, project_dir, tool_name="Write"):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project_dir)
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
        capture_output=True, text=True, env=env,
    )
    return p.returncode, p.stderr


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def write_log(project_dir, authorized, ts=None, entries=None):
    os.makedirs(os.path.join(project_dir, "mvr"), exist_ok=True)
    entry = {
        "entry_id": "DL-test", "timestamp": ts or datetime.now(timezone.utc).isoformat(),
        "decision_authorization": {"authorized_use": authorized, "not_authorized_use": ["national_rollout"]},
        "evidence_gaps": ["consumer weighted sample 67 (minimum: 100)"],
    }
    with open(os.path.join(project_dir, "mvr", "decision-log.json"), "w") as f:
        json.dump(entries or [entry], f)


def main():
    with tempfile.TemporaryDirectory() as d:
        # 1. Code is never gated
        rc, _ = run_hook({"file_path": os.path.join(d, "src", "app.py")}, d)
        check("code write allowed (no log needed)", rc == 0)

        # 2. Claim artifact with NO log -> block
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("claim blocked when no decision log", rc == 2 and "decision-log.json does not exist" in err)

        # 3. Claim with log lacking authorization -> block, message names the gap
        write_log(d, ["internal_planning"])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("unauthorized claim blocked", rc == 2 and "capital_allocation" in err)
        check("block message carries evidence gaps", "sample 67" in err)

        # 4. Claim WITH authorization -> allowed
        write_log(d, ["internal_planning", "capital_allocation"])
        rc, _ = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("authorized claim allowed", rc == 0)

        # 4b. Unsigned required human review cannot authorize even if authorized_use says yes
        unsigned_review = {
            "entry_id": "unsigned", "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []},
            "human_review": {"required": True, "reviewer": None, "signature_ref": None},
        }
        write_log(d, [], entries=[unsigned_review])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("unsigned required human review blocks", rc == 2 and "human_review.required=true" in err)

        # 4c. Local authorized_use cannot exceed kernel_authorized_use unless marked as a signed override
        ambiguous_local = {
            "entry_id": "ambiguous", "timestamp": datetime.now(timezone.utc).isoformat(),
            "kernel_authorized_use": ["internal_planning"],
            "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []},
        }
        write_log(d, [], entries=[ambiguous_local])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("ambiguous local authorization blocks", rc == 2 and "not in kernel_authorized_use" in err)

        # 4d. Explicit named-human override can allow, but is receipted distinctly
        explicit_override = {
            "entry_id": "override", "timestamp": datetime.now(timezone.utc).isoformat(),
            "kernel_authorized_use": ["internal_planning"],
            "authorization_basis": "named_human_override",
            "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []},
            "human_review": {"required": True, "reviewer": "test_reviewer", "signature_ref": "sig-test"},
            "override_note": "Local-only override for test; kernel did not authorize this claim class.",
        }
        write_log(d, [], entries=[explicit_override])
        rc, _ = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        events = [json.loads(x) for x in open(os.path.join(d, "mvr", "gate-events.jsonl"), encoding="utf-8") if x.strip()]
        check("explicit override allowed", rc == 0)
        check("override receipted distinctly", any(e.get("event") == "allow_override_claim" and e.get("entry_id") == "override" for e in events))

        # 5. Stale log (>30d) -> block even if authorized, with renewal path + last known gaps
        old = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        write_log(d, ["capital_allocation"], ts=old)
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("stale authorization blocked", rc == 2 and "days old" in err)
        check("stale block carries renewal path + last known gaps",
              "Renewal path" in err and "sample 67" in err)

        # 6. Unclassified claims/ artifact -> block with naming instruction
        write_log(d, ["capital_allocation"])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "misc-notes.md")}, d)
        check("unclassified claim artifact blocked", rc == 2 and "no known claim class" in err)

        # 7. Corrupt log -> fail CLOSED for claims
        with open(os.path.join(d, "mvr", "decision-log.json"), "w") as f:
            f.write("{not json")
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "board-pack.md")}, d)
        check("corrupt log fails closed", rc == 2 and "unreadable" in err)

        # 8. Non-write tools pass through
        p = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": os.path.join(d, "claims", "x.md")}}),
                           capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
        check("read never gated", p.returncode == 0)

        # 9. Hook covers MultiEdit and Windows-style paths
        write_log(d, ["capital_allocation"])
        rc, _ = run_hook({"file_path": "claims\\investor-deck.md"}, d, tool_name="MultiEdit")
        check("MultiEdit Windows claim path allowed only with authorization", rc == 0)

        # 10. String authorization must be exact, not substring membership
        write_log(d, "not_capital_allocation")
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("string authorization does not allow substring bypass", rc == 2 and "capital_allocation" in err)

        # 11. Latest entry is authoritative
        old_entry = {
            "entry_id": "old", "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []},
        }
        latest_entry = {
            "entry_id": "latest", "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_authorization": {"authorized_use": ["internal_planning"], "not_authorized_use": ["capital_allocation"]},
        }
        write_log(d, [], entries=[old_entry, latest_entry])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "investor-deck.md")}, d)
        check("latest decision-log entry wins", rc == 2 and "NOT in authorized_use" in err)

        # 12. Malformed latest entry fails closed
        write_log(d, [], entries=[latest_entry, "not-an-object"])
        rc, err = run_hook({"file_path": os.path.join(d, "claims", "board-pack.md")}, d)
        check("malformed latest entry fails closed", rc == 2 and "not an object" in err)

        # 13. Windows/Powershell UTF-8 BOM logs are readable
        bom_entry = {
            "entry_id": "bom", "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_authorization": {"authorized_use": ["board_reporting"], "not_authorized_use": []},
        }
        with open(os.path.join(d, "mvr", "decision-log.json"), "w", encoding="utf-8-sig") as f:
            json.dump([bom_entry], f)
        rc, _ = run_hook({"file_path": os.path.join(d, "claims", "board-pack.md")}, d)
        check("UTF-8 BOM decision log allowed", rc == 0)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - claim gate contract verified.")


if __name__ == "__main__":
    main()
