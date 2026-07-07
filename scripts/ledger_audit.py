"""Ledger audit + anchor recording - the auditor's one command.

AUDIT (default):
  python scripts/ledger_audit.py [mvr/decision-log.json]
For every decision-log entry carrying charter_ref+charter_hash it checks:
  1. the charter file exists;
  2. the canonical hash (preregister.py rules) matches the recorded charter_hash;
  3. anchor count (entry's anchor_refs + append-only anchor_update entries);
  4. INFLATION CHECK: any entry claiming settlement.preregistered=true with <2
     anchors is flagged as a FAIL - the ledger may never say more than reality.
Exit 0 = clean; exit 1 = integrity failure. Derived status is printed per charter:
  hash-verified | anchor-pending (n/2) | PREREGISTERED (derived, >=2 anchors)
Auditors trust the DERIVED status, never the flag.

ANCHOR RECORDING (append-only, per decision-log doctrine):
  python scripts/ledger_audit.py --add-anchor <ENTRY_ID> <ANCHOR_REF> [logpath]
Appends an anchor_update entry referencing ENTRY_ID. Original entries are never
mutated. When derived anchors reach 2, the audit reports PREREGISTERED.
"""
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preregister import digest_for  # noqa: E402


def load(path):
    with open(path, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise SystemExit(f"{path} must be a JSON array.")
    return data


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(prefix=".log.", suffix=".tmp", dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def derived_anchors(entries, entry):
    refs = list((entry.get("settlement") or {}).get("anchor_refs") or [])
    eid = entry.get("entry_id")
    for other in entries:
        if other.get("checkpoint") == "anchor_update" and other.get("references") == eid:
            ref = other.get("anchor_ref")
            if ref and ref not in refs:
                refs.append(ref)
    return refs


def audit(log_path):
    entries = load(log_path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(log_path)))  # project root (mvr/..)
    failures = []
    audited = 0
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("charter_hash"):
            continue
        audited += 1
        eid = entry.get("entry_id", "?")
        ref = entry.get("charter_ref", "")
        charter_path = ref if os.path.isabs(ref) else os.path.join(base, ref)
        if not os.path.exists(charter_path):
            # rehearsal folders may store charters relative to the log itself
            alt = os.path.join(os.path.dirname(os.path.abspath(log_path)), "..", ref)
            charter_path = alt if os.path.exists(alt) else charter_path
        if not os.path.exists(charter_path):
            failures.append(f"{eid}: charter file missing ({ref})")
            print(f"FAIL  {eid}  charter missing: {ref}")
            continue
        actual = digest_for(charter_path)
        recorded = str(entry.get("charter_hash", "")).lower()
        if actual != recorded:
            failures.append(f"{eid}: hash mismatch")
            print(f"FAIL  {eid}  hash mismatch: recorded {recorded[:12]}… actual {actual[:12]}…")
            continue
        anchors = derived_anchors(entries, entry)
        claimed = bool((entry.get("settlement") or {}).get("preregistered"))
        if claimed and len(anchors) < 2:
            failures.append(f"{eid}: claims preregistered with {len(anchors)} anchor(s)")
            print(f"FAIL  {eid}  INFLATION: preregistered=true but only {len(anchors)}/2 anchors")
            continue
        status = f"PREREGISTERED (derived, {len(anchors)} anchors)" if len(anchors) >= 2 \
            else f"anchor-pending ({len(anchors)}/2)"
        print(f"PASS  {eid}  hash-verified · {status}")
    print()
    if failures:
        print(f"LEDGER AUDIT FAIL ({len(failures)}): {failures}")
        sys.exit(1)
    print(f"LEDGER AUDIT CLEAN - {audited} charter entrie(s) hash-verified; derived statuses above are authoritative.")


def add_anchor(entry_id, anchor_ref, log_path):
    entries = load(log_path)
    if not any(isinstance(e, dict) and e.get("entry_id") == entry_id for e in entries):
        raise SystemExit(f"entry_id {entry_id} not found in {log_path}")
    entries.append({
        "entry_id": f"AU-{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checkpoint": "anchor_update",
        "references": entry_id,
        "anchor_ref": anchor_ref,
    })
    atomic_write(log_path, entries)
    target = next(e for e in entries if isinstance(e, dict) and e.get("entry_id") == entry_id)
    count = len(derived_anchors(entries, target))
    state = "PREREGISTERED (derived)" if count >= 2 else f"anchor-pending ({count}/2)"
    print(f"anchor recorded for {entry_id}: {anchor_ref}")
    print(f"derived status: {state}")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--add-anchor"]:
        if len(args) < 3:
            raise SystemExit("usage: ledger_audit.py --add-anchor <ENTRY_ID> <ANCHOR_REF> [logpath]")
        log_path = args[3] if len(args) > 3 else os.path.join("mvr", "decision-log.json")
        add_anchor(args[1], args[2], log_path)
        return
    log_path = args[0] if args else os.path.join("mvr", "decision-log.json")
    audit(log_path)


if __name__ == "__main__":
    main()
