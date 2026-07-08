"""Standing adversarial fuzz harness for the claim gate.

This test exists because beta.19's gate passed confirmation tests while missing
claim-shaped payloads hidden in data, notebook, TeX, and nested readme files.
It institutionalizes falsification: sweep paths and extensions that a user could
reasonably use to smuggle a deck or rollout claim outside `claims/`.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hooks")))

from claim_gate import classify_escalating_content  # noqa: E402
from claim_scan_policy import should_scan_content  # noqa: E402

CLAIM_PAYLOADS = [
    "We will launch a national escrow wallet and hold customer deposits at rollout.",
    "This is our investor pitch deck for the Series A fundraising round.",
    "Board pack for the quarterly board report to directors.",
    "We hold members money in trust until the distributor ships.",
    "Tunashikilia akiba ya wanachama hadi usambazaji.",
]

SCAN_EXTS = [
    ".md",
    ".txt",
    ".rst",
    ".csv",
    ".tsv",
    ".yaml",
    ".yml",
    ".json",
    ".ipynb",
    ".tex",
    ".adoc",
    ".org",
    ".html",
    ".xml",
    ".svg",
    ".markdown",
    ".mdx",
]

EXEMPT_LOCATIONS = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "llms.txt",
    "PREFLIGHT.md",
    "docs/PREFLIGHT.md",
    "charter.md",
    "docs/charter.md",
    "x/mirror.md",
    "transcript_report.md",
    "src/app.py",
    "build.py",
    "mvr/state.json",
    "claims/investor_deck.md",
]

FAILS = []


def check(name, condition, detail=""):
    if not condition:
        FAILS.append(f"{name} {detail}")


def main():
    swept = 0
    for payload in CLAIM_PAYLOADS:
        for ext in SCAN_EXTS:
            for path in (f"docs/pitch{ext}", f"a/b/c/deck{ext}", f"notes/plan{ext}"):
                cls, _reason, _tier = classify_escalating_content(path, payload)
                check("caught", cls is not None, f"MISS: {path} :: {payload[:40]!r}")
                swept += 1

    for name in ("readme.md", "changelog.md", "notes.md", "index.md"):
        cls, _reason, _tier = classify_escalating_content(
            f"docs/{name}",
            "national escrow wallet at rollout, investor pitch deck",
        )
        check("nested-doc-scanned", cls is not None, f"MISS nested {name}")
        swept += 1

    for path in ("src/pitch.md", "tests/deck.md", "memory/pitch.md", "scripts/plan.md", "adapters/deck.md"):
        cls, _reason, _tier = classify_escalating_content(
            path,
            "national escrow wallet at rollout, investor pitch deck",
        )
        check("generic-dir-doc-scanned", cls is not None, f"MISS generic dir {path}")
        swept += 1

    for location in EXEMPT_LOCATIONS:
        check("exempt-clean", should_scan_content(location) is False, f"OVER-SCAN: {location}")
        swept += 1

    print(f"fuzz sweep: {swept} cases")
    if FAILS:
        print(f"FUZZ FAIL ({len(FAILS)}):")
        for failure in FAILS[:20]:
            print("  -", failure)
        sys.exit(1)
    print("ALL PASS - no claim payload evaded the gate; no exempt surface over-scanned.")


if __name__ == "__main__":
    main()
