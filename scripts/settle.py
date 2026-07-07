"""Settlement pulse runner - confession-free by doctrine.

Scans mvr/decision-log.json for entries with due, unsettled checkpoints and emits
the settlement worksheet per charter. It does NOT auto-settle - settlement facts are
gathered from channels that never depend on the user's honesty:
  1. instrumentation stream status (silence is data)
  2. public-record pulse (registry, app-store presence, domain, social dormancy, press)
  3. demand-side reports (fund/accelerator cohort records)
  4. renewal-moment capture (bonus, never a dependency)

Usage: python scripts/settle.py [path/to/decision-log.json]
"""
import json, os, sys, tempfile
from datetime import datetime, timezone

PULSE_CHECKLIST = [
    "instrumentation: events in last 30/60/90 days? (none since T => presumed dead at T)",
    "company/business registry status (country registrar)",
    "product surface alive? (domain resolves, app listing present, version date)",
    "social/comms dormancy (last public activity date)",
    "press/community mentions since charter date",
    "counterparty named in charter: still engaged? (one-line outreach, optional)",
]


def write_state(entries, due, log_path):
    # State lives NEXT TO the decision log, never relative to cwd - the settlement
    # daemon may run from anywhere; hooks resolve via CLAUDE_PROJECT_DIR, this
    # resolves via the log it just read. Same mvr/ dir either way.
    path = os.path.join(os.path.dirname(os.path.abspath(log_path)), "state.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state = {}
    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as handle:
                loaded = json.load(handle)
                if isinstance(loaded, dict):
                    state = loaded
    except Exception:
        state = {}
    state["last_settlement_run"] = datetime.now(timezone.utc).isoformat()
    state["settlement_due_count"] = len(due)
    if due:
        entry, checkpoint = due[0]
        state["settlement_next"] = checkpoint.get("at")
        state["charter_ref"] = entry.get("charter_ref") or state.get("charter_ref")
        state["top_blockers"] = [f"Settlement due for {entry.get('charter_ref')}: {checkpoint.get('criterion')}"]
    else:
        future = []
        now = datetime.now(timezone.utc).date()
        for entry in entries:
            settlement = entry.get("settlement") or {}
            if settlement.get("settled"):
                continue
            for checkpoint in settlement.get("checkpoints", []):
                try:
                    at = datetime.fromisoformat(checkpoint["at"]).date()
                    if at > now:
                        future.append((at, entry, checkpoint))
                except Exception:
                    continue
        if future:
            at, entry, checkpoint = sorted(future, key=lambda item: item[0])[0]
            state["settlement_next"] = checkpoint.get("at")
            state["charter_ref"] = entry.get("charter_ref") or state.get("charter_ref")
    fd, tmp_path = tempfile.mkstemp(prefix=".state.", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "mvr/decision-log.json"
    try:
        entries = json.load(open(path, encoding="utf-8-sig"))
    except FileNotFoundError:
        print(f"no decision log at {path}"); sys.exit(1)
    now = datetime.now(timezone.utc).date()
    due = []
    for e in entries:
        s = e.get("settlement") or {}
        if s.get("settled"):
            continue
        for cp in s.get("checkpoints", []):
            try:
                if datetime.fromisoformat(cp["at"]).date() <= now:
                    due.append((e, cp))
            except Exception:
                continue
    if not due:
        write_state(entries, due, path)
        print("No settlement checkpoints due. The ledger ages quietly."); return
    write_state(entries, due, path)
    for e, cp in due:
        print("=" * 70)
        print(f"DUE: {e.get('charter_ref')} | checkpoint {cp['at']}")
        print(f"criterion (written pre-build): {cp['criterion']}")
        print(f"verdict on record: {e.get('verdict')} (conf {e.get('confidence')}) | hash {e.get('kernel_receipts', {}).get('semantic_decision_hash', '')[:16]}")
        print("pulse checklist:")
        for item in PULSE_CHECKLIST:
            print(f"  [ ] {item}")
        print("outcome to append (new entry, never edit): settled: hit | miss | partial | unresolvable, with sources.")
        print("Misses are published with the same prominence as hits. That is the entire value of the ledger.")


if __name__ == "__main__":
    main()
