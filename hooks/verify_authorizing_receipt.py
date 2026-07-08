"""Optional online-strict verification for the authorizing decision-log receipt.

This helper verifies that the latest non-settlement entry's kernel_receipts carry
at least one hash the live ledger confirms. It is opt-in because commit-time network
dependencies are a product choice, not the default local developer experience.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spine"))
import mvr_client as c  # noqa: E402


HEX64 = re.compile(r"^[0-9a-f]{64}$")
AUTHORITY_KEYS = (
    "semantic_decision_hash",
    "immutable_audit_hash",
    "response_hash",
    "provenance_hash",
    "full_response_hash",
    "immutable_receipt_hash",
)


def _authority_hashes(entry):
    receipts = entry.get("kernel_receipts") or {}
    found = []
    for key in AUTHORITY_KEYS:
        value = receipts.get(key)
        if isinstance(value, str) and HEX64.match(value):
            found.append((key, value))
    return found


def authorizing_receipt_status(project_dir):
    log_path = os.path.join(project_dir, "mvr", "decision-log.json")
    if not os.path.exists(log_path):
        return "no_log", "no decision log present"
    try:
        entries = json.load(open(log_path, encoding="utf-8-sig"))
        latest = next(
            (entry for entry in reversed(entries) if isinstance(entry, dict) and entry.get("entry_type") != "settlement"),
            None,
        )
    except Exception as exc:
        return "no_log", f"unreadable log ({exc})"
    if not isinstance(latest, dict):
        return "no_receipt", "no readable authorizing entry"
    hashes = _authority_hashes(latest)
    if not hashes:
        return "no_receipt", "authorizing entry carries no kernel authority hash to verify"
    any_offline = False
    for key, value in hashes:
        _, status, body = c.call(f"/v1/ledger/verify/{value}", timeout=30)
        if status == 0:
            any_offline = True
            continue
        if status == 200 and isinstance(body, dict) and body.get("status") == "verified":
            return "verified", f"{key} verified against kernel ledger"
    if any_offline:
        return "offline", "ledger unreachable; strict check cannot run"
    return "unverified", "no authorizing kernel hash verified; decision log may be forged or from another kernel"


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    status, detail = authorizing_receipt_status(project_dir)
    print(f"[authorizing-receipt] {status}: {detail}")
    sys.exit(1 if status == "unverified" else 0)


if __name__ == "__main__":
    main()
