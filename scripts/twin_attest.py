"""Close the 0.30 -> attested Operator Passport loop.

The fieldkit drafts attestation requests. This script records the response in
`mvr/passport.json` after the operator has a real reference such as a signed
note, MOU, or field-signal id.

It never verifies truth by itself. It is a local passport writer with a
fail-closed rule: no counterparty can be marked `attested` without
`--attestation-ref`.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from passport_check import validate_structure  # noqa: E402


SCHEMA_DEFAULT = os.path.join(PKG, "memory", "passport.schema.json")


def now():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, fallback=None):
    if not os.path.exists(path):
        return fallback
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def slug(value):
    return "-".join(str(value).lower().strip().split()) or "operator"


def new_passport(name, country, consent_basis):
    return {
        "passport_id": f"op-{slug(name)}",
        "created_at": now(),
        "updated_at": now(),
        "operator": {
            "display_name": name,
            "base_geography": {"country": country},
        },
        "reach": {"named_counterparties": []},
        "capacity": {},
        "verification": {"status": "self_reported", "attestation_refs": []},
        "consent": {
            "storage_consented": True,
            "disclosure_per_run": True,
            "consent_basis": consent_basis,
        },
    }


def upsert_counterparty(passport, label, role, relationship, status, attestation_ref=None, will_take_call=None):
    counterparties = passport.setdefault("reach", {}).setdefault("named_counterparties", [])
    match = None
    for item in counterparties:
        if item.get("label") == label and item.get("role") == role:
            match = item
            break
    if match is None:
        match = {"label": label, "role": role}
        counterparties.append(match)
    match["relationship"] = relationship
    match["status"] = status
    if attestation_ref:
        match["attestation_ref"] = attestation_ref
    if will_take_call is not None:
        match["will_take_call"] = will_take_call
    return match


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


def validate_or_exit(passport, schema_path):
    schema = load_json(schema_path, {})
    errors = validate_structure(passport, schema)
    if errors:
        print("PASSPORT INVALID after edit; not written:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Record field attestation into mvr/passport.json.")
    parser.add_argument("--passport", default=os.path.join("mvr", "passport.json"))
    parser.add_argument("--schema", default=SCHEMA_DEFAULT)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--request", action="store_true", help="mark counterparty confirmation_requested")
    parser.add_argument("--attest", action="store_true", help="mark counterparty attested; requires --attestation-ref")
    parser.add_argument("--name", default="Founder")
    parser.add_argument("--country", default="")
    parser.add_argument("--consent-basis", default="consent")
    parser.add_argument("--counterparty")
    parser.add_argument("--role", default="")
    parser.add_argument("--relationship", default="")
    parser.add_argument("--attestation-ref")
    parser.add_argument("--will-take-call", action="store_true")
    args = parser.parse_args()

    passport = load_json(args.passport)
    if args.init:
        passport = new_passport(args.name, args.country, args.consent_basis)
    elif passport is None:
        print(f"no passport at {args.passport}; run with --init first. (exit 3)")
        sys.exit(3)

    if args.attest:
        if not args.attestation_ref:
            print(
                "REFUSED: cannot mark a counterparty 'attested' without --attestation-ref. "
                "The 0.30 rule: you cannot self-upgrade reach."
            )
            sys.exit(2)
        if not args.counterparty:
            print("--attest requires --counterparty")
            sys.exit(2)
        upsert_counterparty(
            passport,
            args.counterparty,
            args.role,
            args.relationship,
            "attested",
            args.attestation_ref,
            args.will_take_call or None,
        )
    elif args.request:
        if not args.counterparty:
            print("--request requires --counterparty")
            sys.exit(2)
        upsert_counterparty(
            passport,
            args.counterparty,
            args.role,
            args.relationship,
            "confirmation_requested",
        )

    passport["updated_at"] = now()
    recompute_verification(passport)
    validate_or_exit(passport, args.schema)
    write_json(args.passport, passport)

    counterparties = (passport.get("reach") or {}).get("named_counterparties", []) or []
    attested_count = sum(1 for item in counterparties if item.get("status") == "attested")
    print(
        f"passport {args.passport} updated (NOT committed - personal data). "
        f"verification.status={passport['verification']['status']}"
    )
    print(
        f"reach: {len(counterparties)} counterparties, {attested_count} attested, "
        f"{len(counterparties) - attested_count} still self-reported/0.30."
    )


if __name__ == "__main__":
    main()
