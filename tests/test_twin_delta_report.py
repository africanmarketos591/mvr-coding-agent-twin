"""Offline tests for twin_delta_report."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import twin_delta_report as delta  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "mvr"))
        json.dump([
            {
                "decision_authorization": {
                    "authorized_use": ["internal_planning"],
                    "not_authorized_use": ["national_rollout", "capital_allocation"],
                },
                "verdict": "permission_not_yet_earned",
                "kernel_receipts": {"strategy_sparring_immutable_receipt_hash": "a" * 64},
            }
        ], open(os.path.join(root, "mvr", "decision-log.json"), "w", encoding="utf-8"))
        open(os.path.join(root, "charter.md"), "w", encoding="utf-8").write(
            "# BUILD CHARTER\n"
            "## 1. The idea as received\nBuild a direct lending app.\n"
            "## PIVOT\nKeep the repayment ledger; defer direct lending.\n"
            "## 5. THE BUILD\nA non-custodial repayment ledger for one partner.\n"
            "## 8. Settlement\nt+90d: one partner records repayments weekly.\n"
        )
        report = delta.build_report(root)
        check("claim level comes from decision log", "internal_planning" in report and "national_rollout" in report)
        check("counterfactual is labelled hypothesis", "Hypothesis, not a market claim" in report)
        check("charter pivot is surfaced", "repayment ledger" in report.lower())
        check("settlement metric is surfaced", "records repayments weekly" in report.lower())
        check("descriptive receipt key is surfaced", "strategy_sparring_immutable_receipt_hash" in report)
        check("does not fabricate validation language", "proven demand" not in report.lower())

    with tempfile.TemporaryDirectory() as bare:
        report = delta.build_report(bare, "Build a marketplace.")
        check("ungrounded report is honest", "No kernel receipt on file" in report)
        check("passed idea is used", "Build a marketplace." in report)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - delta report grounds facts and labels the counterfactual.")


if __name__ == "__main__":
    main()
