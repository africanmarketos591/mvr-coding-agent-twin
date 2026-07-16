"""Regression for the FarmCircle false-green treatment run."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import twin_build_spec as bs  # noqa: E402
import twin_claim_coverage as coverage  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


BRIEF = """Build FarmCircle for a Ugandan agricultural cooperative.
- Register farmer profiles and keep a visible balance for every farmer.
- Keep weekly member contributions together in a shared cooperative fund.
- Let trusted farmers receive inputs before contributions are complete.
- Recover outstanding amounts from harvest sales and track repayments.
- Use a farmer reliability score based on contribution and repayment history.
- Add mobile-money collection and payout placeholders.
- Provide login roles for manager, field officer and farmer.
"""


def base_tree(root, status):
    brief_path = os.path.join(root, "mvr", "user-brief.txt")
    write(brief_path, BRIEF)
    claims, record = coverage.build_coverage(
        BRIEF,
        {"kind": "file", "path": "mvr/user-brief.txt"},
        [],
        "cooperative-ledger",
    )
    packet = {
        "provisional": False,
        "claims_sent": claims,
        "claim_coverage": record,
        "kernel_receipts": {"immutable_audit_hash": "a" * 64},
        "evidence_bill": [],
    }
    write_json(os.path.join(root, "mvr", "committee_packet.json"), packet)
    write_json(os.path.join(root, "mvr", "decision-log.json"), [{
        "entry_id": "DL-farmcircle-regression",
        "charter_ref": "charter.md",
        "verdict": "abstained",
        "decision_authorization": {
            "authorized_use": ["internal_planning"],
            "not_authorized_use": ["national_rollout", "capital_allocation"],
        },
        "kernel_receipts": {"immutable_audit_hash": "a" * 64},
    }])
    write(
        os.path.join(root, "charter.md"),
        "# BUILD CHARTER\n"
        f"**Status:** {status}\n"
        "## 5. THE BUILD\n"
        "- **Build:** a cooperative contribution ledger and input-request prototype.\n"
        "- **Explicitly NOT building:** live mobile money, open lending, or credit scoring.\n"
        "### 5A. Material capability disposition\n"
        "| Capability | Disposition | Exact boundary | Authorization ref |\n"
        "|---|---|---|---|\n"
        "| `fund_custody` | internal_simulation_only | synthetic balances; no live funds | |\n"
        "| `digital_lending` | internal_simulation_only | synthetic requests; no disbursement | |\n"
        "| `credit_scoring` | forbidden | no score may determine eligibility | |\n"
        "| `payment_processing` | internal_simulation_only | event labels only; no external rail | |\n"
        "| `repayment_recovery` | internal_simulation_only | synthetic ledger only | |\n"
        "| `role_based_access` | internal_simulation_only | role views only; not authentication | |\n"
        "| `personal_financial_records` | internal_simulation_only | synthetic people and values only | |\n"
        "The member-only structure keeps the build legal today.\n",
    )
    os.makedirs(os.path.join(root, "src"), exist_ok=True)
    write(
        os.path.join(root, "src", "app.js"),
        "function reliabilityScore(member) { return member.contributions - member.outstandingDebt; }\n"
        "function approveInputRequest(member) { return member.reliabilityScore > 70; }\n",
    )
    return packet


def review(root, request, contract, path, reviewer_id):
    write_json(os.path.join(root, path), {
        "format": bs.REVIEW_FORMAT,
        "request_sha256": request["request_sha256"],
        "reviewer_kind": "independent_model",
        "reviewer_id": reviewer_id,
        "model_id": "test-independent-model",
        "reviewed_at": "2026-07-14T00:00:00Z",
        "verdict": "pass",
        "findings": [],
        "adversarial_probes": [
            {
                "constraint_id": item["constraint_id"],
                "alias_or_data_flow": "reliability/trust alias feeding approval eligibility",
                "outcome": "not_found",
            }
            for item in contract["forbidden_constraints"]
        ],
        "opaque_file_acknowledgements": [],
        "attestation": bs.REVIEW_ATTESTATION,
    })


def main():
    with tempfile.TemporaryDirectory() as root:
        packet = base_tree(root, "pilot_only")
        found = {item["capability"] for item in packet["claim_coverage"]["material_capabilities"]}
        expected = {
            "fund_custody", "digital_lending", "credit_scoring", "payment_processing",
            "repayment_recovery", "role_based_access", "personal_financial_records",
        }
        check("full brief yields the FarmCircle material capability set", expected.issubset(found), sorted(found))
        check("all derived material claims reach sparring", len(packet["claims_sent"]) >= len(expected), len(packet["claims_sent"]))
        contract, _ = bs.write_contract(root)
        check(
            "every material capability has an explicit disposition",
            contract["material_capability_dispositions"]["status"] == "complete"
            and contract["material_capability_dispositions"]["recognized_count"] == 7,
            contract["material_capability_dispositions"],
        )
        check(
            "abstained decision cannot become pilot_only",
            contract["contract_level"] == "authorization_contradiction"
            and any("exceeds decision ceiling" in item for item in contract["blocking_reasons"]),
            contract["blocking_reasons"],
        )
        findings = bs.scan_code(root, ["src"], contract)
        check(
            "reliability-score alias feeding approval trips credit scoring",
            any(item["capability"] == "credit_scoring" for item in findings),
            findings,
        )

    legal_phrases = {
        "ensuring regulatory compliance as a bookkeeping tool": "regulatory_compliance_asserted",
        "designed to comply with the law": "compliance_design_asserted",
        "compliant as a bookkeeping tool": "compliance_design_asserted",
        "outside regulated activity": "licensing_exemption_asserted",
        "does not require licensing": "licensing_exemption_asserted",
        "avoids UMRA jurisdiction": "regulatory_avoidance_asserted",
    }
    for phrase, reason_code in legal_phrases.items():
        findings = bs.unearned_legal_claims(phrase)
        check(
            f"planning-only detector catches {phrase!r}",
            any(item["reason_code"] == reason_code for item in findings),
            findings,
        )
    check(
        "explicit uncertainty is not converted into a legal claim",
        not bs.unearned_legal_claims("UNKNOWN - not verified whether this requires licensing"),
    )
    check(
        "generic disclaimer cannot launder an affirmative legal claim",
        bool(bs.unearned_legal_claims("Not legal advice; this keeps the operator legal.")),
    )
    check(
        "explicit instruction not to claim compliance remains allowed",
        not bs.unearned_legal_claims("Do not claim this is designed to comply with the law."),
    )

    with tempfile.TemporaryDirectory() as root:
        base_tree(root, "internal_planning_only")
        charter_path = os.path.join(root, "charter.md")
        text = open(charter_path, encoding="utf-8").read()
        text = text.replace("| `credit_scoring` | forbidden | no score may determine eligibility | |\n", "")
        text = text.replace("live mobile money, open lending, or credit scoring", "live mobile money or open lending")
        text = text.replace("The member-only structure keeps the build legal today.\n", "")
        write(charter_path, text)
        contract, _ = bs.write_contract(root)
        check(
            "one missing material capability disposition blocks the contract",
            any("credit_scoring has no explicit charter disposition" in item for item in contract["blocking_reasons"]),
            contract["blocking_reasons"],
        )

    with tempfile.TemporaryDirectory() as root:
        base_tree(root, "internal_planning_only")
        charter_path = os.path.join(root, "charter.md")
        text = open(charter_path, encoding="utf-8").read().replace(
            "The member-only structure keeps the build legal today.\n",
            "| `credit_scoring` | internal_simulation_only | second conflicting row | |\n",
        )
        write(charter_path, text)
        contract, _ = bs.write_contract(root)
        check(
            "duplicate disposition rows cannot silently override each other",
            any("dispositions are duplicated: credit_scoring" in item for item in contract["blocking_reasons"]),
            contract["blocking_reasons"],
        )

    with tempfile.TemporaryDirectory() as root:
        base_tree(root, "internal_planning_only")
        charter_path = os.path.join(root, "charter.md")
        text = open(charter_path, encoding="utf-8").read()
        text = text.replace(
            "| `credit_scoring` | forbidden | no score may determine eligibility | |",
            "| `credit_scoring` | separately_authorized | score may determine eligibility | AUTH-self-written |",
        ).replace("The member-only structure keeps the build legal today.\n", "")
        write(charter_path, text)
        contract, _ = bs.write_contract(root)
        check(
            "charter cannot self-authorize a separately-authorized capability",
            any("authorization reference is not bound in the decision log" in item for item in contract["blocking_reasons"]),
            contract["blocking_reasons"],
        )

    with tempfile.TemporaryDirectory() as root:
        base_tree(root, "internal_planning_only")
        charter_path = os.path.join(root, "charter.md")
        text = open(charter_path, encoding="utf-8").read().replace(
            "The member-only structure keeps the build legal today.\n", ""
        )
        write(charter_path, text)
        contract, _ = bs.write_contract(root)
        check("planning-only charter is monotonic", not contract["blocking_reasons"], contract["blocking_reasons"])
        write(os.path.join(root, "src", "app.js"), "function contributionLedger() { return true; }\n")
        request, _ = bs.write_review_request(root, ["src"], contract)
        review(root, request, contract, bs.REVIEW_PATH, "reviewer-one")
        one = bs.validate_semantic_review(root, ["src"], contract, require_independent=True, require_second=True)
        check("one clean high-risk review cannot clear export", one["status"] == "missing", one["errors"])
        review(root, request, contract, bs.SECOND_REVIEW_PATH, "reviewer-one")
        duplicate = bs.validate_semantic_review(root, ["src"], contract, require_independent=True, require_second=True)
        check("same reviewer cannot impersonate second review", duplicate["status"] == "invalid", duplicate["errors"])
        review(root, request, contract, bs.SECOND_REVIEW_PATH, "reviewer-two")
        two = bs.validate_semantic_review(root, ["src"], contract, require_independent=True, require_second=True)
        check("two distinct adversarial reviews satisfy review structure", two["status"] == "current_pass", two["errors"])

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - FarmCircle false-green paths are closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
