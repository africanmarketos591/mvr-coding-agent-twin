"""Authority-to-code contract regression tests."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import twin_build_spec as build_spec  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def main():
    with tempfile.TemporaryDirectory() as root:
        mvr = os.path.join(root, "mvr")
        os.makedirs(mvr)
        write(
            os.path.join(root, "charter.md"),
            "# BUILD CHARTER\n"
            "**Status:** redirect\n"
            "## 5. THE BUILD\n"
            "- **Build:** an employer-funded, non-custodial wage ledger.\n"
            "- **For:** one factory.\n"
            "- **Distributed through:** employer HR.\n"
            "- **Explicitly NOT building:** a consumer loan book or credit scoring; no wallet holding funds.\n"
            "- **What a demo will NOT prove:** regulatory approval.\n"
            "## 6. Redirect\n"
            "The app-funded loan died.\n",
        )
        with open(os.path.join(mvr, "decision-log.json"), "w", encoding="utf-8") as handle:
            json.dump([{
                "decision_authorization": {
                    "authorized_use": ["internal_planning"],
                    "not_authorized_use": ["national_rollout", "capital_allocation"],
                },
                "kernel_receipts": {"immutable_audit_hash": "a" * 64},
            }], handle)
        with open(os.path.join(mvr, "committee_packet.json"), "w", encoding="utf-8") as handle:
            json.dump({
                "provisional": False,
                "claims_sent": ["consumer credit scoring and a digital loan advance"],
                "evidence_bill": [{
                    "stakeholder_class": "worker",
                    "minimum_signal_count": 25,
                    "required_fields": ["trust"],
                }],
            }, handle)

        contract, output = build_spec.write_contract(root)
        forbidden = {item["capability"] for item in contract["forbidden_capabilities"]}
        check("contract file emitted", os.path.exists(output))
        check("claim authorization comes from decision log", contract["authority"]["authorized_claim_classes"] == ["internal_planning"])
        check("denied claim classes retained", "national_rollout" in contract["authority"]["not_authorized_claim_classes"])
        check("build feature excludes cut list", contract["build_features"] == ["an employer-funded, non-custodial wage ledger."])
        check("forbids lending", "digital_lending" in forbidden)
        check("forbids credit scoring", "credit_scoring" in forbidden)
        check("forbids custody", "fund_custody" in forbidden)
        check("captures proposed regulated capability", "credit_scoring" in contract["proposed_regulated_capabilities"])
        check("preserves instrumentation bill", contract["required_instrumentation"][0]["capture_for"] == "worker")
        check("receipt presence is not called verification", contract["authority"]["receipt_verification"] == "not_performed_offline")
        check("source fingerprints validate", not build_spec.validate_contract(root, contract))

        src = os.path.join(root, "src")
        os.makedirs(src)
        write(os.path.join(src, "loans.py"), "def approve_loan(user):\n    return underwrite_credit(user)\n")
        findings = build_spec.scan_code(root, ["src"], contract)
        check("code-time check catches redirected lending", any(item["capability"] == "digital_lending" for item in findings))

        write(os.path.join(src, "loans.py"), "# This app must not approve loans.\ndef record_wages(amount):\n    return amount\n")
        check("negated safety comment does not false-block", not build_spec.scan_code(root, ["src"], contract))

        write(os.path.join(src, "loans.py"), "allowed = not blocked; result = issue_loan(user)\n")
        inline = build_spec.scan_code(root, ["src"], contract)
        check("inline negation cannot hide executable lending", any(item["capability"] == "digital_lending" for item in inline))

        write(os.path.join(root, "charter.md"), read_back(os.path.join(root, "charter.md")) + "\nChanged after contract.\n")
        stale = build_spec.validate_contract(root, contract)
        check("changed charter invalidates old contract", any("charter changed" in item for item in stale))

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - authority-to-code contract is grounded, freshness-bound, and enforced.")
    return 0


def read_back(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


if __name__ == "__main__":
    sys.exit(main())
