"""Tests for done-for-you field evidence kit generation."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_fieldkit.py")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import twin_fieldkit as F  # noqa: E402

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    check("all mapped signal types are verified enum", set(F.STAKEHOLDER_SIGNAL_TYPE.values()) <= F.FIELD_SIGNAL_TYPES)

    with tempfile.TemporaryDirectory() as tempdir:
        os.makedirs(os.path.join(tempdir, "mvr"), exist_ok=True)
        packet = {
            "evidence_bill": [
                {
                    "stakeholder_class": "consumer",
                    "minimum_signal_count": 100,
                    "required_fields": ["belonging", "trust", "absence_sensitivity", "reciprocity"],
                },
                {
                    "stakeholder_class": "guardian",
                    "minimum_signal_count": 2,
                    "required_fields": ["guardian_strength", "permission", "whispered_credibility"],
                },
            ]
        }
        with open(os.path.join(tempdir, "mvr", "committee_packet.json"), "w", encoding="utf-8") as handle:
            json.dump(packet, handle)
        with open(os.path.join(tempdir, "charter.md"), "w", encoding="utf-8") as handle:
            handle.write(
                "| Claim / fact used in charter | Source | URL | Date | Status |\n"
                "|---|---|---|---|---|\n"
                "| Named custody SACCO partner | - | - | - | UNKNOWN - not verified |\n"
                "| Bancassurance agent licence fee UGX 500,000 | IRA | https://example.test | 2026-07-08 | verified |\n"
            )

        result = subprocess.run(
            [
                sys.executable,
                SCRIPT,
                "--root",
                tempdir,
                "--project-id",
                "p1",
                "--country",
                "UG",
                "--region",
                "Kampala",
            ],
            capture_output=True,
            text=True,
        )
        check("fieldkit exits 0", result.returncode == 0, result.stderr[:120])

        request_path = os.path.join(tempdir, "mvr", "fieldkit", "requests", "consumer.request.json")
        request = json.load(open(request_path, encoding="utf-8"))
        check("request signal type valid", request["signal_type"] == "beneficiary_feedback_check")
        check("request contract fields present", all(key in request for key in ("project_id", "signal_type", "country", "target_stakeholder", "questions")))
        check("question count matches fields", len(request["questions"]) == 4)
        check("questions are plain language", all(len(question) > 20 for question in request["questions"]))

        guardian = json.load(open(os.path.join(tempdir, "mvr", "fieldkit", "requests", "guardian.request.json"), encoding="utf-8"))
        check("guardian maps to guardian_vouching_check", guardian["signal_type"] == "guardian_vouching_check")

        outreach_dir = os.path.join(tempdir, "mvr", "fieldkit", "outreach")
        check("outreach generated for UNKNOWN", any("custody" in name.lower() for name in os.listdir(outreach_dir)))
        check("gate costs written", os.path.exists(os.path.join(tempdir, "mvr", "fieldkit", "gate_costs.md")))
        check("next actions written", os.path.exists(os.path.join(tempdir, "mvr", "fieldkit", "NEXT_ACTIONS.md")))

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - fieldkit turns evidence gaps into actionable drafts.")


if __name__ == "__main__":
    main()
