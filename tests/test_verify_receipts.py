"""Offline tests for scripts/verify_receipts.py."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import verify_receipts as vr  # noqa: E402


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


LEDGER = {"a" * 64, "b" * 64}


def fake_call(path, **kwargs):
    h = path.rsplit("/", 1)[-1]
    if h in LEDGER:
        return 0.01, 200, {"status": "verified"}
    return 0.01, 404, {"status": "unverified"}


def run(receipt):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "receipt.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(receipt, handle)
        old_argv = sys.argv[:]
        sys.argv = ["verify_receipts.py", path]
        try:
            try:
                vr.main()
                return 0
            except SystemExit as exc:
                return exc.code
        finally:
            sys.argv = old_argv


def main():
    vr.c.call = fake_call
    old_key = os.environ.get("MVR_API_KEY")
    try:
        os.environ["MVR_API_KEY"] = "test-key"
        check(
            "genuine authority hash verifies",
            run({"immutable_audit_hash": "a" * 64, "stable_content_hash": "c" * 64}) == 0,
        )
        check(
            "descriptive authority hash verifies",
            run({"strategy_sparring_immutable_receipt_hash": "a" * 64}) == 0,
        )
        check("tampered authority hash fails", run({"immutable_audit_hash": "f" * 64}) == 1)
        check("content-only receipt has no authority", run({"stable_content_hash": "a" * 64}) == 2)
        os.environ.pop("MVR_API_KEY", None)
        check("missing key exits unavailable", run({"immutable_audit_hash": "a" * 64}) == 3)
    finally:
        if old_key is None:
            os.environ.pop("MVR_API_KEY", None)
        else:
            os.environ["MVR_API_KEY"] = old_key

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - receipt verification exit contract holds.")


if __name__ == "__main__":
    main()
