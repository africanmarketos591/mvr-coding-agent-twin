"""Operator Passport validator and consent gate.

The claim surface is hook-enforced, but the Operator Passport is personal data
and must not be disclosed into a charter run on honor-system consent. This
script validates `mvr/passport.json` against the shipped schema's required
fields, checks the per-run consent gate, and reports attestation status.

It makes no network calls and never upgrades evidence weights. Attestation
upgrades remain kernel-side through `/v1/field-signal/*`.

Usage:
  python scripts/passport_check.py --passport mvr/passport.json

Exit codes:
  0 valid + disclosable
  1 schema-invalid
  2 consent gate failed
  3 passport missing
"""
import argparse
import json
import os
import sys

SCHEMA_DEFAULT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "memory",
    "passport.schema.json",
)
COUNTERPARTY_STATUS = {"self_reported", "confirmation_requested", "attested", "lapsed"}
VERIFICATION_STATUS = {"self_reported", "partially_attested", "attested"}
CONSENT_BASIS = {"consent", "contract", "legitimate_interest"}


def load(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def validate_structure(passport, schema):
    errors = []
    for key in schema.get("required", []):
        if key not in passport:
            errors.append(f"missing required top-level field: {key}")

    verification = passport.get("verification") or {}
    if verification.get("status") not in VERIFICATION_STATUS:
        errors.append(f"verification.status invalid: {verification.get('status')!r}")

    counterparties = (passport.get("reach") or {}).get("named_counterparties", []) or []
    for index, counterparty in enumerate(counterparties):
        if not isinstance(counterparty, dict):
            errors.append(f"reach.named_counterparties[{index}] is not an object")
            continue
        for required in ("role", "relationship", "status"):
            if not counterparty.get(required):
                errors.append(f"reach.named_counterparties[{index}] missing {required}")
        status = counterparty.get("status")
        if status and status not in COUNTERPARTY_STATUS:
            errors.append(f"reach.named_counterparties[{index}].status invalid: {status!r}")
    return errors


def consent_gate(passport):
    """Return `(ok, reasons)` for passport disclosure into this run."""
    consent = passport.get("consent") or {}
    reasons = []
    if consent.get("storage_consented") is not True:
        reasons.append("consent.storage_consented is not true")
    if consent.get("consent_basis") not in CONSENT_BASIS:
        reasons.append(f"consent.consent_basis invalid/absent: {consent.get('consent_basis')!r}")
    if consent.get("disclosure_per_run") is not True:
        reasons.append("consent.disclosure_per_run is not true")
    return not reasons, reasons


def attestation_summary(passport):
    summary = {}
    counterparties = (passport.get("reach") or {}).get("named_counterparties", []) or []
    for counterparty in counterparties:
        status = counterparty.get("status", "unknown")
        summary[status] = summary.get(status, 0) + 1
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--passport", default=os.path.join("mvr", "passport.json"))
    parser.add_argument("--schema", default=SCHEMA_DEFAULT)
    args = parser.parse_args()

    if not os.path.exists(args.passport):
        print(
            f"no passport at {args.passport} - Operator Seat runs inference-only; "
            "all operator facts remain self_reported/0.30. (exit 3)"
        )
        sys.exit(3)

    passport = load(args.passport)
    schema = load(args.schema)

    errors = validate_structure(passport, schema)
    if errors:
        print("PASSPORT INVALID:")
        for error in errors:
            print("  -", error)
        sys.exit(1)
    print("PASSPORT STRUCTURE: valid against memory/passport.schema.json")

    summary = attestation_summary(passport)
    attested = summary.get("attested", 0)
    self_reported = summary.get("self_reported", 0)
    print(
        f"REACH ATTESTATION: {summary or 'no named counterparties'} "
        f"({attested} attested, {self_reported} self_reported/0.30)"
    )
    if self_reported and not attested:
        print(
            "  NOTE: all reach is self_reported (0.30). Distribution claims that "
            "depend on it stay at founder_intuition weight until field-signal attestation."
        )

    ok, reasons = consent_gate(passport)
    if not ok:
        print("CONSENT GATE: FAIL - passport may NOT be disclosed to a charter run:")
        for reason in reasons:
            print("  -", reason)
        print("  Kenya DPA 2019 / Uganda DPPA 2019 floor: no lawful basis, no disclosure.")
        sys.exit(2)

    print(f"CONSENT GATE: pass (basis={passport['consent']['consent_basis']})")
    print("PASSPORT OK - structurally valid, consented, attestation status reported.")


if __name__ == "__main__":
    main()
