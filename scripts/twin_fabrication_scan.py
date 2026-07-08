"""Scan shippable surfaces for fabricated-as-real credentials and partners.

The claim gate governs claim artifacts. The source ledger governs the charter.
But a polished demo can still present an invented clinic, licence number, or
fee as real inside UI strings, product plans, and go-to-market notes.

This scanner is a PRE-EXPORT / CI guard. It flags unhedged credentials, named
licensed partners, and hard fee/capital figures that are not backed by a
`verified` entry in `mvr/public_research/source_ledger.json`.

Exit codes:
  0 clean
  1 fabricated-as-real claims found
"""
import argparse
import json
import os
import re
import sys


DEFAULT_TARGETS = ["scaffold", "PRODUCT_PLAN.md", "GO_TO_MARKET.md", "SUMMARY.md", "README.md"]
SCAN_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".html", ".md", ".py", ".txt", ".json", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", "__pycache__", "mvr-coding-agent-twin"}

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


def scan_line(line, verified):
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
    return findings


def scan(root, ledger, targets):
    verified = read_ledger(ledger)
    findings = []
    for path in iter_files(root, targets):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, 1):
                    for kind, text, why in scan_line(line, verified):
                        rel = os.path.relpath(path, root).replace("\\", "/")
                        findings.append((rel, line_number, kind, text, why))
        except Exception:
            continue
    return findings


def main():
    parser = argparse.ArgumentParser(description="Scan shippable surfaces for fabricated-as-real regulated facts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--ledger", default=os.path.join("mvr", "public_research", "source_ledger.json"))
    parser.add_argument("--targets", nargs="*", default=DEFAULT_TARGETS)
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    ledger = args.ledger if os.path.isabs(args.ledger) else os.path.join(root, args.ledger)
    findings = scan(root, ledger, args.targets)
    if not findings:
        print("FABRICATION SCAN: clean - no unhedged, unsourced credentials/partners/figures in shippable surfaces.")
        return

    print(f"FABRICATION SCAN: {len(findings)} claim(s) presented AS REAL but not backed by a verified source ledger:\n")
    for path, line_number, kind, text, why in findings[:80]:
        print(f"  [{kind}] {path}:{line_number}  \"{text[:90]}\"")
        print(f"          -> {why}. Mark it demo/mock, or add a verified source-ledger entry.")
    if len(findings) > 80:
        print(f"  ... {len(findings) - 80} more")
    print("\nFix or hedge before export. This is CLAUDE.md Law 5 applied to the product surface.")
    sys.exit(1)


if __name__ == "__main__":
    main()
