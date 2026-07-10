"""Regression for beta.33's extension-allowlist and self-review gaps."""
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


def write(path, value, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if binary else "w"
    kwargs = {} if binary else {"encoding": "utf-8", "newline": "\n"}
    with open(path, mode, **kwargs) as handle:
        handle.write(value)


def review(root, request, kind="host_model"):
    payload = {
        "format": bs.REVIEW_FORMAT,
        "request_sha256": request["request_sha256"],
        "reviewer_kind": kind,
        "reviewer_id": f"{kind}-carrier-review",
        "model_id": "independent-test-model" if kind != "human" else "",
        "reviewed_at": "2026-07-10T00:00:00Z",
        "verdict": "pass",
        "findings": [],
        "opaque_file_acknowledgements": [item["path"] for item in request["opaque_files"]],
        "attestation": bs.REVIEW_ATTESTATION,
    }
    with open(os.path.join(root, bs.REVIEW_PATH), "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def main():
    charter = (
        "# BUILD CHARTER\n**Status:** redirect | **Preregistration hash:** pending\n"
        "## 5. THE BUILD\n- Build: a non-custodial repayment ledger.\n"
        "## Explicitly NOT building (and why)\n"
        "- Digital lending / loan book - requires a licence.\n"
        "- Fund custody: holding customer funds / wallet balance - regulated.\n"
    )
    carriers = {
        "app/loans.dart": "void approveLoan(u){ /* issue loan, loan book */ }\n",
        "api/loans.mjs": "export function approve_loan(u){ return {loan_book:1}; }\n",
        "db/schema.prisma": "model Loan { id Int @id\n  loan_book Boolean }\n",
        "schema/service.graphql": "type Loan { loan_book: Boolean! }\n",
        "mobile/build.gradle": "ext.loan_book = true\n",
        "service/worker.ex": "def approve_loan(user), do: issue_loan(user)\n",
        "bin/launcher": "approve_loan=true\n",
    }
    with tempfile.TemporaryDirectory() as root:
        write(os.path.join(root, "charter.md"), charter)
        write(
            os.path.join(root, "mvr", "decision-log.json"),
            json.dumps([{
                "charter_ref": "charter.md",
                "decision_authorization": {"authorized_use": ["internal_planning"]},
                "kernel_receipts": {"immutable_audit_hash": "a" * 64},
            }]),
        )
        for relative, body in carriers.items():
            write(os.path.join(root, relative), body)
        write(os.path.join(root, "app", "logo.png"), b"\x89PNG\r\n\x1a\n\x00binary", binary=True)
        write(os.path.join(root, "node_modules", "hidden.dart"), "approveLoan();\n")

        contract, _ = bs.write_contract(root)
        targets = ["app", "api", "db", "schema", "mobile", "service", "bin"]
        findings = bs.scan_code(root, targets, contract)
        found_paths = {item["path"] for item in findings}
        check("tripwire sees previously omitted text carriers", set(carriers).issubset(found_paths), sorted(found_paths))

        request, _ = bs.write_review_request(root, targets, contract)
        shown = {item["path"] for item in request["files"]}
        opaque = {item["path"] for item in request["opaque_files"]}
        check("semantic manifest covers all first-party text carriers", set(carriers).issubset(shown), sorted(shown))
        check("known binary is disclosed and hash-bound", "app/logo.png" in opaque, sorted(opaque))
        check("review policy is content-classified", request["scope_policy"]["text_coverage"].endswith("by_content"))

        review(root, request, "host_model")
        check("host self-review supports local accountability", bs.validate_semantic_review(root, targets, contract)["status"] == "current_pass")
        independent = bs.validate_semantic_review(root, targets, contract, require_independent=True)
        check("host self-review cannot satisfy independent assurance", independent["status"] == "invalid")

        review(root, request, "independent_model")
        check(
            "separate reviewer satisfies independent mode",
            bs.validate_semantic_review(root, targets, contract, require_independent=True)["status"] == "current_pass",
        )

        write(os.path.join(root, "app", "loans.dart"), "void releaseAdvance(u){}\n")
        stale = bs.validate_semantic_review(root, targets, contract)
        check("changing an omitted-in-beta33 carrier invalidates review", stale["status"] == "invalid")

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - text-carrier coverage, opaque accounting, and reviewer independence verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
