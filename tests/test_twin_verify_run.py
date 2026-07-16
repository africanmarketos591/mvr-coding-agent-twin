"""Run-evidence audit: offline hashes never become VERIFIED."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import twin_build_spec as bs  # noqa: E402
import twin_verify_run as verifier  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def committee_tree(root, receipt="a" * 64, provisional=False):
    brief_path = os.path.join(root, "mvr", "user-brief.txt")
    os.makedirs(os.path.dirname(brief_path), exist_ok=True)
    with open(brief_path, "w", encoding="utf-8") as handle:
        handle.write("Build a contribution ledger without a savings score or loan book.")
    brief = open(brief_path, encoding="utf-8").read()
    claims, coverage = bs.claim_coverage.build_coverage(
        brief,
        {"kind": "file", "path": "mvr/user-brief.txt"},
        ["contribution ledger"],
        "contribution-ledger",
    )
    entry = {
        "entry_id": "DL-test",
        "charter_ref": "charter.md",
        "verdict": "redirected",
        "decision_authorization": {"authorized_use": ["internal_planning"]},
        "kernel_receipts": {"immutable_audit_hash": receipt} if receipt else {},
    }
    write_json(os.path.join(root, "mvr", "decision-log.seed.json"), [entry])
    write_json(os.path.join(root, "mvr", "committee_packet.json"), {
        "provisional": provisional,
        "seats_sat": {"spine": not provisional},
        "kernel_receipts": entry["kernel_receipts"],
        "claims_sent": claims,
        "claim_coverage": coverage,
    })


def main():
    old_key = os.environ.get("MVR_API_KEY")
    old_call = verifier.receipt_verifier.c.call
    try:
        os.environ.pop("MVR_API_KEY", None)

        with tempfile.TemporaryDirectory() as root:
            # Exact Cursor failure shape: asserted spine, placeholders, invented artifacts.
            write_json(os.path.join(root, "mvr", "decision-log.json"), [{
                "kernel_receipts": {
                    "decision_check_id": "committee-packet-local",
                    "semantic_decision_hash": "pending-preregister",
                    "routes_called": ["/v1/strategy-sparring"],
                },
            }])
            write_json(os.path.join(root, "mvr", "committee_packet.json"), {
                "provisional": False, "seats_sat": {"spine": True}, "kernel_receipts": {},
            })
            write_json(os.path.join(root, "mvr", "build_spec.json"), {"contract_version": "invented"})
            result = verifier.audit_run(root, stage="build")
            check("Cursor-shaped governance is rejected", result["status"] == "rejected", result["status"])
            details = " ".join(item["detail"] for item in result["checks"])
            check("false spine assertion is named", "seats_sat.spine=true" in details, details)

        with tempfile.TemporaryDirectory() as root:
            committee_tree(root)
            result = verifier.audit_run(root, stage="committee")
            check("arbitrary 64-hex without a key is inconclusive, never verified", result["status"] == "inconclusive", result["status"])

            os.environ["MVR_API_KEY"] = "test-key"
            verifier.receipt_verifier.c.call = lambda *args, **kwargs: (0.01, 404, {"status": "unverified"})
            result = verifier.audit_run(root, stage="committee")
            check("ledger-rejected hash rejects run evidence", result["status"] == "rejected", result["status"])

            verifier.receipt_verifier.c.call = lambda *args, **kwargs: (0.01, 200, {"status": "verified"})
            result = verifier.audit_run(root, stage="committee")
            check("live-verified authority plus coherent committee passes", result["status"] == "verified", result["status"])

        with tempfile.TemporaryDirectory() as root:
            committee_tree(root, receipt=None, provisional=True)
            os.environ.pop("MVR_API_KEY", None)
            result = verifier.audit_run(root, stage="committee")
            check("honest outage remains inconclusive rather than forged", result["status"] == "inconclusive", result["status"])

        with tempfile.TemporaryDirectory() as root:
            # Build-stage happy path, including current contract, charter hash, and semantic review.
            os.makedirs(os.path.join(root, "src"))
            with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as handle:
                handle.write(
                    "# Charter\n**Status:** redirect | **Preregistration hash:** <pending> (anchors: pending)\n"
                    "## 5. THE BUILD\n- **Build:** contribution ledger.\n"
                    "- **Explicitly NOT building:** a savings score or loan book.\n"
                )
            digest = verifier.prereg.digest_for(os.path.join(root, "charter.md"))
            verifier.prereg.write_in_place(os.path.join(root, "charter.md"), digest)
            committee_tree(root)
            with open(os.path.join(root, "src", "app.py"), "w", encoding="utf-8") as handle:
                handle.write("def contribution_ledger(): return True\n")
            contract, _ = bs.write_contract(root)
            request, _ = bs.write_review_request(root, ["src"], contract)
            write_json(os.path.join(root, bs.REVIEW_PATH), {
                "format": bs.REVIEW_FORMAT,
                "request_sha256": request["request_sha256"],
                "reviewer_kind": "host_model",
                "reviewer_id": "builder-session",
                "model_id": "test-model",
                "reviewed_at": "2026-07-10T00:00:00Z",
                "verdict": "pass",
                "findings": [],
                "adversarial_probes": [
                    {
                        "constraint_id": item["constraint_id"],
                        "alias_or_data_flow": "renamed eligibility and balance flow",
                        "outcome": "not_found",
                    }
                    for item in contract["forbidden_constraints"]
                ],
                "opaque_file_acknowledgements": [],
                "attestation": bs.REVIEW_ATTESTATION,
            })
            os.environ["MVR_API_KEY"] = "test-key"
            verifier.receipt_verifier.c.call = lambda *args, **kwargs: (0.01, 200, {"status": "verified"})
            result = verifier.audit_run(root, stage="build")
            check("coherent build evidence verifies", result["status"] == "verified", result["status"])
            result = verifier.audit_run(root, stage="export")
            check("host self-review cannot verify export", result["status"] == "rejected", result["status"])
            first = json.load(open(os.path.join(root, bs.REVIEW_PATH), encoding="utf-8"))
            first["reviewer_kind"] = "independent_model"
            first["reviewer_id"] = "independent-reviewer-one"
            write_json(os.path.join(root, bs.REVIEW_PATH), first)
            second = dict(first)
            second["reviewer_id"] = "independent-reviewer-two"
            write_json(os.path.join(root, bs.SECOND_REVIEW_PATH), second)
            with open(os.path.join(root, "MIRROR.md"), "w", encoding="utf-8") as handle:
                handle.write("# MIRROR\nTest assumptions.\n")
            with open(os.path.join(root, "MVR_DELTA_REPORT.md"), "w", encoding="utf-8") as handle:
                handle.write("# MVR DELTA REPORT\nTest-only counterfactual.\n")
            result = verifier.audit_run(root, stage="export")
            check(
                "planning-only authority cannot verify export even after review",
                result["status"] == "rejected"
                and result["dimensions"]["export_authorization"]["status"] == "fail",
                result,
            )
            check(
                "rejected planning export carries the mandatory response banner",
                result["final_response_banner"]
                == "INTERNAL-PLANNING PROTOTYPE ONLY. EXPORT REJECTED. NOT PILOT- OR DEPLOYMENT-AUTHORIZED.",
                result["final_response_banner"],
            )
            status_path = verifier.write_status(root, result)
            status_doc = json.load(open(status_path, encoding="utf-8"))
            check(
                "machine-readable final status preserves rejection and runtime boundary",
                status_doc["exit_code"] == 1
                and status_doc["dimensions"]["runtime_assurance"]["status"] == "not_evaluated",
                status_doc,
            )
            log_path = os.path.join(root, "mvr", "decision-log.seed.json")
            entries = json.load(open(log_path, encoding="utf-8"))
            entries[0]["decision_authorization"]["authorized_use"] = ["internal_planning", "bounded_pilot"]
            write_json(log_path, entries)
            contract, _ = bs.write_contract(root)
            request, _ = bs.write_review_request(root, ["src"], contract)
            for path, reviewer_id in (
                (bs.REVIEW_PATH, "independent-reviewer-one"),
                (bs.SECOND_REVIEW_PATH, "independent-reviewer-two"),
            ):
                review = dict(first)
                review["request_sha256"] = request["request_sha256"]
                review["reviewer_id"] = reviewer_id
                write_json(os.path.join(root, path), review)
            result = verifier.audit_run(root, stage="export")
            check("pilot-authorized export with two distinct reviews verifies", result["status"] == "verified", result["status"])
            check(
                "runtime remains a separate unevaluated dimension",
                result["dimensions"]["runtime_assurance"]["status"] == "not_evaluated",
                result["dimensions"],
            )

        with tempfile.TemporaryDirectory() as root:
            # Cursor beta.35 failure shape: a live receipt and self-review existed, but
            # the product-surface tripwire failed while the run verifier returned 0.
            os.makedirs(os.path.join(root, "src"))
            with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as handle:
                handle.write(
                    "# Charter\n**Status:** redirect | **Preregistration hash:** <pending> (anchors: pending)\n"
                    "## 5. THE BUILD\n- **Build:** contribution ledger.\n"
                    "- **Explicitly NOT building:** a savings score or loan book.\n"
                )
            digest = verifier.prereg.digest_for(os.path.join(root, "charter.md"))
            verifier.prereg.write_in_place(os.path.join(root, "charter.md"), digest)
            committee_tree(root)
            with open(os.path.join(root, "src", "app.py"), "w", encoding="utf-8") as handle:
                handle.write("def approve_loan(member): return member.savings_score\n")
            contract, _ = bs.write_contract(root)
            request, _ = bs.write_review_request(root, ["src"], contract)
            write_json(os.path.join(root, bs.REVIEW_PATH), {
                "format": bs.REVIEW_FORMAT,
                "request_sha256": request["request_sha256"],
                "reviewer_kind": "host_model",
                "reviewer_id": "cursor-session",
                "model_id": "cursor-test-model",
                "reviewed_at": "2026-07-10T00:00:00Z",
                "verdict": "pass",
                "findings": [],
                "adversarial_probes": [
                    {
                        "constraint_id": item["constraint_id"],
                        "alias_or_data_flow": "renamed eligibility and balance flow",
                        "outcome": "not_found",
                    }
                    for item in contract["forbidden_constraints"]
                ],
                "opaque_file_acknowledgements": [],
                "attestation": bs.REVIEW_ATTESTATION,
            })
            os.environ["MVR_API_KEY"] = "test-key"
            verifier.receipt_verifier.c.call = lambda *args, **kwargs: (0.01, 200, {"status": "verified"})
            result = verifier.audit_run(root, stage="build")
            details = " ".join(item["detail"] for item in result["checks"])
            check("failed product tripwire cannot coexist with VERIFIED", result["status"] == "rejected", result["status"])
            check("product tripwire failure is named", "approve_loan" in details or "digital_lending" in details, details)
    finally:
        verifier.receipt_verifier.c.call = old_call
        if old_key is None:
            os.environ.pop("MVR_API_KEY", None)
        else:
            os.environ["MVR_API_KEY"] = old_key

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - run evidence separates live authority, rejection, incompleteness, and uncertainty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
