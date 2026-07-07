"""Append a settlement entry to mvr/decision-log.json without hand-editing JSON.

This is intentionally small and boring: load the append-only decision log, validate
that it is a JSON array, append one settlement object, then atomically replace the
file. It prevents commas, quotes, or BOM quirks from bricking the claim gate.

Usage:
  python scripts/append_settlement.py --charter-ref CH-001 --outcome partial --summary "Pilot retained 3/5 launch sites" --source https://example.com/evidence
"""
import argparse
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone

VALID_OUTCOMES = {"hit", "miss", "partial", "unresolvable"}


def parse_args():
    parser = argparse.ArgumentParser(description="Append an MVR settlement entry.")
    parser.add_argument("--log", default=os.path.join("mvr", "decision-log.json"), help="Decision log path.")
    parser.add_argument("--charter-ref", required=True, help="Build Charter reference being settled.")
    parser.add_argument("--outcome", required=True, choices=sorted(VALID_OUTCOMES), help="Settlement outcome.")
    parser.add_argument("--summary", required=True, help="Short evidence-backed settlement summary.")
    parser.add_argument("--checkpoint", default="", help="Checkpoint date or label being settled.")
    parser.add_argument("--metric", action="append", default=[], help="Metric line. Repeat for multiple metrics.")
    parser.add_argument("--source", action="append", default=[], help="Evidence URL/file reference. Repeat for multiple sources.")
    parser.add_argument("--reviewed-by", default="human_reviewer", help="Reviewer label, not a private name unless approved.")
    return parser.parse_args()


def load_log(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise SystemExit(f"{path} must be a JSON array. Refusing to append.")
    return data


def atomic_write_json(path, data):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".decision-log.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main():
    args = parse_args()
    entries = load_log(args.log)
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "entry_id": f"SET-{uuid.uuid4()}",
        "entry_type": "settlement",
        "timestamp": now,
        "charter_ref": args.charter_ref,
        "settlement": {
            "settled": True,
            "outcome": args.outcome,
            "checkpoint": args.checkpoint,
            "summary": args.summary,
            "metrics": args.metric,
            "sources": args.source,
            "reviewed_by": args.reviewed_by,
        },
    }
    entries.append(entry)
    atomic_write_json(args.log, entries)
    print(json.dumps(entry, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
