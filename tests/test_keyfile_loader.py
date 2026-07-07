"""Offline tests for safe internal key-file parsing."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from keyfile_loader import extract_mvr_api_key


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def main():
    text = """MVR internal Enterprise testing key
Label: mvr-enterprise-label-not-a-key
X-API-Key: mvr_internal_actual_key_abcdefghijklmnopqrstuvwxyz1234567890
Authorization: Bearer mvr_internal_actual_key_abcdefghijklmnopqrstuvwxyz1234567890
KV key hash: key:abc123
"""
    check(
        "prefers explicit X-API-Key over label slug",
        extract_mvr_api_key(text) == "mvr_internal_actual_key_abcdefghijklmnopqrstuvwxyz1234567890",
    )

    text = "Label: mvr-enterprise-label-not-a-key\nAuthorization: Bearer bearer_value_abcdefghijklmnopqrstuvwxyz123456\n"
    check("falls back to bearer field", extract_mvr_api_key(text) == "bearer_value_abcdefghijklmnopqrstuvwxyz123456")

    text = "MVR_API_KEY=mvr-demo-key-2026\n"
    check("accepts env-style sandbox key", extract_mvr_api_key(text) == "mvr-demo-key-2026")

    try:
        extract_mvr_api_key("Label: mvr-enterprise-label-not-a-key\nKV key hash: key:abc123\n")
        check("rejects label-only file", False)
    except ValueError:
        check("rejects label-only file", True)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        raise SystemExit(1)
    print("ALL PASS - keyfile loader contract verified.")


if __name__ == "__main__":
    main()
