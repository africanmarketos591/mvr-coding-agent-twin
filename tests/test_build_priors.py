"""Offline tests for advisory outcome-prior generation."""
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "build_priors.py"))
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "mvr", "decision-log.json")
        out = os.path.join(d, "governance", "outcome_priors.json")
        os.makedirs(os.path.dirname(log), exist_ok=True)
        entries = [
            {
                "entry_id": "DL-1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "charter_ref": "charter.md",
                "archetype": "agri_trade",
                "market_scope": "UG-KE",
                "verdict": "permission_not_yet_earned",
                "redirect_pattern": "directory_over_wallet",
            },
            {
                "entry_id": "SET-1",
                "entry_type": "settlement",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "charter_ref": "charter.md",
                "settlement": {
                    "outcome": "partial",
                    "summary": "Two cooperatives used the directory; no wallet launched.",
                    "sources": ["evidence://pilot-log"],
                },
            },
        ]
        json.dump(entries, open(log, "w", encoding="utf-8"))
        p = subprocess.run([sys.executable, SCRIPT, "--log", log, "--out", out], capture_output=True, text=True)
        check("build_priors exits clean", p.returncode == 0, p.stderr)
        data = json.load(open(out, encoding="utf-8"))
        prior = data["priors"][0]
        check("prior is advisory only", data["policy"] == "advisory_only_no_kernel_mutation_no_claim_authorization")
        check("settlement grouped by base charter", prior["archetype"] == "agri_trade" and prior["market"] == "ug-ke")
        check("cold-start stays insufficient", prior["prior_status"] == "insufficient_prior" and prior["n"] == 1)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - outcome priors contract verified.")


if __name__ == "__main__":
    main()
