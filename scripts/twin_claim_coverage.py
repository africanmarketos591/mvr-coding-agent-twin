"""Bind a committee run to the full user brief and its material capabilities.

This is a finite, conservative coverage check. It does not claim to understand
every product behavior. It makes one narrower guarantee: when a material
capability is recognizable in the preserved brief, that capability is sent to
strategy sparring and remains auditable in the committee packet.
"""
import hashlib
import os
import re


COVERAGE_FORMAT = "mvr_material_claim_coverage_v1"
MAX_SPARRING_CLAIMS = 10

MATERIAL_PATTERNS = {
    "fund_custody": re.compile(
        r"pooled?\s+(?:member\s+)?(?:money|funds?|contributions?)|"
        r"shared\s+(?:cooperative\s+)?fund|(?:keep|hold|pool|collect)[^\n.]{0,45}"
        r"(?:member\s+)?(?:money|funds?|contributions?)|"
        r"(?:farmer|member|customer)[-_ ]?balance|wallet\s+balance",
        re.I,
    ),
    "deposit_taking": re.compile(
        r"deposit[-_ ]taking|accept(?:s|ing)?\s+deposits?|savings\s+account|"
        r"interest[- ]bearing",
        re.I,
    ),
    "digital_lending": re.compile(
        r"input\s+credit|credit\s+(?:advance|financing|line)|loan|borrow|"
        r"receive\s+inputs?[^\n.]{0,70}(?:before|without)[^\n.]{0,50}contribution|"
        r"outstanding\s+(?:amount|balance)[^\n.]{0,70}(?:harvest|repay|recover)|"
        r"recover[^\n.]{0,60}(?:harvest|future\s+sale)",
        re.I,
    ),
    "credit_scoring": re.compile(
        r"(?:farmer|member|borrower)?[-_ ]?(?:reliability|trust|risk|savings|credit)"
        r"[-_ ]?(?:score|index|rating|tier|status)|creditworthiness|"
        r"considered\s+reliable",
        re.I,
    ),
    "payment_processing": re.compile(
        r"mobile[- ]money[^\n.]{0,50}(?:collect|pay|payout|integration|api|placeholder)|"
        r"(?:collect|pay|payout)[^\n.]{0,45}(?:mobile[- ]money|momo|airtel)|"
        r"payment\s+(?:processing|escrow)|escrow\s+wallet|stk\s+push",
        re.I,
    ),
    "repayment_recovery": re.compile(
        r"repayment\s+track|recover(?:y|ed|ing)?[^\n.]{0,55}(?:harvest|sale|proceeds)|"
        r"harvest[-_ ]?(?:payment|sale)[^\n.]{0,55}(?:deduct|reconcil|recover)",
        re.I,
    ),
    "role_based_access": re.compile(
        r"login\s+roles?|role[-_ ]based\s+access|(?:manager|officer|farmer)[^\n.]{0,45}"
        r"(?:login|role|portal|permission)",
        re.I,
    ),
    "personal_financial_records": re.compile(
        r"member\s+profiles?|farmer\s+profiles?|phone\s+numbers?|national\s+id|"
        r"transaction\s+history|debt\s+records?|financial\s+records?",
        re.I,
    ),
    "self_certification": re.compile(
        r"self[- ]certif|certif(?:y|ies|ication)[^\n.]{0,35}"
        r"(?:supplier|clinic|product|facility|compliance)",
        re.I,
    ),
    "collective_investment": re.compile(
        r"collective\s+investment|unit\s+trust|money[- ]market\s+fund|"
        r"invest(?:s|ing)?\s+pooled|portfolio\s+management",
        re.I,
    ),
}


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _dedupe(values):
    output = []
    seen = set()
    for value in values:
        key = re.sub(r"\s+", " ", str(value).strip()).lower()
        if key and key not in seen:
            seen.add(key)
            output.append(str(value).strip())
    return output


def material_claims(text):
    output = []
    for capability, pattern in MATERIAL_PATTERNS.items():
        match = pattern.search(text or "")
        if not match:
            continue
        start = max(0, match.start() - 55)
        end = min(len(text), match.end() + 85)
        excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
        output.append({
            "capability": capability,
            "signal": match.group(0),
            "claim": f"material capability {capability}: {excerpt}",
        })
    return output


def build_coverage(brief_text, source, supplied_claims, subject):
    derived = material_claims(brief_text)
    claims = _dedupe(list(supplied_claims or []) + [item["claim"] for item in derived])
    if not claims:
        claims = [subject]
    source_kind = (source or {}).get("kind")
    if source_kind != "file":
        status = "unverified_source"
    elif len(claims) > MAX_SPARRING_CLAIMS:
        status = "claim_overflow"
    else:
        status = "complete"
    return claims[:MAX_SPARRING_CLAIMS], {
        "format": COVERAGE_FORMAT,
        "status": status,
        "brief_source": source,
        "brief_sha256": sha256_text(brief_text),
        "material_capabilities": derived,
        "supplied_claim_count": len(supplied_claims or []),
        "claims_required": len(claims),
        "claims_sent": claims[:MAX_SPARRING_CLAIMS],
        "overflow_count": max(0, len(claims) - MAX_SPARRING_CLAIMS),
        "boundary": (
            "Finite recognizable-capability coverage, not proof that every semantic product claim was found. "
            "Audit-ready export requires a preserved brief file."
        ),
    }


def validate_packet(root, packet):
    coverage = packet.get("claim_coverage") if isinstance(packet, dict) else None
    errors = []
    if not isinstance(coverage, dict) or coverage.get("format") != COVERAGE_FORMAT:
        return ["material claim coverage record is missing or unsupported"]
    source = coverage.get("brief_source") or {}
    if source.get("kind") != "file" or not source.get("path"):
        errors.append("full user brief is not preserved as a hash-bound project file")
        return errors
    path = os.path.abspath(os.path.join(root, str(source["path"])))
    try:
        inside = os.path.commonpath([os.path.abspath(root), path]) == os.path.abspath(root)
    except ValueError:
        inside = False
    if not inside or not os.path.isfile(path):
        errors.append("preserved user brief is missing or outside the project")
        return errors
    with open(path, encoding="utf-8-sig") as handle:
        brief_text = handle.read()
    if sha256_text(brief_text) != coverage.get("brief_sha256"):
        errors.append("preserved user brief changed after committee execution")
    expected = {item["capability"] for item in material_claims(brief_text)}
    recorded = {
        item.get("capability")
        for item in coverage.get("material_capabilities") or []
        if isinstance(item, dict)
    }
    if expected != recorded:
        errors.append("material capability inventory does not match the preserved brief")
    packet_claims = packet.get("claims_sent") or []
    if packet_claims != coverage.get("claims_sent"):
        errors.append("strategy-sparring claims do not match the coverage record")
    if coverage.get("status") != "complete" or coverage.get("overflow_count"):
        errors.append(f"material claim coverage is {coverage.get('status')}")
    return errors
