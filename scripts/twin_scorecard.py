"""Render outcome delta from settled Twin and solo build ledgers.

This is a visibility layer, not kernel calibration. It reads settlement entries
and shows whether Twin-guided builds are surviving better than solo builds.
"""
import argparse
import json
import os

OUTCOMES = ("hit", "partial", "miss", "unresolvable")
ALIVE = {"hit", "partial"}


def load(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else []


def settlements(entries):
    for entry in entries:
        if entry.get("entry_type") != "settlement":
            continue
        settlement = entry.get("settlement") or {}
        if settlement.get("outcome") in OUTCOMES:
            yield entry, settlement


def base_by_ref(entries):
    base = {}
    for entry in entries:
        if entry.get("entry_type") != "settlement" and entry.get("charter_ref"):
            base[entry["charter_ref"]] = entry
    return base


def summarize(entries, force_mode=None):
    base = base_by_ref(entries)
    tally = {
        "twin": {outcome: 0 for outcome in OUTCOMES},
        "solo": {outcome: 0 for outcome in OUTCOMES},
    }
    rows = []
    for entry, settlement in settlements(entries):
        mode = force_mode or settlement.get("build_mode") or "twin"
        if mode not in tally:
            tally[mode] = {outcome: 0 for outcome in OUTCOMES}
        outcome = settlement["outcome"]
        tally[mode][outcome] += 1
        base_entry = base.get(entry.get("charter_ref"), {})
        rows.append({
            "charter": entry.get("charter_ref"),
            "mode": mode,
            "outcome": outcome,
            "archetype": base_entry.get("archetype", "?"),
            "preregistered": bool(base_entry.get("charter_hash")),
            "kernel_receipt": bool(base_entry.get("kernel_receipts")),
        })
    return rows, tally


def survival_rate(counts):
    resolved = counts["hit"] + counts["partial"] + counts["miss"]
    alive = counts["hit"] + counts["partial"]
    if not resolved:
        return None, resolved
    return round(100 * alive / resolved), resolved


def main():
    parser = argparse.ArgumentParser(description="Show Twin vs solo survival delta.")
    parser.add_argument("--log", default=os.path.join("mvr", "decision-log.json"))
    parser.add_argument("--solo-log")
    args = parser.parse_args()

    entries = load(args.log)
    rows, tally = summarize(entries)
    if args.solo_log:
        _solo_rows, solo_tally = summarize(load(args.solo_log), force_mode="solo")
        for outcome in OUTCOMES:
            tally["solo"][outcome] += solo_tally["solo"][outcome]

    print("=" * 64)
    print("MVR TWIN SCORECARD - outcome delta")
    print("=" * 64)
    if not rows and not any(tally["solo"].values()):
        print("No settled outcomes yet. Add reviewed settlements after t+90d.")
        print("This scorecard becomes useful when misses and hits are both recorded.")
        return

    for label in ("twin", "solo"):
        rate, resolved = survival_rate(tally[label])
        if resolved or any(tally[label].values()):
            print(
                f"  {label:4} builds: {resolved} resolved | ALIVE(hit+partial) {rate}% | "
                f"hit {tally[label]['hit']} partial {tally[label]['partial']} "
                f"miss {tally[label]['miss']} unresolved {tally[label]['unresolvable']}"
            )

    twin_rate, _ = survival_rate(tally["twin"])
    solo_rate, _ = survival_rate(tally["solo"])
    if twin_rate is not None and solo_rate is not None:
        print(f"\n  >>> SURVIVAL DELTA: twin-guided products survive {twin_rate - solo_rate} points more.")

    print("\n  per-charter:")
    for row in rows:
        flags = "preregistered" if row["preregistered"] else "UNREGISTERED"
        if row["kernel_receipt"]:
            flags += ", kernel-receipted"
        print(f"    [{row['mode']:4}] {row['outcome']:12} {str(row['charter'])[:34]:34} {row['archetype']:20} ({flags})")


if __name__ == "__main__":
    main()
