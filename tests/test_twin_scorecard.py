"""Tests for the outcome-delta scorecard."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import twin_scorecard as S  # noqa: E402

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    entries = [
        {
            "entry_id": "DL-1",
            "charter_ref": "a.md",
            "charter_hash": "h",
            "archetype": "agritech_aggregator",
            "kernel_receipts": {"immutable_audit_hash": "x"},
        },
        {"entry_id": "DL-2", "charter_ref": "b.md", "charter_hash": "h"},
        {
            "entry_id": "S1",
            "entry_type": "settlement",
            "charter_ref": "a.md",
            "settlement": {"outcome": "hit", "build_mode": "twin"},
        },
        {
            "entry_id": "S2",
            "entry_type": "settlement",
            "charter_ref": "b.md",
            "settlement": {"outcome": "miss", "build_mode": "solo"},
        },
    ]
    rows, tally = S.summarize(entries)
    check("twin hit counted", tally["twin"]["hit"] == 1)
    check("solo miss counted", tally["solo"]["miss"] == 1)
    check("twin survival 100", S.survival_rate(tally["twin"])[0] == 100)
    check("solo survival 0", S.survival_rate(tally["solo"])[0] == 0)
    check("partial counts alive", S.survival_rate({"hit": 0, "partial": 1, "miss": 1, "unresolvable": 0})[0] == 50)
    check("unresolved only has no rate", S.survival_rate({"hit": 0, "partial": 0, "miss": 0, "unresolvable": 1})[0] is None)
    check("receipt flag exposed", any(row["kernel_receipt"] for row in rows))

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - scorecard computes survival delta.")


if __name__ == "__main__":
    main()
