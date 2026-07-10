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
        "docs/pitch.svg",
        "docs/pitch.txt",
        "docs/notes.adoc",
        "docs/readme.md",
        "src/pitch.md",
        "tests/deck.md",
        "memory/pitch.md",
        "scripts/plan.md",
        "adapters/deck.md",
        "docs/charter.md",
        "docs/preflight.md",
        "x/mirror.md",
        "twin/notes.md",
        "mvr/deck.md",
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

    for path in ("PREFLIGHT.md", "charter.md", "mirror.md", "transcript_report.md"):
        check(f"twin artifact safe {path}", should_scan_content(path) is False)

    for path in (
        "src/app.py",
        "build.py",
        "mvr/state.json",
        "mvr/decision-log.json",
        "mvr/build_spec.json",
        "mvr/checkpoints/strategy_sparring.json",
        "mvr/public_research/source_ledger.json",
        "benchmarks/mvr-viability-v1/answer_key.json",
        "claims/investor.md",
    ):
        check(f"not scanned {path}", should_scan_content(path) is False)

    check("binary pdf carrier", binary_claim_carrier("docs/deck.pdf") is True)
    check("binary pptx carrier", binary_claim_carrier("board/board.pptx") is True)
    check("claims binary not carrier", binary_claim_carrier("claims/deck.pdf") is False)

    cls, reason, tier = classify_escalating_content("docs/deck.ipynb", PITCH)
    check("ipynb pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("docs/readme.md", PITCH)
    check("nested readme pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("src/pitch.md", PITCH)
    check("src claim doc caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("docs/pitch.svg", PITCH)
    check("svg pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("docs/charter.md", PITCH)
    check("nested charter pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("twin/notes.md", PITCH)
    check("bare twin dir pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("mvr/deck.md", PITCH)
    check("unmanaged mvr pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)
    cls, reason, tier = classify_escalating_content("benchmarks/random-pitch.md", PITCH)
    check("unmanaged benchmark pitch caught", cls is not None and tier in {"keyword", "semantic"}, reason)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - claim scan policy verified.")


if __name__ == "__main__":
    main()
