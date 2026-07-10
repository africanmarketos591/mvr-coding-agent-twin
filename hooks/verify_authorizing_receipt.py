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
AUTHORITY_KEY_FRAGMENTS = (
    "immutable_audit_hash",
    "response_hash",
    "provenance_hash",
    "full_response_hash",
    "immutable_receipt_hash",
    "receipt_hash",
    "audit_hash",
)
CONTENT_KEY_FRAGMENTS = (
    "stable_content_hash",
    "evidence_bundle_hash",
    "charter_hash",
    "content_hash",
    "canonical_sha256",
)


def _walk_hashes(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            dotted = f"{prefix}{key}"
            if isinstance(value, str) and HEX64.match(value):
                yield dotted, key, value
            else:
                yield from _walk_hashes(value, dotted + ".")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            yield from _walk_hashes(item, f"{prefix}{idx}.")


def _is_authority_key(key):
    lowered = key.lower()
    if lowered in AUTHORITY_KEYS:
        return True
    if any(fragment in lowered for fragment in CONTENT_KEY_FRAGMENTS):
        return False
    return any(fragment in lowered for fragment in AUTHORITY_KEY_FRAGMENTS)


def _authority_hashes(entry):
    receipts = entry.get("kernel_receipts") or {}
    found = []
    for dotted, key, value in _walk_hashes(receipts):
        if _is_authority_key(key):
            found.append((dotted, value))
    return found


def authority_hashes(entry):
    """Public classifier shared by run-audit tooling; content hashes never qualify."""
    return _authority_hashes(entry if isinstance(entry, dict) else {})


def authorizing_receipt_status(project_dir):
    log_path = next(
        (
            os.path.join(project_dir, "mvr", name)
            for name in ("decision-log.json", "decision-log.seed.json")
            if os.path.exists(os.path.join(project_dir, "mvr", name))
        ),
        None,
    )
    if not log_path:
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
    if not os.environ.get("MVR_API_KEY", "").strip():
        return "no_key", "MVR_API_KEY not set; strict receipt verification cannot run"
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
    if status == "unverified":
        sys.exit(1)
    if status in {"no_log", "no_receipt"}:
        sys.exit(2)
    if status in {"offline", "no_key"}:
        sys.exit(3)
    sys.exit(0 if status == "verified" else 1)


if __name__ == "__main__":
    main()
