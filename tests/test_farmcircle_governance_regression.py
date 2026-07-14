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
