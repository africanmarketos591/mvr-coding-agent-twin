"""Preregister a Build Charter: canonical hash + timestamp + anchor block.

Usage:
  python scripts/preregister.py path/to/charter.md
  python scripts/preregister.py --verify path/to/charter.md

The canonical hash normalizes only the self-referential preregistration header
field, so inserting the resulting hash/anchor text does not invalidate the hash.
Any change to the prediction body, settlement criteria, sources, or verdict still
changes the hash and requires rerunning this script.

Anchoring (public git commit / Wayback / Zenodo) is a human step by protocol -
this script emits the exact instructions and a decision-log skeleton.
"""
import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone


HASH_RE = re.compile(r"\*\*Preregistration hash:\*\*\s*([0-9a-fA-F]{64})")
HEADER_MARKER = "**Preregistration hash:**"


def canonical_bytes(path):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        if "**Preregistration hash:**" in line:
            prefix = line.split("**Preregistration hash:**", 1)[0]
            line = (
                prefix
                + "**Preregistration hash:** <canonical-preregistration-hash> "
                + "(anchors: <anchor-refs>)"
            )
        lines.append(line)
    text = "\n".join(lines).rstrip() + "\n"
    return text.encode("utf-8")


def digest_for(path):
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def embedded_hash(path):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig", errors="replace")
    match = HASH_RE.search(text)
    return match.group(1).lower() if match else None


def preregistration_header_count(path):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig", errors="replace")
    return text.count(HEADER_MARKER)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Verify embedded hash against canonical hash.")
    parser.add_argument("charter", help="Path to Build Charter markdown file.")
    args = parser.parse_args()

    path = args.charter
    header_count = preregistration_header_count(path)
    if header_count != 1:
        print(
            f"FAIL: expected exactly one '{HEADER_MARKER}' line; found {header_count}. "
            "Duplicate or missing preregistration headers are ambiguous and fail closed."
        )
        sys.exit(2)

    digest = digest_for(path)

    if args.verify:
        embedded = embedded_hash(path)
        if not embedded:
            print("FAIL: no embedded 64-character preregistration hash found.")
            sys.exit(2)
        if embedded != digest:
            print(f"FAIL: embedded hash {embedded} != canonical hash {digest}")
            sys.exit(1)
        print(f"PASS: embedded preregistration hash matches canonical hash {digest}")
        return

    now = datetime.now(timezone.utc).isoformat()
    entry_id = f"PR-{uuid.uuid4()}"
    block = {
        "preregistration": {
            "charter_file": path,
            "sha256": digest,
            "hash_mode": "canonical-charter-v2",
            "registered_at": now,
            "entry_id": entry_id,
            "anchor_instructions": [
                "1. Commit this charter to a PUBLIC git repository (hash becomes independently timestamped).",
                "2. Submit the raw file URL to the Wayback Machine (second independent anchor).",
                "3. Flagship charters: Zenodo deposit for a DOI (third anchor).",
                "Protocol: >=2 external anchors before the charter counts as preregistered.",
            ],
            "anchor_refs": [],
        }
    }
    print(json.dumps(block, indent=2))
    print(
        "\n# Embed in charter header exactly:\n"
        f"**Preregistration hash:** {digest} (anchors: <git-commit>, <wayback-url>)"
    )
    print(
        "\n# Decision-log skeleton:\n"
        + json.dumps(
            {
                "entry_id": entry_id.replace("PR-", "DL-"),
                "timestamp": now,
                "checkpoint": "pre_charter",
                "charter_ref": path,
                "charter_hash": digest,
                "charter_hash_mode": "canonical-charter-v2",
                "settlement": {
                    "preregistered": False,
                    "anchor_refs": [],
                    "note": "Set preregistered true only after >=2 external anchors exist.",
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
