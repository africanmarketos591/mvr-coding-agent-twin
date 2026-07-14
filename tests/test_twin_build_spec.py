"""Build-constraint tripwire, history, and semantic-review regression tests."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import twin_build_spec as bs  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def write_decision(root, override=None, charter_ref="charter.md"):
    entry = {
        "charter_ref": charter_ref,
        "decision_authorization": {
            "authorized_use": ["internal_planning"],
            "not_authorized_use": ["national_rollout", "capital_allocation"],
        },
        "kernel_receipts": {"immutable_audit_hash": "a" * 64},
    }
    if override:
        entry["build_contract_override"] = override
    path = os.path.join(root, "mvr", "decision-log.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump([entry], handle)
    brief_path = os.path.join(root, "mvr", "user-brief.txt")
    if not os.path.exists(brief_path):
        write(brief_path, "Build an employer wage ledger. Do not build lending, credit scoring, or a wallet.")
    brief = open(brief_path, encoding="utf-8").read()
    claims, coverage = bs.claim_coverage.build_coverage(
        brief,
        {"kind": "file", "path": "mvr/user-brief.txt"},
        ["employer wage ledger"],
        "wage-ledger",
    )
    packet_path = os.path.join(root, "mvr", "committee_packet.json")
    if not os.path.exists(packet_path):
        with open(packet_path, "w", encoding="utf-8") as handle:
            json.dump({
                "provisional": False,
                "claims_sent": claims,
                "claim_coverage": coverage,
                "kernel_receipts": {"immutable_audit_hash": "a" * 64},
            }, handle)


def charter(cut="a consumer loan book or credit scoring; no wallet holding funds", status="redirect"):
    return (
        "# BUILD CHARTER\n"
        f"**Status:** {status}\n"
        "## 5. THE BUILD\n"
        "- **Build:** an employer-funded, non-custodial wage ledger.\n"
        "- **For:** one factory.\n"
        "- **Distributed through:** employer HR.\n"
        + (f"- **Explicitly NOT building:** {cut}.\n" if cut else "")
        + "- **What a demo will NOT prove:** regulatory approval.\n"
    )


def write_semantic_review(root, targets, contract, verdict="pass", findings=None):
    request, _ = bs.write_review_request(root, targets, contract)
    review = {
        "format": bs.REVIEW_FORMAT,
        "request_sha256": request["request_sha256"],
        "reviewer_kind": "host_model",
        "reviewer_id": "test-reviewer-session",
        "model_id": "test-frontier-model",
        "reviewed_at": "2026-07-10T00:00:00Z",
        "verdict": verdict,
        "findings": findings or [],
        "adversarial_probes": [
            {
                "constraint_id": item["constraint_id"],
                "alias_or_data_flow": "renamed function and downstream balance/eligibility use",
                "outcome": "not_found" if verdict == "pass" else "finding:src/loans.py:1",
            }
            for item in contract["forbidden_constraints"]
        ],
        "opaque_file_acknowledgements": [item["path"] for item in request["opaque_files"]],
        "attestation": bs.REVIEW_ATTESTATION,
    }
    with open(os.path.join(root, bs.REVIEW_PATH), "w", encoding="utf-8") as handle:
        json.dump(review, handle)
    return review


def main():
    with tempfile.TemporaryDirectory() as root:
        write(os.path.join(root, "charter.md"), charter())
        write_decision(root)
        brief = open(os.path.join(root, "mvr", "user-brief.txt"), encoding="utf-8").read()
        claims, coverage = bs.claim_coverage.build_coverage(
            brief,
            {"kind": "file", "path": "mvr/user-brief.txt"},
            ["consumer credit scoring and a digital loan advance"],
            "wage-ledger",
        )
        packet = {
            "provisional": False,
            "claims_sent": claims,
            "claim_coverage": coverage,
            "evidence_bill": [{"stakeholder_class": "worker", "minimum_signal_count": 25, "required_fields": ["trust"]}],
        }
        with open(os.path.join(root, "mvr", "committee_packet.json"), "w", encoding="utf-8") as handle:
            json.dump(packet, handle)

        contract, output = bs.write_contract(root)
        forbidden = {item["capability"] for item in contract["forbidden_capabilities"]}
        check("contract file emitted", os.path.exists(output))
        check("claim authorization comes from decision log", contract["authority"]["authorized_claim_classes"] == ["internal_planning"])
        check("kernel authority boundary is explicit", "not semantic code behavior" in contract["authority"]["boundary"])
        check("build feature excludes cut list", contract["build_features"] == ["an employer-funded, non-custodial wage ledger."])
        check("raw cut-list constraint retained", len(contract["forbidden_constraints"]) == 1)
        check("naive tripwires derived", {"digital_lending", "credit_scoring", "fund_custody"}.issubset(forbidden))
        check("source fingerprints validate", not bs.validate_contract(root, contract))

        src = os.path.join(root, "src")
        os.makedirs(src)
        write(os.path.join(src, "loans.py"), "def approve_loan(user):\n    return underwrite_credit(user)\n")
        findings = bs.scan_code(root, ["src"], contract)
        check("tripwire catches obvious lending spelling", any(item["capability"] == "digital_lending" for item in findings))

        write(os.path.join(src, "loans.py"), "# This app must not approve loans.\ndef record_wages(amount):\n    return amount\n")
        check("negated safety comment does not false-block", not bs.scan_code(root, ["src"], contract))

        # A semantic rename can clear the lexical tripwire, so it must never clear the end-to-end review gate.
        write(
            os.path.join(src, "loans.py"),
            "def release(worker, amount):\n    pool.debit(amount)\n    worker.credit(amount)\n    payroll.deduct_next_cycle(worker, amount)\n",
        )
        check("semantic rename may clear lexical tripwire", not bs.scan_code(root, ["src"], contract))
        missing = bs.validate_semantic_review(root, ["src"], contract)
        check("semantic rename cannot earn assurance without model review", missing["status"] == "missing")
        write_semantic_review(root, ["src"], contract, "block", [{
            "path": "src/loans.py", "line": 1,
            "constraint_id": contract["forbidden_constraints"][0]["constraint_id"],
            "reason": "pool-funded advance repaid through payroll is lending behavior",
        }])
        check("model semantic block is binding", bs.validate_semantic_review(root, ["src"], contract)["status"] == "current_block")

        write(os.path.join(src, "loans.py"), "def record_wages(amount):\n    return amount\n")
        review = write_semantic_review(root, ["src"], contract, "pass")
        check("fresh model semantic pass validates", bs.validate_semantic_review(root, ["src"], contract)["status"] == "current_pass")
        review["model_id"] = "auto"
        with open(os.path.join(root, bs.REVIEW_PATH), "w", encoding="utf-8") as handle:
            json.dump(review, handle)
        placeholder = bs.validate_semantic_review(root, ["src"], contract)
        check(
            "placeholder model identity cannot attest semantic review",
            placeholder["status"] == "invalid" and any("actual model" in item for item in placeholder["errors"]),
            placeholder["errors"],
        )
        write_semantic_review(root, ["src"], contract, "pass")
        write(os.path.join(src, "loans.py"), "def record_wages(amount, ref):\n    return amount\n")
        check("code change makes semantic review stale", bs.validate_semantic_review(root, ["src"], contract)["status"] == "invalid")

        write(os.path.join(src, "wallet.sol"), "contract L { function approve_loan() public {} }\n")
        write(os.path.join(src, "wallet.sql"), "CREATE PROC approve_loan AS INSERT INTO loan_book VALUES(1);\n")
        carriers = bs.scan_code(root, ["src"], contract)
        check("Solidity and SQL are scanned", {"src/wallet.sol", "src/wallet.sql"}.issubset({item["path"] for item in carriers}))
        write(os.path.join(src, "scores.py"), "def savings_score(member): return member.payment_ratio\n")
        score_findings = bs.scan_code(root, ["src/scores.py"], contract)
        check("savings-score engine trips credit-scoring cut", any(item["capability"] == "credit_scoring" for item in score_findings))

        write(
            os.path.join(root, "charter.md"),
            charter(cut="no consumer loan book, no credit scoring, and no custody of member funds", status="redirect"),
        )
        reworded, _ = bs.write_contract(root)
        check("rewording that preserves all capability cuts is not laundering", not reworded["blocking_reasons"])

        write(os.path.join(root, "charter.md"), charter(cut="", status="redirect"))
        weakened, _ = bs.write_contract(root)
        check("constraint removal without signature blocks", weakened["contract_level"] == "constraint_weakening_blocked")
        check("old lending constraint carried forward", "digital_lending" in {item["capability"] for item in weakened["forbidden_capabilities"]})

        dropped_ids = weakened["constraint_history"]["dropped_constraint_ids"]
        dropped_caps = weakened["constraint_history"]["dropped_capabilities"]
        override = {
            "basis": "named_human_override",
            "reviewer": "test-reviewer",
            "signature_ref": "sig-test",
            "note": "Test-only removal after documented scope change.",
            "allow_removed_capabilities": dropped_caps,
            "allow_removed_constraint_ids": dropped_ids,
        }
        write(
            os.path.join(root, "charter.md"),
            charter(cut="", status="redirect")
            + "\nCode capability disposition: capability-free - no regulated capability remains in the fitted build.\n",
        )
        write_decision(root, override=override)
        released, _ = bs.write_contract(root)
        check("complete named-human override can release old constraint", not released["blocking_reasons"], released["blocking_reasons"])

    with tempfile.TemporaryDirectory() as root:
        write(os.path.join(root, "charter.md"), "# Charter\n**Status:** redirect\n## 5. THE BUILD\nA ledger.\n")
        write_decision(root)
        suspect, _ = bs.write_contract(root)
        check("empty redirect extraction fails loud", suspect["contract_level"] == "extraction_suspect" and suspect["blocking_reasons"])

    with tempfile.TemporaryDirectory() as root:
        prose = (
            "# Charter\n**Status:** redirect\n## 5. THE BUILD (fitted)\n"
            "Employer-funded ledger. NOT building: a direct-to-consumer loan book, interest-bearing credit, or credit scoring.\n"
        )
        write(os.path.join(root, "charter.md"), prose)
        write_decision(root)
        parsed, _ = bs.write_contract(root)
        check("inline prose cut-list extracts", len(parsed["forbidden_constraints"]) == 1 and len(parsed["forbidden_capabilities"]) >= 2)

    with tempfile.TemporaryDirectory() as root:
        nested = os.path.join(root, "case", "charter.md")
        write(nested, charter())
        write_decision(root, charter_ref="case/charter.md")
        discovered, _ = bs.write_contract(root)
        check("decision-log charter_ref works outside root", discovered["source_fingerprints"]["charter"]["path"] == "case/charter.md")

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - tripwire, semantic review, extraction, and constraint history boundaries verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
