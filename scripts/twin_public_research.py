"""Create and validate a public-source research pack.

The Twin should push host agents to research what is publicly verifiable instead
of asking the user or laundering memory into facts. This script creates a
source-ledger skeleton and validates that public claims carry source, URL,
access date, status, and claim class before they enter a Build Charter.

It does not browse automatically. The host agent must use its browser/search
tools, fill the ledger, then validate it. Optional `--check-urls` verifies that
HTTP(S) source URLs are reachable.
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from urllib import error, request


FORMAT = "mvr_public_research_pack_v1"
CLAIM_CLASSES = {
    "incumbent",
    "regulation",
    "licence_cost",
    "rail_owner",
    "guardian",
    "market_figure",
    "failure_precedent",
    "public_counterparty",
    "other",
}
SOURCE_TYPES = {"regulator", "registry", "dataset", "news", "company", "academic", "official", "other"}
STATUSES = {"verified", "unknown", "rejected"}
AUTHORITY_REQUIRED_CLASSES = {"regulation", "licence_cost", "guardian"}
AUTHORITY_SOURCE_TYPES = {"regulator", "registry", "official"}


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def queries_for(idea, country, archetypes):
    clipped = " ".join(idea.strip().split())
    if len(clipped) > 100:
        clipped = clipped[:97] + "..."
    archetype_text = " ".join(archetypes)
    return [
        f"{country} {archetype_text} incumbent alternatives for {clipped}",
        f"{country} regulator licence requirements {archetype_text}",
        f"{country} payment logistics identity distribution rails owner {archetype_text}",
        f"{country} failed startup case study {archetype_text} regulation market entry",
        f"{country} market size statistics {archetype_text} official source",
    ]


def template_entries(country):
    return [
        {
            "claim": "UNKNOWN - named incumbent or informal substitute",
            "claim_class": "incumbent",
            "source_name": "",
            "source_type": "other",
            "url": "",
            "access_date": str(date.today()),
            "status": "unknown",
            "used_for": "eclipse",
            "notes": "Replace with public source or keep UNKNOWN with reason.",
        },
        {
            "claim": f"UNKNOWN - licence or regulator gate in {country}",
            "claim_class": "regulation",
            "source_name": "",
            "source_type": "regulator",
            "url": "",
            "access_date": str(date.today()),
            "status": "unknown",
            "used_for": "permission",
            "notes": "Use regulator/official/registry source. Keep as UNKNOWN if only secondary sources exist.",
        },
        {
            "claim": f"UNKNOWN - rail owner in {country}",
            "claim_class": "rail_owner",
            "source_name": "",
            "source_type": "official",
            "url": "",
            "access_date": str(date.today()),
            "status": "unknown",
            "used_for": "rails",
            "notes": "Name who owns payments, logistics, identity, or distribution rails.",
        },
    ]


def init_pack(root, idea, country, archetypes):
    out_dir = os.path.join(root, "mvr", "public_research")
    ledger = {
        "format": FORMAT,
        "idea": idea,
        "country": country,
        "archetypes": archetypes,
        "policy": "public_claims_need_dated_sources_or_UNKNOWN",
        "entries": template_entries(country),
    }
    write_json(os.path.join(out_dir, "source_ledger.json"), ledger)
    query_lines = "\n".join(f"- {query}" for query in queries_for(idea, country, archetypes))
    write_text(
        os.path.join(out_dir, "PUBLIC_RESEARCH.md"),
        f"""# PUBLIC RESEARCH PACK

Run this before named public facts enter the Build Charter.

Idea: {idea}
Country / market: {country}
Archetype(s): {', '.join(archetypes)}

## Agent instruction

Use browser/search tools for facts that are publicly verifiable. Do not ask the
user for researchable facts. Fill `source_ledger.json`, then run:

```bash
python scripts/twin_public_research.py --validate --ledger mvr/public_research/source_ledger.json
```

If a fact cannot be established, keep it as `UNKNOWN` and explain why. Unknown
regulated facts cannot authorize claims or unlock launch language.

## Search queue

{query_lines}

## Required public claim classes

- incumbent
- regulation
- licence_cost when the charter mentions fees/capital
- rail_owner
- guardian or public_counterparty when public gatekeepers are named
- market_figure when statistics appear
- failure_precedent when a failure case is used

Authority-grade rule: `regulation`, `licence_cost`, and `guardian` entries
may be marked `verified` only when the source type is regulator, official, or
registry. Secondary/practitioner sources can guide research, but they stay
UNKNOWN until authority-grade support is attached.
""",
    )
    return out_dir


def valid_date(value):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(value or "")))


def valid_url(value):
    return str(value or "").startswith(("http://", "https://"))


def check_url(url, timeout=10):
    req = request.Request(url, method="HEAD", headers={"User-Agent": "mvr-twin-public-research/1.0"})
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 400, response.status
    except error.HTTPError as exc:
        if exc.code == 405:
            req = request.Request(url, method="GET", headers={"User-Agent": "mvr-twin-public-research/1.0"})
            with request.urlopen(req, timeout=timeout) as response:
                return 200 <= response.status < 400, response.status
        return False, exc.code
    except Exception as exc:
        return False, str(exc)[:120]


def validate_ledger(path, check_urls=False):
    errors = []
    warnings = []
    ledger = read_json(path)
    if ledger.get("format") != FORMAT:
        errors.append(f"format must be {FORMAT!r}")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        entries = []
    verified_count = 0
    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        for field in ("claim", "claim_class", "source_name", "source_type", "url", "access_date", "status", "used_for"):
            if field not in entry:
                errors.append(f"{prefix} missing {field}")
        claim_class = entry.get("claim_class")
        source_type = entry.get("source_type")
        status = entry.get("status")
        if claim_class and claim_class not in CLAIM_CLASSES:
            errors.append(f"{prefix}.claim_class invalid: {claim_class!r}")
        if source_type and source_type not in SOURCE_TYPES:
            errors.append(f"{prefix}.source_type invalid: {source_type!r}")
        if status and status not in STATUSES:
            errors.append(f"{prefix}.status invalid: {status!r}")
        if not valid_date(entry.get("access_date")):
            errors.append(f"{prefix}.access_date must be YYYY-MM-DD")
        if status == "verified":
            verified_count += 1
            if claim_class in AUTHORITY_REQUIRED_CLASSES and source_type not in AUTHORITY_SOURCE_TYPES:
                errors.append(
                    f"{prefix}.source_type must be regulator/official/registry for verified {claim_class!r} claims"
                )
            if not entry.get("source_name"):
                errors.append(f"{prefix}.source_name required for verified entries")
            if not valid_url(entry.get("url")):
                errors.append(f"{prefix}.url must be http(s) for verified public entries")
            elif check_urls:
                ok, detail = check_url(entry["url"])
                if not ok:
                    errors.append(f"{prefix}.url not reachable: {detail}")
        if status == "unknown" and not entry.get("notes"):
            errors.append(f"{prefix}.notes required for UNKNOWN entries")
        if status == "rejected" and not entry.get("notes"):
            errors.append(f"{prefix}.notes required for rejected entries")
    if verified_count == 0:
        warnings.append("no verified public entries yet; charter public facts must stay UNKNOWN")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Create or validate a public research source ledger.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--idea", default="")
    parser.add_argument("--country", default="")
    parser.add_argument("--archetype", action="append", default=[])
    parser.add_argument("--ledger")
    parser.add_argument("--check-urls", action="store_true")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if args.init:
        if not args.idea or not args.country or not args.archetype:
            print("--init requires --idea, --country, and at least one --archetype")
            sys.exit(2)
        out_dir = init_pack(root, args.idea, args.country, args.archetype)
        print(f"public research pack written -> {out_dir}")

    if args.validate:
        ledger = args.ledger or os.path.join(root, "mvr", "public_research", "source_ledger.json")
        errors, warnings = validate_ledger(ledger, args.check_urls)
        for warning in warnings:
            print(f"WARN: {warning}")
        if errors:
            print("PUBLIC RESEARCH LEDGER INVALID:")
            for item in errors:
                print(f"  - {item}")
            sys.exit(1)
        print("PUBLIC RESEARCH LEDGER OK - public claims have source/status/date discipline.")
    elif not args.init:
        print("choose --init and/or --validate")
        sys.exit(2)


if __name__ == "__main__":
    main()
