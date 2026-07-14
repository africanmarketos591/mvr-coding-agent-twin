"""Bind a fitted charter to code without pretending syntax proves behavior.

This module has three deliberately separate jobs:

1. Freeze charter implementation constraints and kernel claim authorization.
2. Run a deterministic *naive-capability tripwire* over common code carriers.
3. Require a current host-model semantic review for behavioral assurance.

The tripwire catches obvious spellings only. A clear tripwire is not proof that a
forbidden behavior is absent; semantic program properties are not decidable in
general. Kernel authority remains limited to finite claim classes.

Usage:
  python scripts/twin_build_spec.py --root . --emit
  python scripts/twin_build_spec.py --root . --review-request src
  # Host model reads the request and writes mvr/semantic-review.json.
  python scripts/twin_build_spec.py --root . --check src --require-semantic-review
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import twin_claim_coverage as claim_coverage

SPEC_VERSION = "2.2"
CONTRACT_FORMAT = "mvr_build_contract_v2"
CONTRACT_PATH = os.path.join("mvr", "build_spec.json")
HISTORY_PATH = os.path.join("mvr", "build-contract-history.jsonl")
REVIEW_REQUEST_PATH = os.path.join("mvr", "semantic-review-request.json")
REVIEW_PATH = os.path.join("mvr", "semantic-review.json")
SECOND_REVIEW_PATH = os.path.join("mvr", "semantic-review-2.json")

# Semantic-review coverage is deliberately NOT a source-extension allowlist.
# Known opaque formats are denied by type and all other first-party files are
# classified by bytes. This keeps new languages and schema formats in scope.
OPAQUE_BINARY_EXTENSIONS = {
    ".7z", ".a", ".apk", ".avif", ".avi", ".avro", ".bmp", ".bz2",
    ".class", ".db", ".dll", ".dmg", ".doc", ".docx", ".dylib", ".eot",
    ".exe", ".feather", ".flac", ".gif", ".gz", ".heic", ".ico", ".iso",
    ".jar", ".jpeg", ".jpg", ".key", ".m4a", ".mkv", ".mov", ".mp3",
    ".mp4", ".numbers", ".o", ".obj", ".odp", ".ods", ".odt", ".ogg",
    ".orc", ".otf", ".pages", ".parquet", ".pdf", ".pickle", ".pkl",
    ".png", ".ppt", ".pptx", ".pyc", ".rar", ".so", ".sqlite",
    ".sqlite3", ".tar", ".tgz", ".tif", ".tiff", ".ttf", ".wav",
    ".wasm", ".war", ".webm", ".webp", ".woff", ".woff2", ".xls",
    ".xlsx", ".xz", ".zip",
}
TEXT_BOMS = (
    b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff",
)
SKIP_DIRS = {
    ".git", ".venv", "build", "dist", "mvr-coding-agent-twin", "mvr-twin",
    "node_modules", "__pycache__",
}
RESERVED_ROOT_FILES = {
    "charter.md", "mirror.md", "preflight.md", "operator_log.md",
    "scorer_sheet.md", "transcript.md", "transcript_report.md",
}
REVIEW_REQUEST_FORMAT = "mvr_semantic_review_request_v3"
REVIEW_FORMAT = "mvr_semantic_code_review_v3"
REVIEW_ATTESTATION = (
    "I reviewed every text file against every forbidden constraint; opaque files "
    "are hash-bound but outside semantic review."
)
PLACEHOLDER_REVIEW_IDENTITIES = {
    "auto", "automatic", "default", "host_model", "model", "n/a", "na", "none",
    "not-specified", "not_specified", "unknown", "unspecified",
}
NEGATED = re.compile(
    r"\b(no|not|never|without|non[- ]custodial|blocked|forbidden|disabled|"
    r"does not|do not|must not|cannot|can't|will not)\b",
    re.I,
)
CAPABILITY_PATTERNS = {
    "fund_custody": re.compile(
        r"\bcustod(?:y|ial)|hold(?:s|ing)?\s+(?:customer\s+|member\s+)?(?:money|funds)|"
        r"wallet balance|stored?[_ -]?value|member[_ -]?float|e[- ]?money\b",
        re.I,
    ),
    "deposit_taking": re.compile(
        r"\bdeposit[-_ ]taking|accept(?:s|ing)?\s+deposits?|savings account|interest[- ]bearing\b",
        re.I,
    ),
    "digital_lending": re.compile(
        r"\bdigital lending|loan[-_ ]?book|loan[-_ ]?api|approve[-_ ]?loan|issue[-_ ]?loan|"
        r"disburse[_ ]?advance|schedule[_ ]?repayment|credit (?:advance|financing|line)|"
        r"asset[- ]backed credit|bnpl|buy now pay later|"
        r"underwrit(?:e|es|ing)[^\n]{0,30}(?:loan|credit|advance)\b",
        re.I,
    ),
    "credit_scoring": re.compile(
        r"\bcredit[-_ ]?scor(?:e|es|ing)|savings[-_ ]?scor(?:e|es|ing)|creditworthiness|loan eligibility|"
        r"eligibility_for_loan|reliability[-_ ]?(?:score|index|rating|tier)|"
        r"trust[-_ ]?(?:score|index|rating|tier)|risk[-_ ]?(?:score|index|rating|tier)\b",
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

HIGH_RISK_CAPABILITIES = {
    "collective_investment", "credit_scoring", "deposit_taking", "digital_lending",
    "fund_custody", "payment_processing", "self_certification",
}

PLANNING_ONLY_STATUSES = {
    "abstain", "abstained", "internal_planning", "internal_planning_only",
    "permission_not_yet_earned", "provisional", "provisional_not_authorized",
    "prototype_only", "redirect", "redirected", "uncalibrated", "uncalibrated_lens_only",
}
PILOT_STATUSES = {"pilot", "pilot_only", "pilot_ready", "pilot_ready_with_review"}
BUILD_STATUSES = {"build_authorized", "authorized", "go"}


def read_text(path):
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
        if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
            return raw.decode("utf-32")
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            return raw.decode("utf-16")
        return raw.decode("utf-8-sig", errors="replace")
    except (OSError, UnicodeError):
        return ""


def read_json(path, fallback):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha256_file(path):
    if not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(raw)


def latest_entry(root):
    for name in ("decision-log.json", "decision-log.seed.json"):
        path = os.path.join(root, "mvr", name)
        data = read_json(path, None)
        if isinstance(data, list) and data and isinstance(data[-1], dict):
            return data[-1], path
        if isinstance(data, dict):
            return data, path
    return {}, None


def _inside(root, path):
    try:
        return os.path.commonpath([os.path.abspath(root), os.path.abspath(path)]) == os.path.abspath(root)
    except ValueError:
        return False


def discover_charter(root, explicit=None):
    root = os.path.abspath(root)
    if explicit:
        path = os.path.abspath(explicit)
        return (path, None) if _inside(root, path) and os.path.isfile(path) else (None, "explicit charter missing or outside project")
    entry, _ = latest_entry(root)
    ref = entry.get("charter_ref") if isinstance(entry, dict) else None
    if ref:
        path = os.path.abspath(os.path.join(root, str(ref)))
        if _inside(root, path) and os.path.isfile(path):
            return path, None
        return None, f"decision-log charter_ref is missing or outside project: {ref}"
    root_charter = os.path.join(root, "charter.md")
    if os.path.isfile(root_charter):
        return root_charter, None
    return None, "no charter_ref and no root charter.md"


def project_has_twin_case(root):
    return any(os.path.exists(os.path.join(root, path)) for path in (
        "charter.md", CONTRACT_PATH, os.path.join("mvr", "decision-log.json"),
        os.path.join("mvr", "decision-log.seed.json"),
    ))


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


def clean_markup(line):
    value = re.sub(r"^\s*[-*+]\s+", "", line).strip()
    value = re.sub(r"\*\*([^*]+):\*\*", r"\1:", value)
    return value.strip()


def _cut_value(value):
    match = re.search(
        r"(?:explicitly\s+)?not\s+building(?:\s*\([^)]*\))?\s*:\*{0,2}\s*(.+)",
        value,
        re.I,
    )
    return match.group(1).strip() if match else None


def charter_constraints(charter):
    build_lines = heading_section(charter, lambda heading: "the build" in heading)
    separate_cut = heading_section(
        charter,
        lambda heading: "explicitly not building" in heading or heading.startswith("not building"),
    )
    features = []
    cuts = []
    for raw in build_lines:
        value = clean_markup(raw)
        if not value:
            continue
        cut = _cut_value(value)
        lowered = value.lower()
        if cut:
            cuts.append(cut)
        elif "demo will not prove" in lowered or "demo does not prove" in lowered:
            continue
        elif lowered.startswith(("build:", "build this:")):
            features.append(value.split(":", 1)[-1].strip())
        elif re.match(r"^\s*[-*+]\s+", raw) and not lowered.startswith(("for:", "distributed through:")):
            features.append(value)
    for raw in separate_cut:
        value = clean_markup(raw)
        if value:
            cuts.append(_cut_value(value) or value)
    for raw in charter.splitlines():
        cut = _cut_value(clean_markup(raw))
        if cut:
            cuts.append(cut)
    return _dedupe(features), _dedupe(cuts)


def _dedupe(values):
    out = []
    seen = set()
    for value in values:
        key = re.sub(r"\s+", " ", str(value).strip()).lower()
        if key and key not in seen:
            seen.add(key)
            out.append(str(value).strip())
    return out


def capability_free_reason(charter):
    match = re.search(
        r"(?:code\s+)?capability\s+disposition:\*{0,2}\s*capability[-_ ]free\s*[-:]\s*(.+)",
        charter,
        re.I,
    )
    return match.group(1).strip() if match else None


def _status_rank(value):
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    if normalized in PLANNING_ONLY_STATUSES:
        return 0, normalized
    if normalized in PILOT_STATUSES:
        return 1, normalized
    if normalized in BUILD_STATUSES:
        return 2, normalized
    return None, normalized


def authorization_consistency(entry, packet, charter_status, charter_text=""):
    decision_rank, decision_status = _status_rank((entry or {}).get("verdict"))
    authorization = (entry or {}).get("decision_authorization") or {}
    authorized_use = {
        re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
        for value in authorization.get("authorized_use") or []
    }
    ceiling = decision_rank if decision_rank is not None else 0
    if authorized_use.intersection({"pilot", "pilot_execution", "bounded_pilot"}):
        ceiling = max(ceiling, 1)
    if authorized_use.intersection({"build_authorized", "production_build", "deployment"}):
        ceiling = max(ceiling, 2)
    if bool((packet or {}).get("provisional")):
        ceiling = -1
    charter_rank, normalized_charter = _status_rank(charter_status)
    errors = []
    if charter_rank is None:
        errors.append(f"charter status is missing or unsupported: {charter_status!r}")
    elif charter_rank > ceiling:
        errors.append(
            f"charter status {normalized_charter} exceeds decision ceiling "
            f"{decision_status or 'internal_planning_only'}"
        )
    legal_claim = re.search(
        r"\b(?:keeps?[^\n.]{0,45}legal|legally?\s+(?:operable|authorized|permitted|compliant)|"
        r"regulator[- ]approved|fully\s+compliant)\b",
        charter_text,
        re.I,
    )
    if ceiling <= 0 and legal_claim:
        errors.append("planning-only authority cannot support a legal-operation or compliance claim")
    return {
        "status": "pass" if not errors else "fail",
        "decision_status": decision_status or None,
        "charter_status": normalized_charter or None,
        "ceiling_rank": ceiling,
        "authorized_use": sorted(authorized_use),
        "errors": errors,
    }


def capabilities_in(text, honor_negation=False):
    if honor_negation and NEGATED.search(text):
        return {}
    return {
        name: match.group(0)
        for name, pattern in CAPABILITY_PATTERNS.items()
        for match in [pattern.search(text)]
        if match
    }


def constraint_record(reason, source="charter:explicit_cut_list"):
    normalized = re.sub(r"\s+", " ", reason.strip()).lower()
    return {
        "constraint_id": sha256_bytes(normalized.encode("utf-8"))[:16],
        "reason": reason[:600],
        "capabilities": sorted(capabilities_in(reason)),
        "source": source,
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


def contract_path(root):
    return os.path.join(os.path.abspath(root), CONTRACT_PATH)


def _git_head_contract(root):
    try:
        proc = subprocess.run(
            ["git", "-C", root, "show", f"HEAD:{CONTRACT_PATH.replace(os.sep, '/')}"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _history_contract(root):
    path = os.path.join(root, HISTORY_PATH)
    last = None
    try:
        with open(path, encoding="utf-8-sig") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    if isinstance(row, dict):
                        last = row.get("active_contract")
    except Exception:
        return None
    return last if isinstance(last, dict) else None


def prior_contract(root):
    current = read_json(contract_path(root), None)
    if isinstance(current, dict):
        return current
    history = _history_contract(root)
    if history:
        return history
    return _git_head_contract(root)


def _valid_constraint_override(entry, dropped_capabilities, dropped_constraints):
    override = entry.get("build_contract_override") if isinstance(entry, dict) else None
    if not isinstance(override, dict):
        return False, None
    identity_ok = all(str(override.get(key, "")).strip() for key in (
        "reviewer", "signature_ref", "note",
    )) and override.get("basis") == "named_human_override"
    allowed_caps = {str(value) for value in override.get("allow_removed_capabilities") or []}
    allowed_constraints = {str(value) for value in override.get("allow_removed_constraint_ids") or []}
    coverage_ok = set(dropped_capabilities).issubset(allowed_caps) and set(dropped_constraints).issubset(allowed_constraints)
    return identity_ok and coverage_ok, override


def _active_snapshot(contract):
    return {
        "forbidden_constraints": contract.get("forbidden_constraints") or [],
        "required_review_count": (contract.get("semantic_review") or {}).get("required_review_count", 1),
        "review_paths": (contract.get("semantic_review") or {}).get("review_paths", [REVIEW_PATH.replace("\\", "/")]),
        "forbidden_capabilities": contract.get("forbidden_capabilities") or [],
        "contract_level": contract.get("contract_level"),
        "verdict_status": contract.get("verdict_status"),
    }


def build_contract(root, charter_path=None, previous=None):
    root = os.path.abspath(root)
    charter_path, charter_error = discover_charter(root, charter_path)
    charter = read_text(charter_path) if charter_path else ""
    entry, decision_path = latest_entry(root)
    packet_path = os.path.join(root, "mvr", "committee_packet.json")
    packet = read_json(packet_path, {})
    if not isinstance(packet, dict):
        packet = {}
    claim_coverage_errors = claim_coverage.validate_packet(root, packet)
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
    constraints = [constraint_record(value) for value in cut_lines]
    capability_free = capability_free_reason(charter)
    status_match = re.search(r"\*\*Status:\*\*\s*([^|\n]+)", charter[:1600], re.I)
    verdict_status = status_match.group(1).strip().lower() if status_match else None
    authority_consistency = authorization_consistency(entry, packet, verdict_status, charter)

    previous = previous if isinstance(previous, dict) else None
    prior_constraints = {
        item.get("constraint_id"): item
        for item in (previous or {}).get("forbidden_constraints") or []
        if isinstance(item, dict) and item.get("constraint_id")
    }
    prior_capabilities = {
        item.get("capability"): item
        for item in (previous or {}).get("forbidden_capabilities") or []
        if isinstance(item, dict) and item.get("capability")
    }
    current_constraint_ids = {item["constraint_id"] for item in constraints}
    current_capabilities = {
        capability
        for item in constraints
        for capability in item.get("capabilities") or []
    }
    dropped_constraints = []
    for constraint_id, prior_item in prior_constraints.items():
        if constraint_id in current_constraint_ids:
            continue
        prior_item_capabilities = set(prior_item.get("capabilities") or [])
        if prior_item_capabilities and prior_item_capabilities.issubset(current_capabilities):
            continue
        dropped_constraints.append(constraint_id)
    dropped_constraints = sorted(dropped_constraints)
    dropped_capabilities = sorted(set(prior_capabilities) - current_capabilities)
    override_ok, override = _valid_constraint_override(entry, dropped_capabilities, dropped_constraints)
    weakening_blocked = bool(dropped_constraints or dropped_capabilities) and not override_ok
    if weakening_blocked:
        for constraint_id in dropped_constraints:
            inherited = dict(prior_constraints[constraint_id])
            inherited["source"] = "history:carried_forward_without_signed_override"
            constraints.append(inherited)
        current_constraint_ids = {item["constraint_id"] for item in constraints}
        current_capabilities = {
            capability
            for item in constraints
            for capability in item.get("capabilities") or []
        }

    forbidden = []
    for capability in sorted(current_capabilities):
        reasons = [item["reason"] for item in constraints if capability in item.get("capabilities", [])]
        forbidden.append({
            "capability": capability,
            "reason": reasons[0] if reasons else "carried from charter constraint history",
            "constraint_ids": [item["constraint_id"] for item in constraints if capability in item.get("capabilities", [])],
            "source": "charter_or_history",
        })

    redirect_like = verdict_status in {
        "redirect", "redirected", "abstain", "abstained", "provisional_not_authorized",
    }
    extraction_suspect = bool(redirect_like and not constraints and not capability_free)

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
    prereg = preregistration_state(charter_path) if charter_path else {
        "status": "not_verified", "reason": charter_error or "charter_missing"
    }
    provisional = bool(packet.get("provisional")) or not receipt_hashes
    if authority_consistency["status"] == "fail":
        contract_level = "authorization_contradiction"
    elif claim_coverage_errors:
        contract_level = "claim_coverage_incomplete"
    elif extraction_suspect:
        contract_level = "extraction_suspect"
    elif weakening_blocked:
        contract_level = "constraint_weakening_blocked"
    elif prereg.get("status") == "verified" and receipt_hashes and not provisional:
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
    brief_ref = (((packet.get("claim_coverage") or {}).get("brief_source") or {}).get("path"))
    if brief_ref:
        brief_path = os.path.abspath(os.path.join(root, str(brief_ref)))
        if _inside(root, brief_path) and os.path.isfile(brief_path):
            source_paths["user_brief"] = brief_path
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

    blocking_reasons = []
    if charter_error:
        blocking_reasons.append(charter_error)
    if extraction_suspect:
        blocking_reasons.append("redirect-like charter has no extracted cut-list and no explicit capability-free disposition")
    if weakening_blocked:
        blocking_reasons.append("previous constraints were removed without a complete named-human override")
    blocking_reasons.extend(authority_consistency["errors"])
    blocking_reasons.extend(claim_coverage_errors)

    high_risk = bool(current_capabilities.intersection(HIGH_RISK_CAPABILITIES))

    return {
        "format": CONTRACT_FORMAT,
        "spec_version": SPEC_VERSION,
        "contract_level": contract_level,
        "verdict_status": verdict_status,
        "blocking_reasons": blocking_reasons,
        "authorization_consistency": authority_consistency,
        "claim_coverage": {
            "status": "pass" if not claim_coverage_errors else "fail",
            "errors": claim_coverage_errors,
            "record": packet.get("claim_coverage") if isinstance(packet, dict) else None,
        },
        "extraction": {
            "status": "suspect" if extraction_suspect else "complete",
            "capability_free_reason": capability_free,
            "cut_line_count": len(cut_lines),
        },
        "authority": {
            "authorized_claim_classes": authorized_use,
            "not_authorized_claim_classes": not_authorized_use,
            "kernel_receipts_present": receipt_hashes,
            "receipt_verification": "not_performed_offline",
            "verify_command": "python scripts/verify_receipts.py --root . --online-strict",
            "boundary": "kernel authority covers finite claim classes, not semantic code behavior",
        },
        "charter_preregistration": prereg,
        "source_fingerprints": source_fingerprints,
        "build_features": features,
        "proposed_regulated_capabilities": proposed,
        "forbidden_constraints": constraints,
        "forbidden_capabilities": forbidden,
        "constraint_history": {
            "prior_contract_sha256": canonical_json_digest(_active_snapshot(previous)) if previous else None,
            "dropped_constraint_ids": dropped_constraints,
            "dropped_capabilities": dropped_capabilities,
            "named_human_override_valid": override_ok,
            "override": override if override_ok else None,
        },
        "required_instrumentation": required_instrumentation,
        "semantic_review": {
            "required": bool(constraints),
            "required_review_count": 2 if high_risk and constraints else (1 if constraints else 0),
            "request_path": REVIEW_REQUEST_PATH.replace("\\", "/"),
            "review_paths": [
                REVIEW_PATH.replace("\\", "/"),
                SECOND_REVIEW_PATH.replace("\\", "/"),
            ] if high_risk and constraints else [REVIEW_PATH.replace("\\", "/")],
            "coverage": "all_first_party_non_binary_text_by_content",
            "assurance": "reviewer_attested_not_deterministic_proof",
        },
        "agent_instruction": (
            "Implement only build_features. Treat forbidden_constraints as the fitted build cut-list. "
            "Run the deterministic tripwire, then obtain a fresh semantic review over every first-party "
            "text carrier. A clear tripwire alone is not semantic assurance; host self-review is not "
            "independent assurance."
        ),
    }


def _append_history(root, contract):
    path = os.path.join(root, HISTORY_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contract_sha256": canonical_json_digest(contract),
        "active_contract": _active_snapshot(contract),
    }
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def write_contract(root, charter_path=None):
    root = os.path.abspath(root)
    previous = prior_contract(root)
    contract = build_contract(root, charter_path, previous)
    output = contract_path(root)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(contract, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    _append_history(root, contract)
    return contract, output


def load_contract(root):
    data = read_json(contract_path(root), None)
    if not isinstance(data, dict):
        raise ValueError("mvr/build_spec.json is missing or unreadable")
    return data


def validate_contract(root, contract):
    errors = []
    if contract.get("format") != CONTRACT_FORMAT:
        errors.append("unsupported contract format")
    if contract.get("spec_version") != SPEC_VERSION:
        errors.append("contract version is stale")
    errors.extend(str(value) for value in contract.get("blocking_reasons") or [])
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
    return _dedupe(errors)


def review_file_kind(path):
    """Classify a file by bytes, using extensions only to deny known binary formats."""
    extension = os.path.splitext(os.path.basename(str(path)).lower())[1]
    if extension in OPAQUE_BINARY_EXTENSIONS:
        return "opaque", "known_binary_extension"
    if os.path.islink(path):
        return "opaque", "symbolic_link"
    try:
        with open(path, "rb") as handle:
            sample = handle.read(16384)
    except OSError:
        return "opaque", "unreadable"
    if not sample or sample.startswith(TEXT_BOMS):
        return "text", "content_text"
    if b"\x00" in sample:
        return "opaque", "binary_nul_bytes"
    try:
        sample.decode("utf-8")
        return "text", "content_text"
    except UnicodeDecodeError:
        control_count = sum(byte < 32 and byte not in {9, 10, 12, 13} for byte in sample)
        if control_count / len(sample) <= 0.02:
            return "text", "content_text_legacy_encoding"
        return "opaque", "binary_control_bytes"


def _relative_parts(root, path):
    full = os.path.abspath(path if os.path.isabs(path) else os.path.join(root, path))
    if not _inside(root, full):
        return full, None
    relative = os.path.relpath(full, root).replace("\\", "/")
    return full, [part.lower() for part in relative.split("/") if part]


def _reserved_product_path(root, path):
    _, parts = _relative_parts(root, path)
    if not parts:
        return True
    if parts[0] in {"mvr", "claims"} or any(part in {"mvr-coding-agent-twin", "mvr-twin"} for part in parts):
        return True
    if any(part in SKIP_DIRS for part in parts[:-1]):
        return True
    return len(parts) == 1 and parts[0] in RESERVED_ROOT_FILES


def is_code_path(path):
    """Backward-compatible name: true for any reviewable text carrier."""
    return os.path.isfile(path) and review_file_kind(path)[0] == "text"


def is_governed_code_path(path, root=None):
    """Return whether a first-party text file belongs in the build review scope."""
    root = os.path.abspath(root or os.getcwd())
    full = path if os.path.isabs(path) else os.path.join(root, path)
    return (
        os.path.isfile(full)
        and not _reserved_product_path(root, full)
        and review_file_kind(full)[0] == "text"
    )


def review_scope(root, targets):
    """Hash all first-party text and disclose opaque files under the exact targets."""
    root = os.path.abspath(root)
    text_files = []
    opaque_files = []
    excluded_paths = []
    seen = set()

    def add_file(candidate):
        full = os.path.abspath(candidate)
        if full in seen:
            return
        seen.add(full)
        if not _inside(root, full):
            raise ValueError(f"review target escapes project root: {candidate}")
        relative = os.path.relpath(full, root).replace("\\", "/")
        if _reserved_product_path(root, full):
            excluded_paths.append({"path": relative, "reason": "twin_or_generated_governance"})
            return
        kind, reason = review_file_kind(full)
        item = {"path": relative, "sha256": sha256_file(full)}
        if kind == "text":
            text_files.append(item)
        else:
            item["reason"] = reason
            opaque_files.append(item)

    for target in targets:
        path = os.path.abspath(target if os.path.isabs(target) else os.path.join(root, target))
        if not _inside(root, path):
            raise ValueError(f"review target escapes project root: {target}")
        if os.path.isfile(path):
            add_file(path)
            continue
        if not os.path.isdir(path):
            raise ValueError(f"review target does not exist: {target}")
        for base, dirs, files in os.walk(path, topdown=True):
            kept = []
            for name in sorted(dirs):
                candidate = os.path.join(base, name)
                if name.lower() in SKIP_DIRS or _reserved_product_path(root, candidate):
                    excluded_paths.append({
                        "path": os.path.relpath(candidate, root).replace("\\", "/"),
                        "reason": "dependency_generated_or_twin_directory",
                    })
                else:
                    kept.append(name)
            dirs[:] = kept
            for name in sorted(files):
                add_file(os.path.join(base, name))

    key = lambda item: (item["path"], item.get("reason", ""))
    return {
        "files": sorted(text_files, key=key),
        "opaque_files": sorted(opaque_files, key=key),
        "excluded_paths": sorted(excluded_paths, key=key),
    }


def iter_code_files(root, targets):
    """Yield every reviewable text carrier; retained for scanner API compatibility."""
    for item in review_scope(root, targets)["files"]:
        yield os.path.join(root, item["path"])


def scan_code(root, targets, contract):
    """Return obvious lexical hits. An empty result is *not* semantic assurance."""
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
            comment_only = stripped.startswith(("#", "//", "/*", "*", "<!--", "--"))
            for capability, signal in capabilities_in(line, honor_negation=comment_only).items():
                if capability in reasons:
                    findings.append({
                        "path": os.path.relpath(path, root).replace("\\", "/"),
                        "line": line_number,
                        "capability": capability,
                        "signal": signal,
                        "charter_reason": reasons[capability],
                        "assurance": "naive_lexical_tripwire",
                    })
    return findings


def code_manifest(root, targets):
    return review_scope(root, targets)["files"]


def normalize_review_targets(root, targets):
    root = os.path.abspath(root)
    normalized = []
    for target in targets:
        path = os.path.abspath(target if os.path.isabs(target) else os.path.join(root, target))
        if not _inside(root, path):
            raise ValueError(f"review target escapes project root: {target}")
        if not os.path.exists(path):
            raise ValueError(f"review target does not exist: {target}")
        relative = os.path.relpath(path, root).replace("\\", "/")
        normalized.append(relative)
    return sorted(set(normalized))


def review_request_digest(request):
    value = dict(request)
    value.pop("request_sha256", None)
    return canonical_json_digest(value)


def write_review_request(root, targets, contract=None):
    root = os.path.abspath(root)
    contract = contract or load_contract(root)
    errors = validate_contract(root, contract)
    if errors:
        raise ValueError("cannot request semantic review from invalid contract: " + "; ".join(errors))
    scope = review_scope(root, targets)
    request = {
        "format": REVIEW_REQUEST_FORMAT,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contract_sha256": canonical_json_digest(contract),
        "contract_level": contract.get("contract_level"),
        "targets": normalize_review_targets(root, targets),
        "required_review_count": int((contract.get("semantic_review") or {}).get("required_review_count", 1)),
        "review_paths": (contract.get("semantic_review") or {}).get("review_paths") or [
            REVIEW_PATH.replace("\\", "/")
        ],
        "forbidden_constraints": contract.get("forbidden_constraints") or [],
        "scope_policy": {
            "text_coverage": "all_first_party_non_binary_text_classified_by_content",
            "binary_policy": "known_or_detected_opaque_files_are_hash_bound_and_disclosed",
            "excluded_directory_names": sorted(SKIP_DIRS),
        },
        "files": scope["files"],
        "opaque_files": scope["opaque_files"],
        "excluded_paths": scope["excluded_paths"],
        "question": (
            "Attempt to falsify compliance before considering a pass. Read every listed text file and review it "
            "semantically, not by keyword. For every forbidden constraint, record at least one adversarial probe "
            "covering an alias, indirection, data flow, or decision-use path. Does any file implement, enable, "
            "or scaffold a forbidden constraint despite renaming, indirection, configuration, data flow, "
            "or another file type? Cite file and line for every finding. Explicitly acknowledge every "
            "opaque file; its bytes are bound for freshness but are not covered by text review."
        ),
        "review_schema": {
            "format": REVIEW_FORMAT,
            "request_sha256": "copy request_sha256 from this request",
            "reviewer_kind": "host_model | independent_model | human",
            "reviewer_id": "required stable reviewer or agent id; placeholders are invalid",
            "model_id": "actual model identifier required for model reviewers; auto/unknown placeholders are invalid",
            "reviewed_at": "ISO-8601",
            "verdict": "pass | block",
            "findings": [{
                "path": "relative path", "line": 1, "constraint_id": "id",
                "reason": "behavioral explanation",
            }],
            "adversarial_probes": [{
                "constraint_id": "one probe required for every forbidden constraint",
                "alias_or_data_flow": "what semantic evasion was inspected",
                "outcome": "not_found | finding:<path>:<line>",
            }],
            "opaque_file_acknowledgements": ["every path in request.opaque_files"],
            "attestation": REVIEW_ATTESTATION,
        },
        "assurance_boundary": (
            "This is reviewer-attested text-file coverage, not deterministic proof, binary analysis, "
            "or kernel authorization. Host-model self-review is not independent assurance."
        ),
    }
    request["request_sha256"] = review_request_digest(request)
    path = os.path.join(root, REVIEW_REQUEST_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(request, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return request, path


def _validate_review_document(review, request, expected_request_hash, require_independent):
    errors = []
    if review.get("format") != REVIEW_FORMAT:
        errors.append("semantic review format is invalid")
    if review.get("request_sha256") != expected_request_hash:
        errors.append("semantic review targets a different request")
    if review.get("reviewer_kind") not in {"host_model", "independent_model", "human"}:
        errors.append("semantic review reviewer_kind is invalid")
    if require_independent and review.get("reviewer_kind") == "host_model":
        errors.append("independent semantic review required; host_model self-review does not qualify")
    reviewer_id = str(review.get("reviewer_id", "")).strip()
    model_id = str(review.get("model_id", "")).strip()
    if not reviewer_id:
        errors.append("semantic review requires reviewer_id")
    elif reviewer_id.lower() in PLACEHOLDER_REVIEW_IDENTITIES:
        errors.append("semantic review reviewer_id must identify the actual reviewer, not a placeholder")
    if review.get("reviewer_kind") in {"host_model", "independent_model"}:
        if not model_id:
            errors.append("semantic model review requires model_id")
        elif model_id.lower() in PLACEHOLDER_REVIEW_IDENTITIES:
            errors.append("semantic review model_id must identify the actual model, not a placeholder")
    try:
        datetime.fromisoformat(str(review.get("reviewed_at", "")).replace("Z", "+00:00"))
    except Exception:
        errors.append("semantic review reviewed_at must be ISO-8601")
    if review.get("verdict") not in {"pass", "block"}:
        errors.append("semantic review verdict must be pass or block")
    expected_opaque = sorted(item["path"] for item in (request.get("opaque_files") or []))
    acknowledgements = review.get("opaque_file_acknowledgements")
    if not isinstance(acknowledgements, list) or sorted(acknowledgements) != expected_opaque:
        errors.append("semantic review must acknowledge every opaque file exactly")
    if review.get("attestation") != REVIEW_ATTESTATION:
        errors.append("semantic review attestation is missing or altered")
    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("semantic review findings must be a list")
    elif review.get("verdict") == "block" and not findings:
        errors.append("blocking semantic review requires at least one finding")
    probes = review.get("adversarial_probes")
    constraint_ids = {
        item.get("constraint_id")
        for item in request.get("forbidden_constraints") or []
        if isinstance(item, dict) and item.get("constraint_id")
    }
    probed_ids = {
        item.get("constraint_id")
        for item in probes or []
        if isinstance(item, dict) and item.get("alias_or_data_flow") and item.get("outcome")
    }
    if not isinstance(probes, list) or not constraint_ids.issubset(probed_ids):
        errors.append("semantic review requires an adversarial alias/data-flow probe for every constraint")
    return errors


def validate_semantic_review(
    root,
    targets,
    contract=None,
    require_independent=False,
    require_second=False,
):
    root = os.path.abspath(root)
    contract = contract or load_contract(root)
    if not (contract.get("semantic_review") or {}).get("required"):
        return {"status": "not_required", "errors": [], "verdict": "pass", "reviews": []}
    request = read_json(os.path.join(root, REVIEW_REQUEST_PATH), None)
    errors = []
    if not isinstance(request, dict):
        return {"status": "missing", "errors": ["semantic review request is missing"], "verdict": None, "reviews": []}
    if request.get("format") != REVIEW_REQUEST_FORMAT:
        errors.append("semantic review request format is invalid")
    expected_request_hash = review_request_digest(request)
    if request.get("request_sha256") != expected_request_hash:
        errors.append("semantic review request hash is invalid")
    if request.get("contract_sha256") != canonical_json_digest(contract):
        errors.append("semantic review request targets a different contract")
    try:
        normalized_targets = normalize_review_targets(root, targets)
    except ValueError as exc:
        normalized_targets = []
        errors.append(str(exc))
    if request.get("targets") != normalized_targets:
        errors.append("semantic review request targets do not match the checked paths")
    try:
        current_scope = review_scope(root, targets)
    except ValueError as exc:
        current_scope = {"files": [], "opaque_files": [], "excluded_paths": []}
        errors.append(str(exc))
    for field in ("files", "opaque_files", "excluded_paths"):
        if request.get(field) != current_scope[field]:
            errors.append(f"semantic review request is stale for current {field.replace('_', ' ')}")

    required_count = 1
    if require_second:
        required_count = max(1, int((contract.get("semantic_review") or {}).get("required_review_count", 1)))
    paths = [REVIEW_PATH] + ([SECOND_REVIEW_PATH] if required_count > 1 else [])
    reviews = []
    missing = []
    for path in paths:
        review = read_json(os.path.join(root, path), None)
        if not isinstance(review, dict):
            missing.append(path.replace("\\", "/"))
            continue
        review_errors = _validate_review_document(review, request, expected_request_hash, require_independent)
        errors.extend(f"{path.replace('\\', '/')}: {item}" for item in review_errors)
        reviews.append(review)
    if missing:
        return {
            "status": "invalid" if errors else "missing",
            "errors": errors + ["missing required semantic review(s): " + ", ".join(missing)],
            "verdict": None,
            "reviews": reviews,
        }
    reviewer_ids = [str(item.get("reviewer_id", "")).strip() for item in reviews]
    if len(reviewer_ids) > 1 and len(set(reviewer_ids)) != len(reviewer_ids):
        errors.append("high-risk second review must use a distinct reviewer_id")
    verdict = "block" if any(item.get("verdict") == "block" for item in reviews) else "pass"
    findings = [finding for item in reviews for finding in (item.get("findings") or [])]
    status = "invalid" if errors else ("current_block" if verdict == "block" else "current_pass")
    return {
        "status": status,
        "errors": errors,
        "verdict": verdict,
        "reviewer_kind": ",".join(str(item.get("reviewer_kind")) for item in reviews),
        "reviewer_id": ",".join(reviewer_ids),
        "model_id": ",".join(str(item.get("model_id") or "") for item in reviews),
        "findings": findings,
        "reviews": reviews,
        "assurance": "reviewer_attested_adversarial_review_not_deterministic_proof",
        "text_file_count": len(request.get("files") or []),
        "opaque_file_count": len(request.get("opaque_files") or []),
    }


def main():
    parser = argparse.ArgumentParser(description="Freeze MVR build constraints and run code tripwire/review checks.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", nargs="+", metavar="PATH")
    parser.add_argument("--review-request", nargs="+", metavar="PATH")
    parser.add_argument("--require-semantic-review", action="store_true")
    parser.add_argument(
        "--require-independent-review",
        action="store_true",
        help="reject host-model self-review; use for PRE-EXPORT and capability evaluation",
    )
    args = parser.parse_args()
    root = os.path.abspath(args.root)

    if args.emit or (not args.check and not args.review_request):
        contract, output = write_contract(root)
        print(f"MVR BUILD CONSTRAINT CONTRACT: wrote {output}")
        print(f"  level: {contract['contract_level']}")
        print(f"  cut-list constraints: {len(contract['forbidden_constraints'])}")
        print(f"  naive capability tripwires: {[item['capability'] for item in contract['forbidden_capabilities']]}")
        if contract.get("blocking_reasons"):
            print("MVR BUILD CONSTRAINT BLOCK: " + "; ".join(contract["blocking_reasons"]), file=sys.stderr)
            return 2

    if args.review_request:
        try:
            request, path = write_review_request(root, args.review_request)
        except (ValueError, OSError) as exc:
            print(f"MVR SEMANTIC REVIEW REQUEST BLOCK: {exc}", file=sys.stderr)
            return 2
        print(f"MVR SEMANTIC REVIEW REQUEST: wrote {path}")
        print(
            f"  text files: {len(request['files'])} | opaque files: {len(request['opaque_files'])} "
            f"| request_sha256: {request['request_sha256']}"
        )
        paths = ", ".join(request.get("review_paths") or [REVIEW_PATH.replace("\\", "/")])
        print(f"  Reviewers: attempt adversarial probes, then write {paths} as required.")

    if args.check:
        try:
            contract = load_contract(root)
        except ValueError as exc:
            print(f"MVR BUILD CONSTRAINT BLOCK: {exc}", file=sys.stderr)
            return 2
        errors = validate_contract(root, contract)
        if errors:
            print("MVR BUILD CONSTRAINT BLOCK: contract is stale, weakened, or malformed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            print("Regenerate with: python scripts/twin_build_spec.py --root . --emit", file=sys.stderr)
            return 2
        findings = scan_code(root, args.check, contract)
        if findings:
            print("MVR NAIVE-CAPABILITY TRIPWIRE HIT:", file=sys.stderr)
            for item in findings[:80]:
                print(
                    f"  {item['path']}:{item['line']} {item['capability']} via {item['signal']!r}\n"
                    f"    charter reason: {item['charter_reason']}",
                    file=sys.stderr,
                )
            return 1
        print(
            f"MVR NAIVE-CAPABILITY TRIPWIRE CLEAR: {len(list(iter_code_files(root, args.check)))} "
            "text carrier(s) checked. This is NOT semantic assurance."
        )
        if args.require_semantic_review or args.require_independent_review:
            review = validate_semantic_review(
                root,
                args.check,
                contract,
                require_independent=args.require_independent_review,
                require_second=args.require_independent_review,
            )
            if review["status"] != "current_pass":
                print("MVR SEMANTIC REVIEW BLOCK:", file=sys.stderr)
                for error in review.get("errors") or ["review verdict is block"]:
                    print(f"  - {error}", file=sys.stderr)
                for finding in review.get("findings") or []:
                    print(f"  - {finding}", file=sys.stderr)
                print(
                    "Run --review-request for the exact paths, then have the host model write "
                    "mvr/semantic-review.json.",
                    file=sys.stderr,
                )
                return 3
            print(
                f"MVR SEMANTIC REVIEW CURRENT: {review.get('reviewer_kind')} "
                f"{review.get('model_id') or ''}. {review.get('assurance')}."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
