"""Regression for the four beta.32 peer-critic evasions.

The deterministic layer is intentionally tested as a tripwire, not semantic proof.
An end-to-end clear requires both a current contract and a current model review.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import twin_build_spec as bs  # noqa: E402


FAILS = []
CONFORMANT_CUT = (
    "## 5. THE BUILD\n- Build: a non-custodial repayment ledger.\n"
    "## Explicitly NOT building (and why)\n"
    "- Digital lending / loan book - requires a CBN licence.\n"
    "- Fund custody: holding customer funds / wallet balance - e-money regulated.\n"
)
PROSE_CUT = (
    "## 5. THE BUILD (fitted)\nEmployer-funded ledger. NOT building: a direct-to-consumer "
    "loan book, interest-bearing credit, or credit scoring, until a licensed partner carries it.\n"
)


def check(name, condition):
    print(f"{'PASS' if condition else 'FAIL'}  {name}")
    if not condition:
        FAILS.append(name)


def setup(root, body):
    os.makedirs(os.path.join(root, "mvr"), exist_ok=True)
    os.makedirs(os.path.join(root, "src"), exist_ok=True)
    with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as handle:
        handle.write("# BUILD CHARTER\n**Status:** redirect\n" + body)
    with open(os.path.join(root, "mvr", "decision-log.json"), "w", encoding="utf-8") as handle:
        json.dump([{
            "charter_ref": "charter.md",
            "verdict": "redirected",
            "decision_authorization": {"authorized_use": ["internal_planning"]},
            "kernel_receipts": {"immutable_audit_hash": "a" * 64},
        }], handle)
    brief = "Build a repayment ledger without digital lending, credit scoring, or custody of customer funds."
    with open(os.path.join(root, "mvr", "user-brief.txt"), "w", encoding="utf-8") as handle:
        handle.write(brief)
    claims, coverage = bs.claim_coverage.build_coverage(
        brief, {"kind": "file", "path": "mvr/user-brief.txt"}, [], "repayment-ledger"
    )
    with open(os.path.join(root, "mvr", "committee_packet.json"), "w", encoding="utf-8") as handle:
        json.dump({
            "provisional": False,
            "claims_sent": claims,
            "claim_coverage": coverage,
            "kernel_receipts": {"immutable_audit_hash": "a" * 64},
        }, handle)
    return bs.write_contract(root)[0]


def write_model_pass(root, target, contract):
    request, _ = bs.write_review_request(root, [target], contract)
    review = {
        "format": bs.REVIEW_FORMAT,
        "request_sha256": request["request_sha256"],
        "reviewer_kind": "host_model",
        "reviewer_id": "redteam-control-session",
        "model_id": "redteam-control-model",
        "reviewed_at": "2026-07-10T00:00:00Z",
        "verdict": "pass",
        "findings": [],
        "adversarial_probes": [
            {
                "constraint_id": item["constraint_id"],
                "alias_or_data_flow": "renamed advance and balance flow",
                "outcome": "not_found",
            }
            for item in contract["forbidden_constraints"]
        ],
        "opaque_file_acknowledgements": [item["path"] for item in request["opaque_files"]],
        "attestation": bs.REVIEW_ATTESTATION,
    }
    with open(os.path.join(root, bs.REVIEW_PATH), "w", encoding="utf-8") as handle:
        json.dump(review, handle)


def main():
    # 1. Prose cut-list no longer emits an empty contract.
    with tempfile.TemporaryDirectory() as root:
        contract = setup(root, PROSE_CUT)
        with open(os.path.join(root, "src", "a.py"), "w") as handle:
            handle.write("def approve_loan(u): return {'loan book': 1, 'wallet balance': u}\n")
        check("GAP1 prose cut-list extracted", bool(contract["forbidden_constraints"]))
        check("GAP1 blatant implementation trips", bool(bs.scan_code(root, ["src"], contract)))

    # 2. A lexical rename cannot earn an end-to-end pass without semantic review.
    with tempfile.TemporaryDirectory() as root:
        contract = setup(root, CONFORMANT_CUT)
        with open(os.path.join(root, "src", "b.py"), "w") as handle:
            handle.write(
                "def release(w, a):\n    pool.debit(a)\n    w.credit(a)\n    payroll.deduct_next_cycle(w, a)\n"
            )
        lexical_clear = not bs.scan_code(root, ["src"], contract)
        semantic = bs.validate_semantic_review(root, ["src"], contract)
        check("GAP2 lexical limits remain honestly visible", lexical_clear)
        check("GAP2 no semantic review means no assurance", semantic["status"] == "missing")

    # 3. SQL and Solidity are realistic governed carriers.
    with tempfile.TemporaryDirectory() as root:
        contract = setup(root, CONFORMANT_CUT)
        with open(os.path.join(root, "src", "x.sol"), "w") as handle:
            handle.write("contract L { function approve_loan() public {} }\n")
        with open(os.path.join(root, "src", "y.sql"), "w") as handle:
            handle.write("CREATE PROC approve_loan AS INSERT INTO loan_book VALUES(1);\n")
        paths = {item["path"] for item in bs.scan_code(root, ["src"], contract)}
        check("GAP3 Solidity governed", "src/x.sol" in paths)
        check("GAP3 SQL governed", "src/y.sql" in paths)

    # 4. Re-emitting a weaker charter carries old constraints and blocks.
    with tempfile.TemporaryDirectory() as root:
        setup(root, CONFORMANT_CUT)
        with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as handle:
            handle.write("# BUILD CHARTER\n**Status:** build_authorized\n## 5. THE BUILD\n- Build: everything.\n")
        weakened, _ = bs.write_contract(root)
        with open(os.path.join(root, "src", "c.py"), "w") as handle:
            handle.write("def approve_loan(u): return {'loan book': 1}\n")
        check("GAP4 weakening fails contract validation", bool(bs.validate_contract(root, weakened)))
        check("GAP4 old cut-list remains active", bool(bs.scan_code(root, ["src"], weakened)))

    # Fair control: fitted code plus current model review clears both layers.
    with tempfile.TemporaryDirectory() as root:
        contract = setup(root, CONFORMANT_CUT)
        with open(os.path.join(root, "src", "ledger.py"), "w") as handle:
            handle.write("def record_repayment(amount, ref): return amount\n")
        write_model_pass(root, "src", contract)
        check("clean fitted code clears tripwire", not bs.scan_code(root, ["src"], contract))
        check("clean fitted code has current semantic review", bs.validate_semantic_review(root, ["src"], contract)["status"] == "current_pass")

    benchmark_root = os.path.join(ROOT, "benchmarks", "mvr-viability-v1", "runs31_scored")
    redirect_charters = 0
    missing_constraints = []
    for case_id in sorted(os.listdir(benchmark_root)):
        path = os.path.join(benchmark_root, case_id, "treatment", "charter.md")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if "Status:** redirect" not in text:
            continue
        redirect_charters += 1
        _features, cuts = bs.charter_constraints(text)
        if not cuts and not bs.capability_free_reason(text):
            missing_constraints.append(case_id)
    check("published redirect charters all extract at least one constraint", redirect_charters > 0 and not missing_constraints)

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - all four beta.32 evasions are closed or routed to explicit model review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
