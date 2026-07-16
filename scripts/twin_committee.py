"""Run the PRE-CHARTER MVR Twin committee in one command.

This is orchestration, not judgment. It performs the deterministic spine calls,
unions the evidence bill across archetypes, and emits the packet a host model
needs before writing a Build Charter:

  - mvr/committee_packet.json
  - charter.draft.md
  - mvr/decision-log.seed.json

The model still writes the pivot, fitted build, source ledger, and settlement
criteria. This script never authorizes a claim. If the kernel is unreachable,
the packet is marked provisional and claim authorization remains impossible.
"""
import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "spine"))

import mvr_client as c  # noqa: E402
import twin_claim_coverage as claim_coverage  # noqa: E402


def load_key(keyfile):
    if not keyfile:
        return
    from keyfile_loader import extract_mvr_api_key  # noqa: E402

    with open(keyfile, encoding="utf-8-sig") as handle:
        os.environ["MVR_API_KEY"] = extract_mvr_api_key(handle.read())


def safe_call(fn, *args):
    try:
        return fn(*args)
    except Exception as exc:
        return 0, 0, {
            "error": "spine_call_failed",
            "detail": str(exc)[:240],
            "outage_rule": (
                "Build proceeds; charter provisional; claim authorization impossible "
                "until the kernel is reachable. Do not simulate verdicts locally."
            ),
        }


def union_evidence(playbooks):
    lanes = {}
    for playbook in playbooks:
        for lane in playbook.get("required_local_evidence") or []:
            key = lane.get("stakeholder_class") or lane.get("lane") or lane.get("name")
            if not key:
                continue
            existing = lanes.get(key)
            minimum = lane.get("minimum_signal_count", 0) or 0
            existing_minimum = (existing or {}).get("minimum_signal_count", 0) or 0
            if existing is None or minimum > existing_minimum:
                lanes[key] = lane
    return list(lanes.values())


def extract_receipts(**responses):
    receipts = {}
    for label, response in responses.items():
        if not isinstance(response, dict):
            continue
        for key in (
            "immutable_audit_hash",
            "provenance_hash",
            "response_hash",
            "semantic_hash",
            "decision_check_id",
        ):
            if response.get(key):
                output_key = key if key not in receipts else f"{label}_{key}"
                receipts[output_key] = response[key]
    return receipts


def add_guardian_tiers(guardian_map, tiers):
    seen = {
        item.get("guardian_tier") or item.get("tier") or item.get("name")
        for item in guardian_map
        if isinstance(item, dict)
    }
    for tier in tiers or []:
        if not isinstance(tier, dict):
            continue
        key = tier.get("guardian_tier") or tier.get("tier") or tier.get("name")
        if key and key not in seen:
            guardian_map.append(tier)
            seen.add(key)


def market_country(market):
    match = re.search(r"(?:^|[^A-Z])([A-Z]{2})(?:$|[^A-Z])", str(market).upper())
    return match.group(1) if match else None


def write_json(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def draft_charter(args, packet, seed_entry_id):
    guardian_tiers = [
        str(item.get("guardian_tier") or item.get("tier") or item.get("name"))
        for item in packet["guardian_map"]
        if isinstance(item, dict)
    ]
    board_questions = packet["board_questions"][:4]
    evidence_bill = packet["evidence_bill"]
    rows = []
    for lane in evidence_bill:
        fields = lane.get("required_fields") or lane.get("fields") or []
        if not isinstance(fields, list):
            fields = [str(fields)]
        rows.append(
            "| {stakeholder} | >={minimum} signals | {fields} |".format(
                stakeholder=lane.get("stakeholder_class") or lane.get("lane") or lane.get("name") or "unknown",
                minimum=lane.get("minimum_signal_count", "unknown"),
                fields=", ".join(str(field) for field in fields[:4]) or "see playbook",
            )
        )
    if not rows:
        rows.append("| kernel_unavailable_or_no_lanes | unknown | rerun committee when spine is reachable |")

    capability_rows = []
    for item in ((packet.get("claim_coverage") or {}).get("material_capabilities") or []):
        if not isinstance(item, dict) or not item.get("capability"):
            continue
        capability_rows.append(
            "| `{capability}` | pending_evidence | Replace this placeholder with the exact build boundary; "
            "pending_evidence means do not implement it. | |".format(capability=item["capability"])
        )
    if not capability_rows:
        capability_rows.append("| - | - | No material capability recognized from the brief. | |")

    calibration = packet.get("calibration_scope") or {}
    uncalibrated = calibration.get("verdict") == "uncalibrated"
    if packet["provisional"]:
        status_line = "PROVISIONAL - spine unavailable or calibration unknown; no claim authorization."
        status_choices = "provisional_not_authorized"
    elif uncalibrated:
        status_line = "Spine sat, but the market is outside calibrated scope; Law 6 requires lens-only reasoning."
        status_choices = "uncalibrated_lens_only"
    else:
        status_line = (
            "Spine sat, but this committee seed authorizes internal planning only. "
            "A later decision entry is required before any pilot or build-authorized status."
        )
        status_choices = "{internal_planning_only|redirected}"
    provisional_rule = (
        "\n> PROVISIONAL RULE: do not change Status to build_authorized, and do not place regulated "
        "implementation details in scaffold/export surfaces until a non-empty kernel receipt exists."
        if packet["provisional"]
        else (
            "\n> LAW 6: this market is outside measured calibration scope. Use lens-only reasoning, label "
            "all market judgments uncalibrated, and do not trade them as kernel measurement."
            if uncalibrated else ""
        )
    )

    return f"""# BUILD CHARTER - {{PROJECT}} (DRAFT)
**Charter ID:** CH-{uuid.uuid4()} | **Date:** {datetime.now(timezone.utc).date()} | **Archetype:** {', '.join(args.archetype)} | **Market:** {args.market}
**Status:** {status_choices} | **Preregistration hash:** {{canonical_sha256}} (anchors: {{anchor_refs}})

> Committee packet: `mvr/committee_packet.json`. Decision-log seed: `{seed_entry_id}`. {status_line}
{provisional_rule}

## PIVOT EXPLANATION (model writes <=3 sentences before the charter)
{{MODEL: binding constraint; what was preserved; what stays legal or possible today}}

## 1. The idea as received
> {args.idea}

## 2. What we researched
Guardian veto surface: {', '.join(guardian_tiers) or 'kernel unavailable'}

Board questions:
{chr(10).join(f'- {question}' for question in board_questions) or '- Rerun committee when playbooks are reachable.'}

Source ledger requirement: every named incumbent, regulation, licensing claim, figure, failure precedent, capital number, or health/credit/legal constraint must carry source/date or be marked `UNKNOWN - not verified`.

## 3. What the evidence machine said (quoted, not paraphrased)
- claim_coverage: {json.dumps(packet.get('claim_coverage', {}), ensure_ascii=False)}
- calibration_scope: {json.dumps(calibration, ensure_ascii=False)}
- unsafe_claims: {json.dumps(packet['sparring'].get('unsafe_claims', []), ensure_ascii=False)}
- evidence_required: {json.dumps(packet['sparring'].get('evidence_required', []), ensure_ascii=False)}
- abstention_reason_codes: {json.dumps(packet['sparring'].get('abstention_reason_codes', []), ensure_ascii=False)}
- kernel_receipts: {json.dumps(packet['kernel_receipts'], ensure_ascii=False)}

## 4. Who you are in this build (from passport or inference)
Operator seat: {packet['seats_sat']['operator']}. Self-reported reach remains at 0.30 until field-signal attestation.

## 5. THE BUILD (model writes the fitted, smallest falsifiable wedge)
{{MODEL}}

### 5A. Material capability disposition (complete every recognized row before code)
Allowed dispositions: `internal_simulation_only`, `redirected`, `forbidden`, `pending_evidence`, or
`separately_authorized`. An internal simulation must name its synthetic-data/live-action boundary.
Separately authorized work must cite the exact reference bound in the decision log's
`decision_authorization.capability_authorizations`; the charter cannot authorize itself.

| Capability | Disposition | Exact boundary | Authorization ref |
|---|---|---|---|
{chr(10).join(capability_rows)}

## 6. Redirect (only if the original idea did not survive)
{{MODEL}}

## 7. Claims you may not make yet
Unless a later decision-log entry authorizes them, the default non-authorized classes remain: national_rollout, capital_allocation, board_reporting, partnership_claims.

## 7A. Evidence still missing before stronger claims
| Lane / stakeholder | Minimum | Key fields |
|---|---|---|
{chr(10).join(rows)}

## 8. Settlement (model writes t+90d / t+365d criteria before the build)
{{MODEL}}
"""


def main():
    parser = argparse.ArgumentParser(description="Run the PRE-CHARTER MVR Twin committee.")
    parser.add_argument("--idea", required=True)
    parser.add_argument(
        "--brief-file",
        help="Preserved verbatim user brief inside --root; required for audit-ready export.",
    )
    parser.add_argument("--archetype", action="append", required=True, default=[])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--market", required=True)
    parser.add_argument("--claim", action="append", default=[])
    parser.add_argument("--claims-file")
    parser.add_argument("--keyfile")
    parser.add_argument("--root", default=os.getcwd())
    args = parser.parse_args()

    load_key(args.keyfile)

    supplied_claims = list(args.claim)
    if args.claims_file:
        with open(args.claims_file, encoding="utf-8-sig") as handle:
            supplied_claims.extend(line.strip() for line in handle if line.strip())

    root = os.path.abspath(args.root)
    os.environ["CLAUDE_PROJECT_DIR"] = root
    mvr_dir = os.path.join(root, "mvr")
    checkpoints_dir = os.path.join(mvr_dir, "checkpoints")
    brief_text = args.idea
    brief_source = {"kind": "inline_unverified", "path": None}
    if args.brief_file:
        brief_path = os.path.abspath(
            args.brief_file if os.path.isabs(args.brief_file) else os.path.join(root, args.brief_file)
        )
        try:
            brief_inside = os.path.commonpath([root, brief_path]) == root
        except ValueError:
            brief_inside = False
        if not brief_inside or not os.path.isfile(brief_path):
            raise SystemExit("--brief-file must exist inside --root")
        with open(brief_path, encoding="utf-8-sig") as handle:
            brief_text = handle.read()
        brief_source = {
            "kind": "file",
            "path": os.path.relpath(brief_path, root).replace("\\", "/"),
        }
    claims, coverage = claim_coverage.build_coverage(
        brief_text,
        brief_source,
        supplied_claims,
        args.subject,
    )
    os.makedirs(checkpoints_dir, exist_ok=True)

    _latency, schema_status, schema = safe_call(c.schema)
    provisional = schema_status != 200

    country = market_country(args.market)
    calibration_response = {}
    calibration_scope = {
        "verdict": "unknown",
        "coverage_tier": None,
        "source": "kernel_decision_check.response_meta.country_calibration_scope",
        "boundary": "calibration could not be measured; provisional only",
    }
    if country and args.archetype:
        _latency, calibration_status, calibration_response = safe_call(
            c.calibration_probe,
            args.subject,
            args.archetype[0],
            country,
        )
        if calibration_status == 200 and isinstance(calibration_response, dict):
            calibration_scope = c.calibration_scope_from_response(calibration_response)
            calibration_scope["country"] = country
            write_json(os.path.join(checkpoints_dir, "calibration_scope.json"), {
                "scope": calibration_scope,
                "kernel_response": calibration_response,
            })
            if calibration_scope.get("verdict") == "unknown":
                provisional = True
        else:
            provisional = True
    else:
        provisional = True

    playbooks = []
    guardian_map = []
    for archetype in args.archetype:
        _latency, status, playbook = safe_call(c.category_playbook, archetype)
        if status == 200 and isinstance(playbook, dict):
            playbooks.append(playbook)
            if playbook.get("minimum_guardian_map"):
                add_guardian_tiers(guardian_map, playbook.get("minimum_guardian_map") or [])
            write_json(os.path.join(checkpoints_dir, f"playbook_{archetype}.json"), playbook)
        else:
            provisional = True

    _latency, sparring_status, sparring = safe_call(c.strategy_sparring, claims, args.subject, args.market)
    if sparring_status == 200 and isinstance(sparring, dict):
        write_json(os.path.join(checkpoints_dir, "strategy_sparring.json"), sparring)
    else:
        provisional = True
        if not isinstance(sparring, dict):
            sparring = {"error": "strategy_sparring_unavailable"}

    packet = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kernel_version": schema.get("api_version") if isinstance(schema, dict) else None,
        "provisional": provisional,
        "archetypes": args.archetype,
        "subject": args.subject,
        "market_scope": args.market,
        "calibration_scope": calibration_scope,
        "claims_sent": claims,
        "claim_coverage": coverage,
        "guardian_map": guardian_map,
        "evidence_bill": union_evidence(playbooks),
        "sparring": {
            "unsafe_claims": sparring.get("unsafe_claims") or [],
            "evidence_required": sparring.get("evidence_required") or [],
            "abstention_reason_codes": sparring.get("abstention_reason_codes") or [],
            "challenges": (sparring.get("challenges") or [])[:10],
        },
        "board_questions": (playbooks[0].get("board_questions") if playbooks else []) or [],
        "seats_sat": {
            "advocate": "model",
            "research": "model",
            "spine": not provisional,
            "operator": "passport" if os.path.exists(os.path.join(mvr_dir, "passport.json")) else "inference_0.30",
        },
        "kernel_receipts": extract_receipts(
            strategy_sparring=sparring,
            calibration_probe=calibration_response,
            schema=schema,
        ),
    }

    write_json(os.path.join(mvr_dir, "committee_packet.json"), packet)

    seed_entry = {
        "entry_id": f"DL-{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checkpoint": "pre_charter",
        "charter_ref": "charter.md",
        "archetype": args.archetype[0] if args.archetype else None,
        "market_scope": args.market,
        "redirect_pattern": "<model sets if redirected>",
        "verdict": (
            "uncalibrated"
            if packet["calibration_scope"].get("verdict") == "uncalibrated"
            else ("abstained" if packet["sparring"]["abstention_reason_codes"] else "pending")
        ),
        "calibration_scope": packet["calibration_scope"],
        "abstention_reason_codes": packet["sparring"]["abstention_reason_codes"],
        "kernel_receipts": packet["kernel_receipts"],
        "decision_authorization": {
            "authorized_use": ["internal_planning"],
            "not_authorized_use": [
                "national_rollout",
                "capital_allocation",
                "board_reporting",
                "partnership_claims",
            ],
        },
    }
    write_json(os.path.join(mvr_dir, "decision-log.seed.json"), [seed_entry])

    draft = draft_charter(args, packet, seed_entry["entry_id"])
    with open(os.path.join(root, "charter.draft.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(draft)

    status = "SPINE_OK" if packet["seats_sat"]["spine"] else "SPINE_OUTAGE_PROVISIONAL"
    abstention = ", ".join(packet["sparring"]["abstention_reason_codes"]) or "none"
    display_verdict = (
        "uncalibrated"
        if packet["calibration_scope"].get("verdict") == "uncalibrated"
        else ("abstained" if abstention != "none" else "no-abstention")
    )
    blockers = ", ".join(str(item) for item in packet["sparring"]["evidence_required"][:2]) or "none reported"
    guardians = ", ".join(
        str(item.get("guardian_tier") or item.get("tier") or item.get("name"))
        for item in packet["guardian_map"]
        if isinstance(item, dict)
    ) or "offline"

    print("=" * 72)
    print("MVR COMMITTEE - status line")
    print(f"  seats: ADVOCATE[x] RESEARCH[model] {status} OPERATOR[{packet['seats_sat']['operator']}]")
    print(f"  verdict: {display_verdict} ({abstention})")
    print(
        f"  calibration: {packet['calibration_scope'].get('verdict')} "
        f"({packet['calibration_scope'].get('coverage_tier') or 'unknown'})"
    )
    print(f"  top blockers: {blockers}")
    print(f"  guardian veto surface: {guardians}")
    print("  wrote: charter.draft.md | mvr/committee_packet.json | mvr/decision-log.seed.json")
    print("  next: write PIVOT + THE BUILD + settlement, save as charter.md, then run preregister.py --in-place charter.md")
    print("=" * 72)


if __name__ == "__main__":
    main()
