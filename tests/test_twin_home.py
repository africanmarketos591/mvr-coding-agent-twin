"""Tests for scripts/twin_home.py."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_home.py")
FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write_json(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def make_project(root, name, counterparty, archetype, outcome):
    project = os.path.join(root, name)
    os.makedirs(os.path.join(project, "mvr"), exist_ok=True)
    write_json(
        os.path.join(project, "mvr", "passport.json"),
        {
            "passport_id": f"op-{name}",
            "created_at": "2026-07-08T00:00:00Z",
            "reach": {
                "named_counterparties": [
                    {
                        "label": counterparty,
                        "role": "partner",
                        "relationship": "partner",
                        "status": "attested",
                        "attestation_ref": f"ref-{name}",
                    }
                ]
            },
            "capacity": {},
            "verification": {"status": "attested", "attestation_refs": [f"ref-{name}"]},
            "consent": {"storage_consented": True, "disclosure_per_run": True, "consent_basis": "consent"},
        },
    )
    write_json(
        os.path.join(project, "mvr", "decision-log.json"),
        [
            {
                "entry_id": f"{name}-base",
                "charter_ref": f"{name}.md",
                "archetype": archetype,
                "market_scope": "UG",
                "verdict": "pilot_only",
                "redirect_pattern": "coordination_layer",
            },
            {
                "entry_id": f"{name}-settlement",
                "entry_type": "settlement",
                "charter_ref": f"{name}.md",
                "settlement": {"outcome": outcome, "summary": "test", "sources": ["evidence://test"]},
            },
        ],
    )
    return project


def run(home, *args):
    return subprocess.run(
        [sys.executable, SCRIPT, "--home", home, *args],
        capture_output=True,
        text=True,
    )


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        home = os.path.join(tempdir, "home")
        first = make_project(tempdir, "project-a", "Wandegeya SACCO", "agritech_aggregator", "hit")
        second = make_project(tempdir, "project-b", "IRA insurer", "fintech_lending", "miss")

        check("init exits 0", run(home, "--init").returncode == 0)
        check("pull first exits 0", run(home, "--pull", first).returncode == 0)
        check("pull second exits 0", run(home, "--pull", second).returncode == 0)

        passport = json.load(open(os.path.join(home, "passport.json"), encoding="utf-8"))
        labels = {item["label"] for item in passport["reach"]["named_counterparties"]}
        check("home accumulates attested reach", labels == {"Wandegeya SACCO", "IRA insurer"})
        check("home verification is attested", passport["verification"]["status"] == "attested")

        priors = json.load(open(os.path.join(home, "outcome_priors.json"), encoding="utf-8"))["priors"]
        check("home accumulates two prior buckets", len(priors) == 2)
        check("hit prior retained", any(item["archetype"] == "agritech_aggregator" and item["hit_rate"] == 1.0 for item in priors))
        check("miss prior retained", any(item["archetype"] == "fintech_lending" and item["miss_rate"] == 1.0 for item in priors))

        third = os.path.join(tempdir, "project-c")
        os.makedirs(third, exist_ok=True)
        check("export exits 0", run(home, "--export", third).returncode == 0)
        exported = json.load(open(os.path.join(third, "mvr", "passport.json"), encoding="utf-8"))
        check("export seeds new project with reach", len(exported["reach"]["named_counterparties"]) == 2)
        check("export seeds priors", os.path.exists(os.path.join(third, "mvr", "outcome_priors.json")))

        run(home, "--pull", first)
        priors_after = json.load(open(os.path.join(home, "outcome_priors.json"), encoding="utf-8"))["priors"]
        agritech = [item for item in priors_after if item["archetype"] == "agritech_aggregator"][0]
        check("re-pull is idempotent", agritech["counts"]["hit"] == 1, f"hit={agritech['counts']['hit']}")
        check("status shows survival", "portfolio survival" in run(home, "--status").stdout)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - home memory carries attested reach and advisory priors across projects.")


if __name__ == "__main__":
    main()
