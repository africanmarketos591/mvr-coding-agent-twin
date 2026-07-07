"""Settlement daemon - schedulable draft worksheet generator.

This is the cron/Task Scheduler entrypoint for confession-free settlement pulses.
It finds due checkpoints, collects automatable public signals from
mvr/settlement-targets.json, and writes DRAFT settlement worksheets.

It never writes settlement.settled=true and never records hit/partial/miss. Human
countersign still happens through scripts/append_settlement.py.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "adapters"))
import pulse_collectors as pulse  # noqa: E402


HUMAN_ONLY_CHECKLIST = [
    "company/business registry status (country registrar)",
    "press/community mentions since charter date",
    "counterparty named in charter: still engaged? (one-line outreach)",
]


def load_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def due_checkpoints(entries, today):
    due = []
    for entry in entries:
        settlement = entry.get("settlement") or {}
        if settlement.get("settled"):
            continue
        for checkpoint in settlement.get("checkpoints", []):
            try:
                if datetime.fromisoformat(str(checkpoint["at"])).date() <= today:
                    due.append((entry, checkpoint))
            except Exception:
                continue
    return due


def safe_name(ref, checkpoint):
    name = f"{ref}__{checkpoint}".replace("/", "_").replace("\\", "_").replace(":", "-")
    return name or "unknown-charter"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=os.path.join("mvr", "decision-log.json"))
    parser.add_argument("--refresh", action="store_true", help="recollect even if a draft already exists")
    args = parser.parse_args()

    mvr_dir = os.path.dirname(os.path.abspath(args.log))
    entries = load_json(args.log, None)
    if not isinstance(entries, list):
        print(f"no readable decision log at {args.log}")
        sys.exit(1)

    targets_map = load_json(os.path.join(mvr_dir, "settlement-targets.json"), {})
    drafts_dir = os.path.join(mvr_dir, "settlement-drafts")
    os.makedirs(drafts_dir, exist_ok=True)

    due = due_checkpoints(entries, datetime.now(timezone.utc).date())
    if not due:
        print("No settlement checkpoints due. The ledger ages quietly.")
        return

    for entry, checkpoint in due:
        ref = entry.get("charter_ref", "unknown-charter")
        at = checkpoint.get("at", "na")
        draft_path = os.path.join(drafts_dir, f"{safe_name(ref, at)}.draft.json")
        if os.path.exists(draft_path) and not args.refresh:
            print(f"draft exists (skip): {draft_path}")
            continue
        targets = targets_map.get(ref, {})
        signals = pulse.collect(targets) if targets else []
        draft = {
            "draft": True,
            "settled": None,
            "charter_ref": ref,
            "charter_hash": entry.get("charter_hash"),
            "checkpoint": at,
            "criterion_written_pre_build": checkpoint.get("criterion"),
            "auto_pulse_signals": signals,
            "auto_suggestion": "presumed_dead" if pulse.presumed_dead(signals) else "inconclusive_needs_human",
            "human_checklist_outstanding": HUMAN_ONLY_CHECKLIST,
            "how_to_settle": (
                "gather the human checklist, then: python scripts/append_settlement.py "
                f"--charter-ref {ref} --outcome <hit|partial|miss|unresolvable> --summary ... --source ..."
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy": "observation_only_no_auto_settlement_no_kernel_mutation",
        }
        with open(draft_path, "w", encoding="utf-8") as handle:
            json.dump(draft, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        live = ", ".join(f"{s['signal']}={s['value']}" for s in signals) or "no auto-targets"
        print(f"DRAFT  {ref} @ {at}  [{live}]  suggestion={draft['auto_suggestion']}")
        print(f"       -> {draft_path}")

    print("\nDrafts are evidence, not verdicts. A human countersigns via append_settlement.py.")


if __name__ == "__main__":
    main()
