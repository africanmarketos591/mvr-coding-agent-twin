"""Generate done-for-you evidence collection assets from a Twin committee packet.

The committee names what lies ahead. This script turns the evidence bill and
UNKNOWN counterparties into action files:

  - mvr/fieldkit/requests/*.json
  - mvr/fieldkit/surveys/*.md
  - mvr/fieldkit/outreach/*.md
  - mvr/fieldkit/gate_costs.md
  - mvr/fieldkit/NEXT_ACTIONS.md

It does not submit anything. It drafts contract-shaped field-signal requests for
human review and submission.
"""
import argparse
import json
import os
import re

FIELD_SIGNAL_TYPES = {
    "retailer_permission_check",
    "guardian_vouching_check",
    "beneficiary_feedback_check",
    "donor_confidence_check",
    "implementing_partner_check",
    "service_provider_availability_check",
    "public_official_regulatory_check",
    "stockout_check",
    "trust_pulse",
    "price_change_reaction_check",
    "trust_trajectory_check",
    "channel_health_check",
    "school_fees_window_check",
    "harvest_liquidity_check",
    "market_event_verification",
}

STAKEHOLDER_SIGNAL_TYPE = {
    "beneficiary": "beneficiary_feedback_check",
    "consumer": "beneficiary_feedback_check",
    "customer": "beneficiary_feedback_check",
    "farmer": "beneficiary_feedback_check",
    "member": "beneficiary_feedback_check",
    "rider": "beneficiary_feedback_check",
    "guardian": "guardian_vouching_check",
    "community_leader": "guardian_vouching_check",
    "stage_chairman": "guardian_vouching_check",
    "public_official": "public_official_regulatory_check",
    "regulator": "public_official_regulatory_check",
    "retailer": "retailer_permission_check",
    "distributor": "retailer_permission_check",
    "partner": "implementing_partner_check",
    "internal_operations": "implementing_partner_check",
    "supplier": "service_provider_availability_check",
    "service_provider": "service_provider_availability_check",
    "donor": "donor_confidence_check",
}

DIMENSION_QUESTION = {
    "trust": "Would you trust this enough to use it with your own money, time, or reputation? Why?",
    "reciprocity": "What do you get back quickly enough to keep participating?",
    "embeddedness": "Is this carried by someone already rooted in your community or channel?",
    "belonging": "Does using it make you feel part of the group, or exposed on your own?",
    "cultural_fit": "Does this match how people here already coordinate, save, buy, or verify?",
    "continuity": "Would you still use this after the first week? What would make you stop?",
    "absence_sensitivity": "When the builder is absent, do people recommend it, ignore it, or warn others off?",
    "whispered_credibility": "Who told you about it, and would you vouch for it to someone you respect?",
    "narrative_looping": "Is this becoming part of the stories people tell each other about what works?",
    "fractal_trust": "Did someone trusted bring you in, and would you bring in the next person?",
    "guardian_strength": "Does the relevant guardian actively approve, merely tolerate, or oppose this?",
    "permission": "Who has granted permission for this to operate here, and what proof exists?",
    "channel_permission": "Which channel owner allows this in, and under what terms?",
    "infrastructural_intimacy": "Does this fit the phones, payments, network quality, and daily tools already used?",
}


def load_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


AUTHORITY_SOURCE_TYPES = {"regulator", "registry", "official"}
LEDGER_COST_CLASSES = {"licence_cost", "regulation"}


def slug(value):
    text = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return text or "item"


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def unknown_counterparties(charter_text):
    items = []
    for line in charter_text.splitlines():
        if "UNKNOWN" not in line or not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|") if cell.strip()]
        if cells and "claim" not in cells[0].lower():
            items.append(cells[0])
    return items


def ledger_cost_rows(root):
    ledger = load_json(os.path.join(root, "mvr", "public_research", "source_ledger.json"), {})
    rows = []
    if ledger.get("format") != "mvr_public_research_pack_v1":
        return rows
    for entry in ledger.get("entries", []) or []:
        if str(entry.get("status", "")).lower() != "verified":
            continue
        claim_class = str(entry.get("claim_class", "")).lower()
        source_type = str(entry.get("source_type", "")).lower()
        if claim_class not in LEDGER_COST_CLASSES or source_type not in AUTHORITY_SOURCE_TYPES:
            continue
        claim = str(entry.get("claim", "")).strip()
        notes = str(entry.get("notes", "")).strip()
        if not re.search(r"(fee|licen[cs]e|capital|ugx|ksh|usd|cost)", f"{claim} {notes}", re.I):
            continue
        source = str(entry.get("source_name", "")).strip() or "source ledger"
        url = str(entry.get("url", "")).strip()
        source_ref = f"{source} ({url})" if url else source
        rows.append([claim, "see source claim", "TODO-verify lead time", source_ref])
    return rows


def questions_for_lane(lane):
    fields = lane.get("required_fields") or lane.get("fields") or []
    if not isinstance(fields, list):
        fields = [fields]
    questions = []
    for field in fields:
        field = str(field)
        questions.append(DIMENSION_QUESTION.get(field, f"What would prove `{field}` locally for this stakeholder?"))
    if not questions:
        questions = [
            "What would make you trust or reject this offer?",
            "Who locally can approve, block, or validate it?",
            "What evidence would make this safe to rely on?",
        ]
    return questions


def signal_type_for(stakeholder):
    key = str(stakeholder or "").lower()
    return STAKEHOLDER_SIGNAL_TYPE.get(key, "beneficiary_feedback_check")


def generate_fieldkit(root, project_id, country, region="", committee=None, charter_text=""):
    packet = committee or load_json(os.path.join(root, "mvr", "committee_packet.json"), {})
    lanes = packet.get("evidence_bill") or []
    out = os.path.join(root, "mvr", "fieldkit")
    made = {"requests": 0, "surveys": 0, "outreach": 0}

    for lane in lanes:
        stakeholder = lane.get("stakeholder_class") or lane.get("lane") or lane.get("name")
        if not stakeholder:
            continue
        questions = questions_for_lane(lane)
        signal_type = signal_type_for(stakeholder)
        request = {
            "project_id": project_id,
            "signal_type": signal_type,
            "country": country,
            "target_stakeholder": stakeholder,
            "questions": questions,
        }
        if region:
            request["region"] = region
        request_path = os.path.join(out, "requests", f"{slug(stakeholder)}.request.json")
        survey_path = os.path.join(out, "surveys", f"{slug(stakeholder)}.md")
        write_json(request_path, request)
        write_text(
            survey_path,
            "# Field survey - {stakeholder}\n\n"
            "Signal type: `{signal_type}`\n"
            "Minimum signals: {minimum}\n\n"
            "Ask with consent, in local wording. Keep the dimension intent intact.\n\n"
            "{questions}\n".format(
                stakeholder=stakeholder,
                signal_type=signal_type,
                minimum=lane.get("minimum_signal_count", "unknown"),
                questions="\n".join(f"- {question}" for question in questions),
            ),
        )
        made["requests"] += 1
        made["surveys"] += 1

    for item in unknown_counterparties(charter_text):
        write_text(
            os.path.join(out, "outreach", f"{slug(item)[:48]}.md"),
            "# Outreach - {item}\n\n"
            "This counterparty is UNKNOWN in the charter and must become a dated, "
            "logged reference before dependent claims are made.\n\n"
            "Draft ask:\n\n"
            "> We are running a licence-safe pilot for `{project_id}` in {country}. "
            "Before we build on `{item}`, we need to confirm the terms, eligibility, "
            "and evidence you can provide. Could we schedule a short call and receive "
            "a dated note we can log as evidence?\n\n"
            "Until this is confirmed, keep the charter status as UNKNOWN - not verified.\n".format(
                item=item,
                project_id=project_id,
                country=country,
            ),
        )
        made["outreach"] += 1

    cost_rows = ledger_cost_rows(root)
    table_rows = []
    for cells in cost_rows[:20]:
        table_rows.append(f"| {cells[0][:140]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    if not table_rows:
        table_rows.append("| No verified fee/capital rows parsed | TODO-verify | TODO-verify | source ledger |")
    write_text(
        os.path.join(out, "gate_costs.md"),
        "# Gate cost and time\n\n"
        "Use current-format source-ledger figures only. Regulatory numbers go stale; "
        "verified cost rows require regulator, official, or registry sources. If a "
        "number cannot be verified, mark it TODO-verify.\n\n"
        "| Gate | Cost / capital | Lead time | Source |\n"
        "|---|---|---|---|\n"
        + "\n".join(table_rows)
        + "\n",
    )

    write_text(
        os.path.join(out, "NEXT_ACTIONS.md"),
        "# NEXT ACTIONS\n\n"
        f"Project: `{project_id}`\n"
        f"Market: {country}{' / ' + region if region else ''}\n\n"
        "1. Close UNKNOWN counterparties using `outreach/`.\n"
        "2. Run field surveys using `surveys/` and submit reviewed requests from `requests/`.\n"
        "3. Verify gate costs and time in `gate_costs.md`.\n"
        "4. Return to the Build Charter and update evidence only after corroboration.\n\n"
        f"Generated: {made['requests']} requests, {made['surveys']} surveys, {made['outreach']} outreach asks.\n",
    )
    return made


def main():
    parser = argparse.ArgumentParser(description="Generate field evidence actions from a committee packet.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--committee")
    parser.add_argument("--charter")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--region", default="")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    committee = load_json(args.committee or os.path.join(root, "mvr", "committee_packet.json"), {})
    charter_path = args.charter or os.path.join(root, "charter.md")
    charter_text = ""
    if os.path.exists(charter_path):
        with open(charter_path, encoding="utf-8-sig") as handle:
            charter_text = handle.read()
    made = generate_fieldkit(root, args.project_id, args.country, args.region, committee, charter_text)
    print(
        "twin_fieldkit wrote mvr/fieldkit "
        f"({made['requests']} requests, {made['surveys']} surveys, {made['outreach']} outreach asks)"
    )
    print("Nothing was submitted. Human review is required before field-signal requests are sent.")


if __name__ == "__main__":
    main()
