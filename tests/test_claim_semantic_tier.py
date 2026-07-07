"""Offline tests for the escalate-only semantic/multilingual claim tier."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hooks")))
from claim_gate import classify_content  # noqa: E402
from claim_semantic_tier import classify_escalating  # noqa: E402


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def main():
    path = "docs/note.md"
    check(
        "keyword floor misses English paraphrase",
        classify_content(path, "We hold members money in trust until dispatch.")[0] is None,
    )
    claim, _, tier = classify_escalating(path, "We hold members money in trust until dispatch.")
    check("semantic tier catches English paraphrase", claim == "national_rollout" and tier == "semantic")

    claim, _, tier = classify_escalating(path, "Tunashikilia akiba ya wanachama hadi usambazaji.")
    check("semantic tier catches Swahili", claim == "national_rollout" and tier == "semantic")

    claim, _, tier = classify_escalating(path, "Tukuuma ssente zabalimi okutuusa nga bituuse.")
    check("semantic tier catches Luganda", claim == "national_rollout" and tier == "semantic")

    claim, _, tier = classify_escalating(path, "We will design an internal order aggregation data model.")
    check("benign text stays clean", claim is None and tier == "none")

    keyword_claim, _ = classify_content(path, "We will launch a national escrow wallet and hold customer deposits.")
    claim, _, tier = classify_escalating(path, "We will launch a national escrow wallet and hold customer deposits.")
    check("keyword hit is preserved", keyword_claim == claim and tier == "keyword")

    claim, _, tier = classify_escalating("mvr/state.json", "We hold members money in trust.")
    check("skip-segment path not escalated", claim is None and tier == "none")

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - semantic tier is escalate-only and multilingual.")


if __name__ == "__main__":
    main()
