"""Calibration bridge: submit settled outcomes to governed kernel review.

The Twin observes and packages outcomes; the kernel decides when evidence becomes
calibration. POST /v1/outcome-feedback accepts real-world outcome feedback into a
review queue without automatically changing the engine.

Default mode is dry-run. Use --submit only for real, settled outcomes.
"""
import argparse
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spine"))
import mvr_client as c  # noqa: E402


VALID_OUTCOMES = {"hit", "partial", "miss", "unresolvable"}


def load(path):
    with open(path, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise SystemExit(f"{path} must be a JSON array")
    return data


def base_for(entries, settlement):
    ref = settlement.get("charter_ref")
    charter_hash = settlement.get("charter_hash")
    best = {}
    for entry in entries:
        if entry.get("entry_type") == "settlement":
            continue
        if (ref and entry.get("charter_ref") == ref) or (charter_hash and entry.get("charter_hash") == charter_hash):
            best = entry
    return best


def missing_required(payload):
    missing = []
    if not (payload.get("entity_name") or payload.get("project_id") or payload.get("decision_id")):
        missing.append("target_identity(entity_name|project_id|decision_id)")
    if not (payload.get("predicted_verdict") or payload.get("decision_reference")):
        missing.append("predicted_verdict|decision_reference")
    if not payload.get("actual_outcome"):
        missing.append("actual_outcome")
    if not (payload.get("outcome_date") or payload.get("observed_at")):
        missing.append("outcome_date|observed_at")
    return missing


def build_payload(entries, settlement_entry, entity=None, project=None):
    settlement = settlement_entry.get("settlement") or {}
    base = base_for(entries, settlement_entry)
    ref = settlement_entry.get("charter_ref") or base.get("charter_ref") or "unknown-charter"
    ts = settlement_entry.get("timestamp", "")
    return {
        "entity_name": entity or base.get("entity_name"),
        "project_id": project or ref.rsplit("/", 1)[-1].replace(".md", ""),
        "decision_reference": base.get("charter_hash") or settlement_entry.get("charter_hash"),
        "predicted_verdict": base.get("verdict"),
        "archetype": base.get("archetype"),
        "market_scope": base.get("market_scope"),
        "actual_outcome": settlement.get("outcome"),
        "outcome_date": ts[:10] if ts else None,
        "summary": settlement.get("summary", ""),
        "sources": (settlement.get("sources") or [])[:5],
        "calibration_note": "submitted for governed review; kernel decides calibration, not this client",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=os.path.join("mvr", "decision-log.json"))
    parser.add_argument("--entity", default=None, help="entity_name if not present in the base entry")
    parser.add_argument("--project", default=None, help="project_id override; default is the charter file stem")
    parser.add_argument("--submit", action="store_true", help="actually POST; default is dry-run")
    args = parser.parse_args()

    entries = load(args.log)
    settled = [
        entry for entry in entries
        if entry.get("entry_type") == "settlement"
        and (entry.get("settlement") or {}).get("outcome") in VALID_OUTCOMES
    ]
    if not settled:
        print("No settled outcomes to submit.")
        return

    mode = "SUBMIT" if args.submit else "DRY-RUN (no network write)"
    print(f"outcome-feedback bridge - mode: {mode}\n")
    receipts_path = os.path.join(os.path.dirname(os.path.abspath(args.log)), "outcome-submissions.jsonl")
    exit_code = 0
    for entry in settled:
        payload = build_payload(entries, entry, args.entity, args.project)
        missing = missing_required(payload)
        if missing:
            print(f"SKIP  {payload.get('project_id')}: missing {missing}")
            exit_code = 1
            continue
        if not args.submit:
            print(
                f"WOULD-SUBMIT  {payload['project_id']} outcome={payload['actual_outcome']} "
                f"predicted={payload['predicted_verdict']}"
            )
            print("  payload:", json.dumps(payload, ensure_ascii=False))
            continue
        _, status, body = c.call("/v1/outcome-feedback", payload, idempotency_key=f"of-{uuid.uuid4()}")
        impact = body.get("calibration_impact", "unknown") if isinstance(body, dict) else "unknown"
        print(f"SUBMIT  {payload['project_id']} -> status={status} calibration_impact={impact}")
        try:
            with open(receipts_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({
                    "project_id": payload["project_id"],
                    "status": status,
                    "calibration_impact": impact,
                    "public_receipt_hash": (body or {}).get("public_receipt_hash"),
                }, ensure_ascii=False) + "\n")
        except Exception:
            pass
        if status not in (200, 201, 202):
            exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
