"""Read product telemetry into a draft-only settlement suggestion.

This script never writes `settled=true` and never records hit/miss. It produces a
human-reviewable `mvr/settlement-draft.json` from aggregate product usage.
"""
import argparse
import json
import os
from datetime import datetime, timezone


def load_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def load_buffer(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def latest_by_metric(rows):
    latest = {}
    for row in rows:
        metric = row.get("metric")
        if not metric or not row.get("ts"):
            continue
        timestamp = datetime.fromisoformat(row["ts"])
        if metric not in latest or timestamp > latest[metric][1]:
            latest[metric] = (row.get("value"), timestamp)
    return latest


def main():
    parser = argparse.ArgumentParser(description="Read a self-settling product's telemetry buffer.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--buffer", default="mvr_telemetry.buffer.jsonl")
    parser.add_argument("--max-age-days", type=int, default=90)
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    settlement_map = load_json(os.path.join(root, "mvr", "settlement_map.json"), None)
    if not settlement_map:
        print(f"no settlement_map.json under {os.path.join(root, 'mvr')}; run twin_instrument.py first")
        return

    rows = load_buffer(os.path.join(root, args.buffer))
    latest = latest_by_metric(rows)
    now = datetime.now(timezone.utc)

    per_criterion = []
    any_fresh = False
    any_seen = False
    for criterion in settlement_map.get("criteria", []):
        metric = criterion.get("metric")
        if metric in latest:
            any_seen = True
            value, timestamp = latest[metric]
            age_days = (now - timestamp).total_seconds() / 86400
            fresh = age_days <= args.max_age_days
            any_fresh = any_fresh or fresh
            state = f"ALIVE value={value} age={age_days:.0f}d" if fresh else f"STALE value={value} age={age_days:.0f}d"
        else:
            state = "SILENT no usage observed"
        per_criterion.append({
            "checkpoint": criterion.get("checkpoint"),
            "criterion": criterion.get("criterion"),
            "metric": metric,
            "state": state,
        })

    if not any_seen:
        suggestion = "presumed_dead"
    elif any_fresh:
        suggestion = "leading_life_needs_corroboration"
    else:
        suggestion = "inconclusive_stale_usage"

    draft = {
        "draft": True,
        "settled": None,
        "project_id": settlement_map.get("project_id"),
        "auto_suggestion": suggestion,
        "generated_at": now.isoformat(),
        "per_criterion": per_criterion,
        "cap": settlement_map.get("cap"),
        "how_to_settle": (
            "Corroborate with field signals, then append a reviewed settlement with "
            "scripts/append_settlement.py."
        ),
    }
    os.makedirs(os.path.join(root, "mvr"), exist_ok=True)
    with open(os.path.join(root, "mvr", "settlement-draft.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(draft, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print("=" * 60)
    print(f"SELF-SETTLEMENT DRAFT - {settlement_map.get('project_id')} ({suggestion})")
    print("=" * 60)
    for row in per_criterion:
        print(f"  [{row['checkpoint']}] {row['state']}")
        print(f"      <- {row['criterion']}")
    print("  DRAFT only: self-telemetry is capped and needs human review.")
    print(f"  wrote {os.path.join(root, 'mvr', 'settlement-draft.json')}")


if __name__ == "__main__":
    main()
