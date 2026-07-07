"""Offline tests for the state producer side of the heartbeat protocol."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "spine"))
import mvr_client as spine

HEARTBEAT = os.path.join(ROOT, "hooks", "heartbeat.py")
SETTLE = os.path.join(ROOT, "scripts", "settle.py")
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def heartbeat(project_dir):
    p = subprocess.run(
        [sys.executable, HEARTBEAT],
        input="{}",
        capture_output=True,
        text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=project_dir),
    )
    try:
        return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


def main():
    with tempfile.TemporaryDirectory() as d:
        spine.update_state(
            "/v1/decision-check",
            {
                "verdict": "pilot_only",
                "confidence": 0.35,
                "decision_authorization": {
                    "authorized_use": ["internal_planning"],
                    "not_authorized_use": ["national_rollout"],
                },
                "evidence_gaps": ["guardian evidence missing"],
            },
            charter_ref="CH-state",
            passport_status="self_reported",
            project_dir=d,
        )
        state_path = os.path.join(d, "mvr", "state.json")
        state = json.load(open(state_path, encoding="utf-8"))
        check("spine writes state.json", state["verdict"] == "pilot_only" and state["charter_ref"] == "CH-state")
        check("state carries authorization", state["authorized_use"] == ["internal_planning"] and state["not_authorized_use"] == ["national_rollout"])
        context = heartbeat(d)
        check("heartbeat consumes produced state", "pilot_only" in context and "guardian evidence missing" in context)

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
        log_path = os.path.join(d, "mvr", "decision-log.json")
        json.dump([
            {
                "charter_ref": "CH-due",
                "settlement": {
                    "settled": False,
                    "checkpoints": [{"at": "2026-01-01", "criterion": "settle smoke"}],
                },
            }
        ], open(log_path, "w", encoding="utf-8"))
        p = subprocess.run([sys.executable, SETTLE, log_path], cwd=d, capture_output=True, text=True)
        check("settle exits clean", p.returncode == 0)
        state = json.load(open(os.path.join(d, "mvr", "state.json"), encoding="utf-8"))
        check("settle writes state.json", state["settlement_due_count"] == 1 and state["settlement_next"] == "2026-01-01")

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - state producer contract verified.")


if __name__ == "__main__":
    main()
