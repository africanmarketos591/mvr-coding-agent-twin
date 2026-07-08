"""Cross-project MVR Twin memory.

Each project remains one case per repo. The home directory carries only
user-owned passport reach and aggregate outcome priors across those projects.
It never copies raw evidence packs or project secrets.

Default home: ~/.mvr-twin
Override: MVR_TWIN_HOME or --home
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from build_priors import build, load_entries  # noqa: E402
from passport_check import validate_structure  # noqa: E402


STATUS_RANK = {"self_reported": 0, "lapsed": 1, "confirmation_requested": 2, "attested": 3}
PRIOR_KEY = ("archetype", "market", "verdict", "redirect_pattern")
SCHEMA_DEFAULT = os.path.join(PKG, "memory", "passport.schema.json")


def now():
    return datetime.now(timezone.utc).isoformat()


def default_home():
    return os.environ.get("MVR_TWIN_HOME") or os.path.join(os.path.expanduser("~"), ".mvr-twin")


def read_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def write_json(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def empty_passport():
    return {
        "passport_id": "op-home",
        "created_at": now(),
        "updated_at": now(),
        "operator": {"display_name": "operator"},
        "reach": {"named_counterparties": []},
        "capacity": {},
        "verification": {"status": "self_reported", "attestation_refs": []},
        "consent": {
            "storage_consented": True,
            "disclosure_per_run": True,
            "consent_basis": "consent",
        },
    }


def recompute_verification(passport):
    counterparties = (passport.get("reach") or {}).get("named_counterparties", []) or []
    attested = [item for item in counterparties if item.get("status") == "attested"]
    refs = sorted({
        item["attestation_ref"]
        for item in attested
        if item.get("attestation_ref")
    })
    verification = passport.setdefault("verification", {})
    if not counterparties:
        verification["status"] = "self_reported"
    elif attested and len(attested) == len(counterparties):
        verification["status"] = "attested"
    elif attested:
        verification["status"] = "partially_attested"
    else:
        verification["status"] = "self_reported"
    verification["attestation_refs"] = refs
    if refs:
        verification["last_attestation_at"] = now()
    passport["updated_at"] = now()


def merge_passport(home_passport, project_passport):
    home_items = home_passport.setdefault("reach", {}).setdefault("named_counterparties", [])
    index = {(item.get("label"), item.get("role")): item for item in home_items}
    project_items = (project_passport.get("reach") or {}).get("named_counterparties", []) or []
    for item in project_items:
        key = (item.get("label"), item.get("role"))
        if not key[0] or not key[1]:
            continue
        existing = index.get(key)
        existing_rank = STATUS_RANK.get((existing or {}).get("status"), 0)
        incoming_rank = STATUS_RANK.get(item.get("status"), 0)
        if existing and incoming_rank <= existing_rank:
            continue
        if existing:
            existing.update(item)
        else:
            copied = dict(item)
            home_items.append(copied)
            index[key] = copied
    recompute_verification(home_passport)


def merge_priors(all_entries, min_n=5):
    return {
        "format": "mvr_home_outcome_priors_v1",
        "updated_at": now(),
        "policy": "advisory_only_cross_project_no_raw_evidence",
        "minimum_n": min_n,
        "priors": build(all_entries, min_n) if all_entries else [],
    }


def settlement_counts(entries):
    counts = {"hit": 0, "partial": 0, "miss": 0, "unresolvable": 0}
    for entry in entries:
        if entry.get("entry_type") != "settlement":
            continue
        outcome = (entry.get("settlement") or {}).get("outcome")
        if outcome in counts:
            counts[outcome] += 1
    return counts


def load_portfolio(home):
    portfolio = read_json(os.path.join(home, "portfolio.json"), {"projects": []})
    portfolio["projects"] = list(portfolio.get("projects") or [])
    return portfolio


def recompute_home(home, portfolio):
    home_passport = empty_passport()
    all_entries = []
    for project_record in portfolio["projects"]:
        project = project_record["project"]
        project_passport = read_json(os.path.join(project, "mvr", "passport.json"), None)
        if project_passport:
            merge_passport(home_passport, project_passport)
        entries = load_entries(os.path.join(project, "mvr", "decision-log.json"))
        all_entries.extend(entries)
        project_record["settled"] = settlement_counts(entries)
    write_json(os.path.join(home, "passport.json"), home_passport)
    write_json(os.path.join(home, "outcome_priors.json"), merge_priors(all_entries))
    write_json(os.path.join(home, "portfolio.json"), portfolio)


def cmd_init(home):
    os.makedirs(home, exist_ok=True)
    if not os.path.exists(os.path.join(home, "passport.json")):
        write_json(os.path.join(home, "passport.json"), empty_passport())
    if not os.path.exists(os.path.join(home, "outcome_priors.json")):
        write_json(os.path.join(home, "outcome_priors.json"), merge_priors([]))
    if not os.path.exists(os.path.join(home, "portfolio.json")):
        write_json(os.path.join(home, "portfolio.json"), {"projects": []})
    print(f"initialized MVR Twin home at {home}")


def cmd_pull(home, project):
    cmd_init(home)
    project_abs = os.path.abspath(project)
    portfolio = load_portfolio(home)
    portfolio["projects"] = [
        item for item in portfolio["projects"]
        if item.get("project") != project_abs
    ]
    portfolio["projects"].append({"project": project_abs, "pulled_at": now()})
    recompute_home(home, portfolio)
    passport = read_json(os.path.join(home, "passport.json"), empty_passport())
    priors = read_json(os.path.join(home, "outcome_priors.json"), {"priors": []})
    attested = sum(
        1 for item in (passport.get("reach") or {}).get("named_counterparties", [])
        if item.get("status") == "attested"
    )
    print(
        f"pulled {project_abs}: home has {attested} attested counterparties, "
        f"{len(priors.get('priors', []))} prior buckets, "
        f"{len(load_portfolio(home)['projects'])} projects."
    )


def cmd_export(home, project, force):
    passport = read_json(os.path.join(home, "passport.json"), None)
    if not passport:
        print("home has no passport; run --init and --pull first. (exit 3)")
        sys.exit(3)
    dst_passport = os.path.join(project, "mvr", "passport.json")
    if os.path.exists(dst_passport) and not force:
        print(f"{dst_passport} exists; use --force to overwrite. (exit 2)")
        sys.exit(2)
    write_json(dst_passport, passport)
    write_json(
        os.path.join(project, "mvr", "outcome_priors.json"),
        read_json(os.path.join(home, "outcome_priors.json"), merge_priors([])),
    )
    attested = sum(
        1 for item in (passport.get("reach") or {}).get("named_counterparties", [])
        if item.get("status") == "attested"
    )
    print(f"seeded {project}: {attested} attested counterparties and cross-project priors exported.")


def cmd_status(home):
    cmd_init(home)
    passport = read_json(os.path.join(home, "passport.json"), empty_passport())
    priors = read_json(os.path.join(home, "outcome_priors.json"), {"priors": []}).get("priors", [])
    portfolio = load_portfolio(home).get("projects", [])
    print("=" * 60)
    print(f"MVR TWIN HOME - {home}")
    print("=" * 60)
    print(f"passport verification={passport.get('verification', {}).get('status')}")
    attested = [
        item for item in (passport.get("reach") or {}).get("named_counterparties", [])
        if item.get("status") == "attested"
    ]
    for item in attested:
        print(f"  [attested] {item.get('label')} ({item.get('role')}) ref={item.get('attestation_ref')}")
    if not attested:
        print("  no attested counterparties yet; reach remains self-reported/0.30.")
    print(f"market prior buckets={len(priors)}")
    totals = {"hit": 0, "partial": 0, "miss": 0}
    for project in portfolio:
        settled = project.get("settled") or {}
        for key in totals:
            totals[key] += settled.get(key, 0)
    resolved = sum(totals.values())
    if resolved:
        alive = round(100 * (totals["hit"] + totals["partial"]) / resolved)
        print(
            f"portfolio survival={alive}% "
            f"(hit={totals['hit']} partial={totals['partial']} miss={totals['miss']})"
        )


def validate_home_passport(home, schema_path):
    passport = read_json(os.path.join(home, "passport.json"), {})
    schema = read_json(schema_path, {})
    errors = validate_structure(passport, schema)
    if errors:
        print("WARN: home passport failed validation:")
        for error in errors:
            print(f"  - {error}")


def main():
    parser = argparse.ArgumentParser(description="Manage cross-project MVR Twin home memory.")
    parser.add_argument("--home", default=None)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--pull")
    parser.add_argument("--export")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--schema", default=SCHEMA_DEFAULT)
    args = parser.parse_args()

    home = os.path.abspath(args.home or default_home())
    if args.init:
        cmd_init(home)
    if args.pull:
        cmd_pull(home, args.pull)
        validate_home_passport(home, args.schema)
    elif args.export:
        cmd_export(home, args.export, args.force)
    elif args.status or not args.init:
        cmd_status(home)


if __name__ == "__main__":
    main()
