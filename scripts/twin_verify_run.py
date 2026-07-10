"""Audit run evidence without claiming to prove which process authored local files.

Exit contract:
  0  VERIFIED      live kernel authority + stage-local artifact consistency
  1  REJECTED      contradiction, forged/unverified receipt, or invalid artifact
  2  INCOMPLETE    required stage artifacts are missing
  3  INCONCLUSIVE  local structure may be coherent, but no live authority check

An arbitrary 64-hex string never earns exit 0. A verified kernel receipt proves
that authority exists in the ledger; it does not cryptographically prove that a
particular host process generated every local file.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "hooks"))

import preregister as prereg  # noqa: E402
import twin_build_spec as build_spec  # noqa: E402
import verify_authorizing_receipt as receipt_verifier  # noqa: E402


EXIT_BY_STATUS = {"verified": 0, "rejected": 1, "incomplete": 2, "inconclusive": 3}


def _read_json(path):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return None


def _latest_entry(root):
    for name in ("decision-log.json", "decision-log.seed.json"):
        path = os.path.join(root, "mvr", name)
        data = _read_json(path)
        if isinstance(data, list):
            entry = next(
                (
                    item for item in reversed(data)
                    if isinstance(item, dict) and item.get("entry_type") != "settlement"
                ),
                None,
            )
            if entry:
                return entry, path
        elif isinstance(data, dict):
            return data, path
    return None, None


def _record(checks, name, status, detail):
    checks.append({"name": name, "status": status, "detail": str(detail)})


def _load_key(keyfile):
    if not keyfile:
        return None
    from keyfile_loader import extract_mvr_api_key

    with open(keyfile, encoding="utf-8-sig") as handle:
        return extract_mvr_api_key(handle.read())


def _charter_path(root, entry, contract):
    fingerprint = ((contract or {}).get("source_fingerprints") or {}).get("charter") or {}
    reference = fingerprint.get("path") or (entry or {}).get("charter_ref") or "charter.md"
    path = os.path.abspath(os.path.join(root, str(reference)))
    try:
        inside = os.path.commonpath([root, path]) == root
    except ValueError:
        inside = False
    return path if inside else None


def audit_run(root, keyfile=None, stage="build"):
    root = os.path.abspath(root)
    checks = []
    rejected = False
    incomplete = False
    authority_inconclusive = False

    entry, log_path = _latest_entry(root)
    if not entry:
        _record(checks, "decision_log", "missing", "no decision-log.json or decision-log.seed.json")
        return {
            "status": "incomplete", "stage": stage, "checks": checks,
            "boundary": "No statement about Twin execution can be made without a decision log.",
        }
    _record(checks, "decision_log", "pass", os.path.relpath(log_path, root).replace("\\", "/"))

    packet_path = os.path.join(root, "mvr", "committee_packet.json")
    packet = _read_json(packet_path)
    if not isinstance(packet, dict):
        incomplete = True
        _record(checks, "committee_packet", "missing", "mvr/committee_packet.json is required")
        packet = {}
    else:
        _record(checks, "committee_packet", "pass", "readable")

    entry_hashes = receipt_verifier.authority_hashes(entry)
    packet_hashes = receipt_verifier.authority_hashes({"kernel_receipts": packet.get("kernel_receipts") or {}})
    entry_values = {value for _, value in entry_hashes}
    packet_values = {value for _, value in packet_hashes}
    if entry_values and packet_values and not entry_values.intersection(packet_values):
        rejected = True
        _record(checks, "receipt_binding", "fail", "committee packet and decision log carry disjoint authority hashes")
    elif entry_values:
        _record(checks, "receipt_binding", "pass", f"{len(entry_values)} candidate authority hash(es)")
    else:
        _record(checks, "receipt_binding", "unavailable", "no authority hash present")

    seats = packet.get("seats_sat") if isinstance(packet.get("seats_sat"), dict) else {}
    routes_asserted = bool((entry.get("kernel_receipts") or {}).get("routes_called"))
    false_authority = []
    if not entry_values:
        if seats.get("spine") is True:
            false_authority.append("seats_sat.spine=true")
        if packet.get("provisional") is False:
            false_authority.append("committee_packet.provisional=false")
        if routes_asserted:
            false_authority.append("kernel_receipts.routes_called")
    if false_authority:
        rejected = True
        _record(checks, "authority_assertions", "fail", "asserted without an authority hash: " + ", ".join(false_authority))
    else:
        _record(checks, "authority_assertions", "pass", "no receipt-free spine assertion")

    contract = None
    contract_valid = False
    if stage in {"build", "export"}:
        try:
            contract = build_spec.load_contract(root)
            errors = build_spec.validate_contract(root, contract)
        except ValueError as exc:
            contract, errors = None, [str(exc)]
        if errors:
            rejected = True
            _record(checks, "build_contract", "fail", "; ".join(errors))
        else:
            contract_valid = True
            _record(checks, "build_contract", "pass", f"{contract.get('format')} spec {contract.get('spec_version')}")

        charter = _charter_path(root, entry, contract)
        if not charter or not os.path.isfile(charter):
            incomplete = True
            _record(checks, "preregistration", "missing", "governed charter is missing or outside project")
        else:
            embedded = prereg.embedded_hash(charter)
            expected = prereg.digest_for(charter)
            count = prereg.preregistration_header_count(charter)
            entry_hash = entry.get("charter_hash")
            if count != 1 or not embedded or embedded != expected or (entry_hash and entry_hash != embedded):
                rejected = True
                _record(checks, "preregistration", "fail", "charter hash/header does not verify")
            else:
                _record(checks, "preregistration", "pass", embedded)

        review_request = _read_json(os.path.join(root, build_spec.REVIEW_REQUEST_PATH))
        if not contract_valid:
            _record(checks, "semantic_review", "not_evaluated", "build contract is invalid")
        elif (contract or {}).get("semantic_review", {}).get("required"):
            targets = review_request.get("targets") if isinstance(review_request, dict) else None
            if not isinstance(targets, list) or not targets:
                rejected = True
                _record(checks, "semantic_review", "fail", "current tool-format review request with explicit targets is missing")
            else:
                review = build_spec.validate_semantic_review(
                    root,
                    targets,
                    contract,
                    require_independent=(stage == "export"),
                )
                if review.get("status") == "current_pass":
                    _record(checks, "semantic_review", "pass", review.get("assurance"))
                elif review.get("status") == "missing":
                    incomplete = True
                    _record(checks, "semantic_review", "missing", "; ".join(review.get("errors") or []))
                else:
                    rejected = True
                    _record(checks, "semantic_review", "fail", "; ".join(review.get("errors") or ["review blocked"]))
        else:
            _record(checks, "semantic_review", "not_required", "contract carries no forbidden constraints")

    old_key = os.environ.get("MVR_API_KEY")
    try:
        if keyfile:
            os.environ["MVR_API_KEY"] = _load_key(keyfile)
        authority_status, authority_detail = receipt_verifier.authorizing_receipt_status(root)
    except Exception as exc:
        authority_status, authority_detail = "no_key", f"key/ledger check unavailable ({type(exc).__name__})"
    finally:
        if old_key is None:
            os.environ.pop("MVR_API_KEY", None)
        else:
            os.environ["MVR_API_KEY"] = old_key

    if authority_status == "verified":
        _record(checks, "kernel_authority", "pass", authority_detail)
    elif authority_status == "unverified":
        rejected = True
        _record(checks, "kernel_authority", "fail", authority_detail)
    elif authority_status in {"no_key", "offline", "no_receipt"}:
        authority_inconclusive = True
        _record(checks, "kernel_authority", "inconclusive", authority_detail)
    else:
        incomplete = True
        _record(checks, "kernel_authority", "missing", authority_detail)

    if rejected:
        status = "rejected"
    elif incomplete:
        status = "incomplete"
    elif authority_inconclusive:
        status = "inconclusive"
    else:
        status = "verified"
    return {
        "status": status,
        "stage": stage,
        "checks": checks,
        "boundary": (
            "VERIFIED means live kernel authority and local artifact consistency. It does not "
            "cryptographically prove which host process authored every file."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Audit MVR Twin run evidence.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--keyfile")
    parser.add_argument("--stage", choices=("committee", "build", "export"), default="build")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit_run(args.root, args.keyfile, args.stage)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"TWIN RUN EVIDENCE {result['status'].upper()} ({result['stage']})")
        for item in result["checks"]:
            print(f"  [{item['status']}] {item['name']}: {item['detail']}")
        print("  boundary: " + result["boundary"])
    return EXIT_BY_STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
