"""Regression tests for the hardened claim scan policy."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hooks")))

from claim_gate import classify_escalating_content  # noqa: E402
from claim_scan_policy import binary_claim_carrier, should_scan_content  # noqa: E402

PITCH = "We will launch a national escrow wallet and hold customer deposits at rollout."

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    for path in (
        "docs/pitch.csv",
        "docs/plan.yaml",
        "docs/pitch.json",
        "docs/deck.ipynb",
        "docs/pitch.tex",
        "docs/pitch.txt",
        "docs/notes.adoc",
        "docs/readme.md",
    ):
        check(f"scans {path}", should_scan_content(path) is True)

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "llms.txt",
        "LICENSE",
        "REPLICATION_RECEIPTS.md",
        "STRESS_TEST_REPORT.md",
    ):
        check(f"root safe {path}", should_scan_content(path) is False)

    for path in ("docs/agents.md", "docs/claude.md", "docs/llms.txt"):
        check(f"nested control doc scanned {path}", should_scan_content(path) is True)

    for path in ("some/dir/charter.md", "x/mirror.md", "transcript_report.md"):
        check(f"twin artifact safe {path}", should_scan_content(path) is False)

    for path in ("src/app.py", "build.py", "mvr/state.json", "claims/investor.md"):
        check(f"not scanned {path}", should_scan_content(path) is False)

    check("binary pdf carrier", binary_claim_carrier("docs/deck.pdf") is True)
    check("binary pptx carrier", binary_claim_carrier("board/board.pptx") is True)
    check("claims binary not carrier", binary_claim_carrier("claims/deck.pdf") is False)

    cls, reason, tier = classify_escalating_content("docs/deck.ipynb", PITCH)
    check("ipynb pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("docs/readme.md", PITCH)
    check("nested readme pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - claim scan policy verified.")


if __name__ == "__main__":
    main()
