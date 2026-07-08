"""Scan shippable surfaces for fabricated-as-real credentials and regulated features.

The claim gate governs claim artifacts. The source ledger governs the charter.
But a polished demo can still present an invented clinic, licence number, or
fee as real inside UI strings, product plans, and go-to-market notes.

This scanner is a PRE-EXPORT / CI guard. It flags unhedged credentials, named
licensed partners, hard fee/capital figures, and unhedged regulated product
capabilities that are not backed by a current-format source ledger or local
Twin authorization.

Exit codes:
  0 clean
  1 fabricated-as-real claims found
"""
import argparse
import json
import os
import re
import sys


ROOT_DOC_TARGETS = ["PRODUCT_PLAN.md", "GO_TO_MARKET.md", "SUMMARY.md", "README.md"]
COMMON_DIR_TARGETS = ["scaffold", "app", "apps", "src", "web", "frontend", "backend", "client", "server", "product"]
SCAN_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".html", ".md", ".py", ".txt", ".json", ".vue", ".svelte"}
SKIP_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "__pycache__",
    "mvr-coding-agent-twin",
    "mvr-twin",
    "mvr",
    "charters",
    "claims",
    "rehearsals",
}
LEDGER_FORMAT = "mvr_public_research_pack_v1"

HEDGE = re.compile(
    r"\b(e\.?g\.?|mock|demo|sample|placeholder|dummy|fake|hypothetical|illustrat|"
    r"for demonstration|example|todo|unknown|not real|fictional|sandbox|test data)\b",
    re.I,
)
CREDENTIAL = re.compile(r"#?\b[A-Z]{1,4}(?:[-/][A-Z]{1,4})?[-/]\d{3,7}\b")
BARE_CREDENTIAL = re.compile(
    r"\b(?:licen[cs]e|registration|permit|reg)\b[^\n]{0,16}?(?:no\.?|number|#|:)\s*#?[A-Z]{1,4}(?:[-/][A-Z]{1,4})?[-/]\d{3,7}\b",
    re.I,
)
REGULATED_CONTEXT = re.compile(
    r"KMPDC|PPB|IRA|ODPC|SHA|CBK|BoU|UMRA|licen[cs]e|registration|\breg\b|permit|"
    r"underwrit|policy\s*id|regulat|certif",
    re.I,
)
PARTNER = re.compile(
    r"(?:underwritten by|registered (?:clinic|partner|pharmacy)|licensed by|partnered with|"
    r"partner\s*[:=]|clinical partner)\s+([A-Z][A-Za-z&'. ]{2,48}?)(?=[\.,\(\)<\"\n]|$)",
    re.I,
)
FIGURE = re.compile(
    r"(?:KES|Ksh|UGX|USD|\$)\s?[\d,]+(?:\.\d+)?\s?(?:k|m|bn|million|billion)?"
    r"(?:[^\n]{0,45}?(?:fee|capital|licen[cs]e|cap|premium|minimum|cover|sum insured))?",
    re.I,
)
FIGURE_CONTEXT = re.compile(r"fee|capital|licen[cs]e|\bcap\b|minimum|premium|cover|sum insured", re.I)
CAPABILITY_NEGATION = re.compile(
    r"\b(no|not|without|exclude[ds]?|does not|do not|never|avoid|blocked|unauthori[sz]ed|"
    r"requires|required|need(?:s|ed)?|will need|licen[cs]e|regulat|only after|path back in|explicitly not)\b",
    re.I,
)
REGULATED_CAPABILITIES = [
    (
        "credit_scoring",
        re.compile(r"\bcredit[-_\s]?scor(?:e|ing)|eligibility_for_loan|loan eligibility\b", re.I),
    ),
    (
        "mobile_money_integration",
        re.compile(
            r"\bmobile money (?:integration|api|callback|endpoint|collection|payment flow)|"
            r"/api/mobile-money|(?:mtn|airtel)[^\n]{0,40}money[^\n]{0,40}callback|stk push",
            re.I,
        ),
    ),
    (
        "payment_custody",
        re.compile(r"\bescrow wallet|payment escrow|hold(?:s|ing)?[^\n]{0,20}(?:money|funds)|custody of funds\b", re.I),
    ),
    (
        "digital_lending",
        re.compile(r"\bloan api|small loans|digital lending|underwrit(?:e|ing)[^\n]{0,40}loan|asset[- ]backed credit|credit financing\b", re.I),
    ),
]


def normalize_code(value):
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def normalize_words(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def number_value(text):
    match = re.search(r"[\d,]+(?:\.\d+)?", text)
    if not match:
        return None
    raw = match.group(0).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    suffix = text[match.end(): match.end() + 12].lower()
    if re.match(r"\s*(bn|billion)", suffix):
        value *= 1_000_000_000
    elif re.match(r"\s*(m|million)", suffix):
        value *= 1_000_000
    elif re.match(r"\s*k", suffix):
        value *= 1_000
    return int(value) if value.is_integer() else value


def read_ledger(path):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except Exception:
        data = {}
    if data.get("format") != LEDGER_FORMAT:
        data = {}

    blobs = []
    codes = set()
    numbers = set()
    names = set()
    for entry in data.get("entries", []) or []:
        if str(entry.get("status", "")).lower() != "verified":
            continue
        blob = " ".join(str(entry.get(key, "")) for key in ("claim", "source_name", "url", "notes"))
        blobs.append(normalize_words(blob))
        for code in CREDENTIAL.findall(blob):
            codes.add(normalize_code(code))
        for figure in FIGURE.findall(blob):
            value = number_value(figure)
            if value is not None:
                numbers.add(value)
        for number in re.findall(r"[\d,]+(?:\.\d+)?\s?(?:k|m|bn|million|billion)?", blob, re.I):
            value = number_value(number)
            if value is not None:
                numbers.add(value)
        source_name = str(entry.get("source_name", "")).strip()
        claim = str(entry.get("claim", "")).strip()
        for phrase in (source_name, claim):
            for word in re.findall(r"[A-Za-z][A-Za-z&'.-]{2,}", phrase):
                names.add(normalize_words(word))
    return {"blobs": blobs, "codes": codes, "numbers": numbers, "names": names}


def read_authorized(root):
    state_path = os.path.join(root, "mvr", "state.json")
    try:
        with open(state_path, encoding="utf-8-sig") as handle:
            state = json.load(handle)
    except Exception:
        state = {}
    authorized = state.get("authorized_use") or []
    if not isinstance(authorized, list):
        return set()
    return {str(item).strip().lower() for item in authorized if str(item).strip()}


def is_verified_name(name, verified):
    normalized = normalize_words(name)
    if not normalized:
        return False
    if any(normalized in blob for blob in verified["blobs"]):
        return True
    first = normalized.split()[0]
    return first in verified["names"]


def is_verified_figure(fragment, verified):
    value = number_value(fragment)
    return value is not None and value in verified["numbers"]


def iter_files(root, targets):
    for target in targets:
        path = os.path.join(root, target)
        if os.path.isdir(path):
            for base, dirs, files in os.walk(path):
                dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
                for filename in files:
                    if os.path.splitext(filename)[1].lower() in SCAN_EXTENSIONS:
                        yield os.path.join(base, filename)
        elif os.path.isfile(path):
            yield path


def discover_default_targets(root):
    targets = []
    seen = set()

    def add(target):
        normalized = target.replace("\\", "/")
        if normalized not in seen and os.path.exists(os.path.join(root, target)):
            seen.add(normalized)
            targets.append(target)

    for target in ROOT_DOC_TARGETS + COMMON_DIR_TARGETS:
        add(target)
    try:
        for name in os.listdir(root):
            path = os.path.join(root, name)
            lowered = name.lower()
            if not os.path.isdir(path) or lowered in SKIP_DIRS:
                continue
            if lowered.endswith(("-app", "_app")):
                add(name)
    except OSError:
        pass
    return targets


def scan_line(line, verified, authorized):
    findings = []
    if HEDGE.search(line):
        return findings

    credential = CREDENTIAL.search(line) or BARE_CREDENTIAL.search(line)
    if credential and REGULATED_CONTEXT.search(line):
        code = normalize_code(credential.group(0))
        if code not in verified["codes"]:
            findings.append((
                "credential",
                credential.group(0).strip(),
                "specific licence/registration/policy number presented as real",
            ))

    for match in PARTNER.finditer(line):
        name = match.group(1).strip()
        if name and not is_verified_name(name, verified):
            findings.append((
                "partner",
                name,
                "named as a licensed/registered partner but not in the verified source ledger",
            ))

    for match in FIGURE.finditer(line):
        fragment = match.group(0).strip()
        if FIGURE_CONTEXT.search(fragment) and not is_verified_figure(fragment, verified):
            findings.append((
                "figure",
                fragment,
                "hard fee/capital/cap/cover figure stated as fact without a verified source",
            ))
    if not CAPABILITY_NEGATION.search(line):
        for capability, pattern in REGULATED_CAPABILITIES:
            match = pattern.search(line)
            if match and capability not in authorized:
                findings.append((
                    "capability",
                    match.group(0).strip(),
                    f"regulated product capability {capability!r} appears without Twin authorization",
                ))
    return findings


def scan(root, ledger, targets):
    verified = read_ledger(ledger)
    authorized = read_authorized(root)
    findings = []
    for path in iter_files(root, targets):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, 1):
                    for kind, text, why in scan_line(line, verified, authorized):
                        rel = os.path.relpath(path, root).replace("\\", "/")
                        findings.append((rel, line_number, kind, text, why))
        except Exception:
            continue
    return findings


def main():
    parser = argparse.ArgumentParser(description="Scan shippable surfaces for fabricated-as-real regulated facts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--ledger", default=os.path.join("mvr", "public_research", "source_ledger.json"))
    parser.add_argument("--targets", nargs="*")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    ledger = args.ledger if os.path.isabs(args.ledger) else os.path.join(root, args.ledger)
    targets = args.targets if args.targets else discover_default_targets(root)
    findings = scan(root, ledger, targets)
    if not findings:
        print("FABRICATION SCAN: clean - no unhedged, unsourced credentials/partners/figures or unauthorized regulated capabilities in shippable surfaces.")
        return

    print(f"FABRICATION SCAN: {len(findings)} claim(s) presented AS REAL but not backed by a verified source ledger:\n")
    for path, line_number, kind, text, why in findings[:80]:
        print(f"  [{kind}] {path}:{line_number}  \"{text[:90]}\"")
        print(f"          -> {why}. Mark it demo/mock, add verified evidence, or remove/authorize the capability.")
    if len(findings) > 80:
        print(f"  ... {len(findings) - 80} more")
    print("\nFix, hedge, source, or obtain authorization before export. This is CLAUDE.md Law 5 applied to the product surface.")
    sys.exit(1)


if __name__ == "__main__":
    main()
