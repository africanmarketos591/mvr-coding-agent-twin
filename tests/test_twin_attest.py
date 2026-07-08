"""Tests for scripts/twin_attest.py."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_attest.py")
FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def run(tempdir, *args):
    return subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--passport",
            os.path.join(tempdir, "mvr", "passport.json"),
            *args,
        ],
        cwd=tempdir,
        capture_output=True,
        text=True,
    )


def load_passport(tempdir):
    with open(os.path.join(tempdir, "mvr", "passport.json"), encoding="utf-8") as handle:
        return json.load(handle)


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        os.makedirs(os.path.join(tempdir, "mvr"), exist_ok=True)

        result = run(tempdir, "--init", "--name", "Mark", "--country", "UG")
        passport = load_passport(tempdir)
        check("init creates self_reported passport", result.returncode == 0 and passport["verification"]["status"] == "self_reported")

        result = run(
            tempdir,
            "--request",
            "--counterparty",
            "Wandegeya SACCO",
            "--role",
            "custody_partner",
            "--relationship",
            "partner",
        )
        passport = load_passport(tempdir)
        check("request marks confirmation_requested", result.returncode == 0 and passport["reach"]["named_counterparties"][0]["status"] == "confirmation_requested")

        result = run(
            tempdir,
            "--attest",
            "--counterparty",
            "Wandegeya SACCO",
            "--role",
            "custody_partner",
            "--relationship",
            "partner",
        )
        passport = load_passport(tempdir)
        check("attest without ref refused", result.returncode == 2 and "REFUSED" in result.stdout)
        check("refusal preserves 0.30 status", passport["reach"]["named_counterparties"][0]["status"] == "confirmation_requested")

        result = run(
            tempdir,
            "--attest",
            "--counterparty",
            "Wandegeya SACCO",
            "--role",
            "custody_partner",
            "--relationship",
            "partner",
            "--attestation-ref",
            "field-signal:fsr-123",
        )
        passport = load_passport(tempdir)
        check("attest with ref succeeds", result.returncode == 0 and passport["reach"]["named_counterparties"][0]["status"] == "attested")
        check("verification upgrades to attested", passport["verification"]["status"] == "attested")
        check("attestation ref collected", "field-signal:fsr-123" in passport["verification"]["attestation_refs"])

        run(
            tempdir,
            "--request",
            "--counterparty",
            "IRA insurer",
            "--role",
            "underwriter",
            "--relationship",
            "partner",
        )
        passport = load_passport(tempdir)
        check("mixed reach becomes partially_attested", passport["verification"]["status"] == "partially_attested")

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - attestation loop closes without self-upgrading reach.")


if __name__ == "__main__":
    main()
