"""Tests for scripts/twin_fabrication_scan.py."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_fabrication_scan.py")
FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def setup(root, plan="", app="", ledger=None):
    write(os.path.join(root, "PRODUCT_PLAN.md"), plan)
    write(os.path.join(root, "scaffold", "src", "App.jsx"), app)
    if ledger is not None:
        path = os.path.join(root, "mvr", "public_research", "source_ledger.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)


def run(root):
    return subprocess.run(
        [sys.executable, SCRIPT, "--root", root, "--targets", "scaffold", "PRODUCT_PLAN.md"],
        capture_output=True,
        text=True,
    )


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        setup(
            tempdir,
            "Underwritten by Britam Microinsurance (IRA #MI-2094).",
            "const x = 'Cover by Britam (IRA #MI-2094). Clinic KMPDC Reg #LC-41094';",
        )
        result = run(tempdir)
        check("fabricated credential exits 1", result.returncode == 1)
        check("catches licence number", "MI-2094" in result.stdout)
        check("catches unsourced partner", "Britam" in result.stdout)

    with tempfile.TemporaryDirectory() as tempdir:
        setup(
            tempdir,
            "Underwritten by a licensed insurer (e.g. Britam, mock licence #MI-2094 for demo).",
            "const x = 'placeholder clinic (mock KMPDC Reg #LC-00000)';",
        )
        result = run(tempdir)
        check("hedged placeholders pass", result.returncode == 0, result.stdout[:100])

    with tempfile.TemporaryDirectory() as tempdir:
        setup(
            tempdir,
            "Enforces the IRA Microinsurance Regulations 2020 and Pharmacy and Poisons Act Cap 244.",
            "const note = 'Complies with Data Protection Act 2019 and DPA 2019 consent.';",
        )
        result = run(tempdir)
        check("statutes are not credentials", result.returncode == 0, result.stdout[:100])

    with tempfile.TemporaryDirectory() as tempdir:
        setup(tempdir, "Order id prefix MC-2026 and SKU AB-1234.", "const orderId = 'MC-2026';")
        result = run(tempdir)
        check("benign codes pass", result.returncode == 0, result.stdout[:100])

    verified_ledger = {
        "entries": [
            {
                "claim": "Britam Microinsurance is verified here with IRA #MI-2094 and KES 500,000 cover cap.",
                "source_name": "Britam Microinsurance",
                "url": "https://example.test/britam",
                "status": "verified",
                "notes": "Includes KES 500,000 cap.",
            }
        ]
    }
    with tempfile.TemporaryDirectory() as tempdir:
        setup(
            tempdir,
            "Underwritten by Britam Microinsurance (IRA #MI-2094). Sum insured KES 500,000 cap.",
            "const x = 'Britam Microinsurance IRA #MI-2094 KES 500,000 cover';",
            verified_ledger,
        )
        result = run(tempdir)
        check("verified partner credential and figure pass", result.returncode == 0, result.stdout[:120])

    with tempfile.TemporaryDirectory() as tempdir:
        setup(tempdir, "Minimum capital KES 500k cap.", "")
        result = run(tempdir)
        check("unverified hard figure flagged", result.returncode == 1 and "KES 500k" in result.stdout)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - fabrication scan catches unverified product-surface claims.")


if __name__ == "__main__":
    main()
