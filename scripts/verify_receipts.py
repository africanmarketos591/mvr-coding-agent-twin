"""PRE-EXPORT kernel-receipt verification against the live MVR ledger.

The local decision log is tamper-evident, not tamper-proof. This tool verifies
kernel authority hashes against GET /v1/ledger/verify/<hash> before export.
Content-derived hashes are informational; authority hashes must verify.

Usage:
  python scripts/verify_receipts.py mvr/checkpoints/strategy_sparring.json
  python scripts/verify_receipts.py mvr/checkpoints/
  python scripts/verify_receipts.py mvr/decision-log.json --all

Exit codes:
  0 authority hashes found and verified
  1 at least one authority hash was not verified
  2 no authority hashes found
  3 ledger unreachable
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spine"))
import mvr_client as c  # noqa: E402


HEX64 = re.compile(r"^[0-9a-f]{64}$")

AUTHORITY_HASH_KEYS = {
    "provenance_hash",
    "immutable_audit_hash",
    "response_hash",
    "full_response_hash",
    "anti_corruption_audit_hash",
    "request_hash",
    "immutable_receipt_hash",
    "semantic_decision_hash",
}
CONTENT_HASH_KEYS = {"stable_content_hash", "evidence_bundle_hash", "charter_hash"}
AUTHORITY_KEY_FRAGMENTS = {
    "provenance_hash",
    "immutable_audit_hash",
    "response_hash",
    "full_response_hash",
    "anti_corruption_audit_hash",
    "request_hash",
    "immutable_receipt_hash",
    "receipt_hash",
    "audit_hash",
    "semantic_decision_hash",
}
CONTENT_KEY_FRAGMENTS = {
    "stable_content_hash",
    "evidence_bundle_hash",
    "charter_hash",
    "content_hash",
    "canonical_sha256",
}


def is_authority_key(key):
    lowered = key.lower()
    if lowered in AUTHORITY_HASH_KEYS:
        return True
    if any(fragment in lowered for fragment in CONTENT_KEY_FRAGMENTS):
        return False
    return any(fragment in lowered for fragment in AUTHORITY_KEY_FRAGMENTS)


def is_content_key(key):
    lowered = key.lower()
    return lowered in CONTENT_HASH_KEYS or any(fragment in lowered for fragment in CONTENT_KEY_FRAGMENTS)


def walk_hashes(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            dotted = f"{prefix}{key}"
            if isinstance(value, str) and HEX64.match(value):
                yield dotted, key, value
            else:
                yield from walk_hashes(value, dotted + ".")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            yield from walk_hashes(item, f"{prefix}{idx}.")


def iter_json_files(target):
    if os.path.isdir(target):
        for name in sorted(os.listdir(target)):
            if name.endswith(".json"):
                yield os.path.join(target, name)
    else:
        yield target


def verify_hash(value):
    if not os.environ.get("MVR_API_KEY", "").strip():
        return "no_key", {"error": "MVR_API_KEY not set"}
    _, status, body = c.call(f"/v1/ledger/verify/{value}", timeout=30)
    if status == 0:
        return "unreachable", body
    if status == 200 and isinstance(body, dict) and body.get("status") == "verified":
        return "verified", body
    return "unverified", body


def load_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="receipt JSON file, directory of JSON receipts, or decision log")
    parser.add_argument("--all", action="store_true", help="verify every 64-hex hash, not only authority keys")
    args = parser.parse_args()

    seen = {}
    for path in iter_json_files(args.target):
        try:
            data = load_json(path)
        except Exception as exc:
            print(f"SKIP  {path} (unreadable: {exc})")
            continue
        for dotted, leaf, value in walk_hashes(data):
            is_authority = is_authority_key(leaf)
            is_content = is_content_key(leaf)
            if not args.all and not is_authority and not is_content:
                continue
            if value in seen:
                continue
            result, _ = verify_hash(value)
            seen[value] = (result, dotted, leaf)
            tag = "AUTHORITY" if is_authority else ("content" if is_content else "other")
            print(f"  [{result:>11}] {tag:9} {dotted} = {value[:16]}...")

    authority = {value: meta for value, meta in seen.items() if is_authority_key(meta[2])}
    if any(result in {"unreachable", "no_key"} for result, _, _ in seen.values()):
        print("\nLEDGER UNREACHABLE OR NO KEY - cannot verify now. Outage Rule: do not assert. (exit 3)")
        sys.exit(3)
    if not authority:
        print("\nNo kernel AUTHORITY receipt hashes found. Nothing to verify. (exit 2)")
        sys.exit(2)
    failed = [(value, meta) for value, meta in authority.items() if meta[0] != "verified"]
    if failed:
        print(f"\nRECEIPT VERIFICATION FAILED: {len(failed)} authority hash(es) not in the kernel ledger:")
        for value, (result, dotted, _) in failed:
            print(f"  {result}  {dotted} = {value}")
        print("An unverified authority hash means the receipt is fabricated, edited, or from another kernel. (exit 1)")
        sys.exit(1)
    print(f"\nRECEIPTS VERIFIED - {len(authority)} kernel authority hash(es) confirmed. Safe to export. (exit 0)")


if __name__ == "__main__":
    main()
