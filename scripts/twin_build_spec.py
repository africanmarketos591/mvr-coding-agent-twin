"""Compile a frozen MVR charter into an enforceable code-generation contract.

The kernel authorizes claim classes. The charter records the fitted build and its
explicit cut list. This tool binds both layers into ``mvr/build_spec.json`` and
fingerprints every governed input so an old contract cannot survive a changed
charter or decision log.

Usage:
  python scripts/twin_build_spec.py --root . --emit
  python scripts/twin_build_spec.py --root . --check src

The checker is deliberately offline. Receipt authenticity remains the job of
``verify_receipts.py``; this contract reports receipt presence without upgrading
it to live verification.
"""
import argparse
import hashlib
import json
import os
import re
import sys


SPEC_VERSION = "1.1"
CONTRACT_PATH = os.path.join("mvr", "build_spec.json")
CODE_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".html", ".java", ".js", ".jsx",
    ".kt", ".php", ".py", ".rb", ".rs", ".svelte", ".swift", ".ts",
    ".tsx", ".vue",
}
SKIP_DIRS = {
    ".git", ".venv", "build", "dist", "mvr-coding-agent-twin", "mvr-twin",
    "node_modules", "__pycache__",
}
NEGATED = re.compile(
    r"\b(no|not|never|without|non[- ]custodial|blocked|forbidden|disabled|"
    r"does not|do not|must not|cannot|can't|will not)\b",
    re.I,
)
CAPABILITY_PATTERNS = {
    "fund_custody": re.compile(
        r"\bcustod(?:y|ial)|hold(?:s|ing)?\s+(?:customer\s+|member\s+)?(?:money|funds)|"
        r"wallet balance|store[- ]of[- ]value|e[- ]?money\b",
        re.I,
    ),
    "deposit_taking": re.compile(
        r"\bdeposit[-_ ]taking|accept(?:s|ing)?\s+deposits?|savings account|interest[- ]bearing\b",
        re.I,
    ),
    "digital_lending": re.compile(
        r"\bdigital lending|loan book|loan api|approve[_ ]?loan|issue[_ ]?loan|"
        r"credit (?:advance|financing|line)|asset[- ]backed credit|bnpl|buy now pay later|"
        r"underwrit(?:e|es|ing)[^\n]{0,30}(?:loan|credit|advance)\b",
        re.I,
    ),
    "credit_scoring": re.compile(
        r"\bcredit[-_ ]?scor(?:e|es|ing)|creditworthiness|loan eligibility|"
        r"eligibility_for_loan\b",
        re.I,
    ),
    "payment_processing": re.compile(
        r"\bprocess(?:es|ing)? payments?|payment processing|payment escrow|escrow wallet|"
        r"mobile money (?:integration|api|callback|collection|payment flow)|stk push\b",
        re.I,
    ),
    "self_certification": re.compile(
        r"\bself[- ]certif|issue(?:s|ing)? (?:a )?(?:licen[cs]e|certificate)|"
        r"certif(?:y|ies|ication)[^\n]{0,30}(?:supplier|clinic|product|facility)\b",
        re.I,
    ),
    "collective_investment": re.compile(
        r"\bcollective investment|unit trust|money[- ]market fund|invest(?:s|ing)? pooled|"
        r"portfolio management|invest the fund\b",
        re.I,
    ),
}


def read_text(path):
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def read_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def sha256_file(path):
    if not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_entry(root):
    for name in ("decision-log.json", "decision-log.seed.json"):
        path = os.path.join(root, "mvr", name)
        data = read_json(path, None)
        if isinstance(data, list) and data and isinstance(data[-1], dict):
            return data[-1], path
        if isinstance(data, dict):
            return data, path
    return {}, None


def heading_section(text, predicate):
    lines = text.splitlines()
    start = None
    level = None
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if match and predicate(match.group(2).strip().lower()):
            start = index + 1
            level = len(match.group(1))
            break
    if start is None:
        return []
    out = []
    for line in lines[start:]:
        match = re.match(r"^(#{1,6})\s+", line.strip())
        if match and len(match.group(1)) <= level:
            break
        out.append(line)
    return out


def clean_bullet(line):
    value = re.sub(r"^\s*[-*+]\s+", "", line).strip()
    value = re.sub(r"\*\*([^*]+):\*\*", r"\1:", value)
    return value.strip()


def charter_constraints(charter):
    build_lines = heading_section(charter, lambda h: "the build" in h)
    separate_cut = heading_section(
        charter,
        lambda h: "explicitly not building" in h or h.startswith("not building"),
    )
    features = []
    cut_lines = []
    for raw in build_lines:
        if not re.match(r"^\s*[-*+]\s+", raw):
            continue
        value = clean_bullet(raw)
        lowered = value.lower()
        if lowered.startswith("explicitly not building"):
            cut_lines.append(value.split(":", 1)[-1].strip())
        elif "demo will not prove" in lowered or "demo does not prove" in lowered:
            continue
        elif lowered.startswith(("build:", "build this:")):
            features.append(value.split(":", 1)[-1].strip())
        elif lowered.startswith(("for:", "distributed through:")):
            continue
        elif value:
            features.append(value)
    for raw in separate_cut:
        if re.match(r"^\s*[-*+]\s+", raw):
            cut_lines.append(clean_bullet(raw))
    return [item for item in features if item], [item for item in cut_lines if item]


def capabilities_in(text, honor_negation=False):
    if honor_negation and NEGATED.search(text):
        return {}
    return {
        name: match.group(0)
        for name, pattern in CAPABILITY_PATTERNS.items()
        for match in [pattern.search(text)]
        if match
    }


def preregistration_state(charter_path):
    text = read_text(charter_path)
    matches = re.findall(r"\*\*Preregistration hash:\*\*\s*([0-9a-fA-F]{64})", text)
    if len(matches) != 1:
        return {"status": "not_verified", "reason": "exactly_one_embedded_hash_required"}
    try:
        from preregister import digest_for
        expected = digest_for(charter_path)
    except Exception as exc:
        return {"status": "not_verified", "reason": f"hash_check_failed:{type(exc).__name__}"}
    actual = matches[0].lower()
    return {
        "status": "verified" if actual == expected else "mismatch",
        "embedded_hash": actual,
        "computed_hash": expected,
    }


def build_contract(root, charter_path=None):
    root = os.path.abspath(root)
    charter_path = os.path.abspath(charter_path or os.path.join(root, "charter.md"))
    charter = read_text(charter_path)
    entry, decision_path = latest_entry(root)
    packet_path = os.path.join(root, "mvr", "committee_packet.json")
    packet = read_json(packet_path, {})
    if not isinstance(packet, dict):
        packet = {}
    authorization = entry.get("decision_authorization") or {}
    if not isinstance(authorization, dict):
        authorization = {}
    authorized_use = authorization.get("authorized_use") or ["internal_planning"]
    not_authorized_use = authorization.get("not_authorized_use") or []
    if not isinstance(authorized_use, list):
        authorized_use = ["internal_planning"]
    if not isinstance(not_authorized_use, list):
        not_authorized_use = []

    features, cut_lines = charter_constraints(charter)
    forbidden = []
    seen = set()
    for line in cut_lines:
        for capability, signal in capabilities_in(line).items():
            if capability in seen:
                continue
            seen.add(capability)
            forbidden.append({
                "capability": capability,
                "reason": line[:400],
                "matched_signal": signal,
                "source": "charter:explicit_cut_list",
            })

    claims_sent = packet.get("claims_sent") or []
    proposed = []
    for claim in claims_sent if isinstance(claims_sent, list) else []:
        for capability in capabilities_in(str(claim)):
            if capability not in proposed:
                proposed.append(capability)

    receipt_map = entry.get("kernel_receipts") or packet.get("kernel_receipts") or {}
    if not isinstance(receipt_map, dict):
        receipt_map = {}
    receipt_hashes = {
        str(key): str(value)
        for key, value in receipt_map.items()
        if re.fullmatch(r"[0-9a-fA-F]{64}", str(value))
    }
    prereg = preregistration_state(charter_path) if os.path.exists(charter_path) else {
        "status": "not_verified", "reason": "charter_missing"
    }
    provisional = bool(packet.get("provisional")) or not receipt_hashes
    if prereg.get("status") == "verified" and receipt_hashes and not provisional:
        contract_level = "frozen_charter_kernel_receipted"
    elif receipt_hashes and not provisional:
        contract_level = "draft_charter_kernel_receipted"
    else:
        contract_level = "provisional_default_deny"

    source_paths = {
        "charter": charter_path,
        "decision_log": decision_path,
        "committee_packet": packet_path if os.path.exists(packet_path) else None,
    }
    source_fingerprints = {
        name: {"path": os.path.relpath(path, root).replace("\\", "/"), "sha256": sha256_file(path)}
        for name, path in source_paths.items()
        if path
    }
    evidence_bill = packet.get("evidence_bill") or []
    required_instrumentation = []
    if isinstance(evidence_bill, list):
        for lane in evidence_bill:
            if isinstance(lane, dict) and lane.get("stakeholder_class"):
                required_instrumentation.append({
                    "capture_for": lane.get("stakeholder_class"),
                    "minimum_signal_count": lane.get("minimum_signal_count"),
                    "required_fields": lane.get("required_fields") or [],
                })

    status_match = re.search(r"\*\*Status:\*\*\s*([^|\n]+)", charter[:1200], re.I)
    return {
        "format": "mvr_build_contract_v1",
        "spec_version": SPEC_VERSION,
        "contract_level": contract_level,
        "verdict_status": status_match.group(1).strip() if status_match else None,
        "authority": {
            "authorized_claim_classes": authorized_use,
            "not_authorized_claim_classes": not_authorized_use,
            "kernel_receipts_present": receipt_hashes,
            "receipt_verification": "not_performed_offline",
            "verify_command": "python scripts/verify_receipts.py --root . --online-strict",
        },
        "charter_preregistration": prereg,
        "source_fingerprints": source_fingerprints,
        "build_features": features,
        "proposed_regulated_capabilities": proposed,
        "forbidden_capabilities": forbidden,
        "required_instrumentation": required_instrumentation,
        "agent_instruction": (
            "Implement only build_features. Do not implement forbidden_capabilities. "
            "Do not convert authorized claim classes into product-capability permission. "
            "Run twin_build_spec.py --check before commit and export."
        ),
    }


def contract_path(root):
    return os.path.join(os.path.abspath(root), CONTRACT_PATH)


def write_contract(root, charter_path=None):
    contract = build_contract(root, charter_path)
    output = contract_path(root)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(contract, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return contract, output


def load_contract(root):
    data = read_json(contract_path(root), None)
    if not isinstance(data, dict):
        raise ValueError("mvr/build_spec.json is missing or unreadable")
    return data


def validate_contract(root, contract):
    errors = []
    if contract.get("format") != "mvr_build_contract_v1":
        errors.append("unsupported contract format")
    if contract.get("spec_version") != SPEC_VERSION:
        errors.append("contract version is stale")
    fingerprints = contract.get("source_fingerprints") or {}
    if not fingerprints:
        errors.append("source fingerprints are missing")
    for name, item in fingerprints.items():
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            errors.append(f"{name} fingerprint is malformed")
            continue
        path = os.path.join(root, item["path"])
        current = sha256_file(path)
        if current != item["sha256"]:
            errors.append(f"{name} changed after build contract emission")
    return errors


def is_code_path(path):
    return os.path.splitext(str(path))[1].lower() in CODE_EXTENSIONS


def is_governed_code_path(path):
    normalized = str(path).replace("\\", "/")
    parts = {part.lower() for part in normalized.split("/")}
    return is_code_path(normalized) and not parts.intersection({"mvr-coding-agent-twin", "mvr-twin"})


def iter_code_files(root, targets):
    seen = set()
    for target in targets:
        path = target if os.path.isabs(target) else os.path.join(root, target)
        if os.path.isfile(path) and is_governed_code_path(path):
            key = os.path.abspath(path)
            if key not in seen:
                seen.add(key)
                yield key
        elif os.path.isdir(path):
            for base, dirs, files in os.walk(path):
                dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
                for name in files:
                    candidate = os.path.join(base, name)
                    if is_governed_code_path(candidate):
                        key = os.path.abspath(candidate)
                        if key not in seen:
                            seen.add(key)
                            yield key


def scan_code(root, targets, contract):
    reasons = {
        item.get("capability"): item.get("reason")
        for item in contract.get("forbidden_capabilities") or []
        if isinstance(item, dict) and item.get("capability")
    }
    findings = []
    if not reasons:
        return findings
    for path in iter_code_files(root, targets):
        text = read_text(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            comment_only = stripped.startswith(("#", "//", "/*", "*", "<!--"))
            line_capabilities = capabilities_in(
                line,
                honor_negation=comment_only,
            )
            for capability, signal in line_capabilities.items():
                if capability in reasons:
                    findings.append({
                        "path": os.path.relpath(path, root).replace("\\", "/"),
                        "line": line_number,
                        "capability": capability,
                        "signal": signal,
                        "charter_reason": reasons[capability],
                    })
    return findings


def main():
    parser = argparse.ArgumentParser(description="Bind MVR authority and charter constraints into code generation.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", nargs="+", metavar="PATH")
    args = parser.parse_args()
    root = os.path.abspath(args.root)

    if args.emit or not args.check:
        contract, output = write_contract(root)
        print(f"MVR BUILD CONTRACT: wrote {output}")
        print(f"  level: {contract['contract_level']}")
        print(f"  build features: {len(contract['build_features'])}")
        print(f"  forbidden capabilities: {[item['capability'] for item in contract['forbidden_capabilities']]}")

    if args.check:
        try:
            contract = load_contract(root)
        except ValueError as exc:
            print(f"MVR BUILD CONTRACT BLOCK: {exc}", file=sys.stderr)
            return 2
        errors = validate_contract(root, contract)
        if errors:
            print("MVR BUILD CONTRACT BLOCK: contract is stale or malformed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            print("Regenerate with: python scripts/twin_build_spec.py --root . --emit", file=sys.stderr)
            return 2
        findings = scan_code(root, args.check, contract)
        if findings:
            print("MVR BUILD CONTRACT BLOCK: redirected-away capability found in code:", file=sys.stderr)
            for item in findings[:80]:
                print(
                    f"  {item['path']}:{item['line']} {item['capability']} via {item['signal']!r}\n"
                    f"    charter reason: {item['charter_reason']}",
                    file=sys.stderr,
                )
            return 1
        print(f"MVR BUILD CONTRACT PASS: {len(list(iter_code_files(root, args.check)))} code file(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
