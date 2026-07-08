"""Tests for scripts/passport_check.py."""
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "passport_check.py"))
SCHEMA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory", "passport.schema.json"))

VALID = {
    "passport_id": "op-1",
    "created_at": "2026-07-08T00:00:00Z",
    "verification": {"status": "self_reported"},
    "reach": {
        "named_counterparties": [
            {"role": "sacco_chair", "relationship": "community", "status": "self_reported"},
            {
                "role": "distributor_manager",
                "relationship": "client",
                "status": "attested",
                "attestation_ref": "fsr-1",
            },
        ]
    },
    "capacity": {"hours_per_week": 20},
    "consent": {
        "storage_consented": True,
        "disclosure_per_run": True,
        "consent_basis": "consent",
    },
}

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def run(passport_path):
    return subprocess.run(
        [sys.executable, SCRIPT, "--passport", passport_path, "--schema", SCHEMA],
        capture_output=True,
        text=True,
    )


def write(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        passport_path = os.path.join(tempdir, "passport.json")

        write(passport_path, VALID)
        result = run(passport_path)
        check("valid passport exits 0", result.returncode == 0)
        check("valid passport reports consent pass", "CONSENT GATE: pass" in result.stdout)

        bad_consent = json.loads(json.dumps(VALID))
        bad_consent["consent"]["disclosure_per_run"] = False
        write(passport_path, bad_consent)
        result = run(passport_path)
        check("consent failure exits 2", result.returncode == 2)
        check("consent failure message", "may NOT be disclosed" in result.stdout)

        missing_required = json.loads(json.dumps(VALID))
        del missing_required["passport_id"]
        write(passport_path, missing_required)
        result = run(passport_path)
        check("missing required exits 1", result.returncode == 1)

        invalid_status = json.loads(json.dumps(VALID))
        invalid_status["reach"]["named_counterparties"][0]["status"] = "magic"
        write(passport_path, invalid_status)
        result = run(passport_path)
        check("invalid counterparty status exits 1", result.returncode == 1)

        absent = os.path.join(tempdir, "missing.json")
        result = run(absent)
        check("absent passport exits 3", result.returncode == 3)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - passport check verified.")


if __name__ == "__main__":
    main()
