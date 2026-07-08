"""Hardened content-scan policy for the claim gate.

The claim gate must scan obvious claim-shaped text files outside claims/. This
policy covers document, data, and notebook formats where market claims are likely
to be hidden, while avoiding source-code false positives.
"""

SKIP_SEGMENTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "mvr-coding-agent-twin",
    "mvr-twin",
    "twin",
    "mvr",
    "src",
    "tests",
    "hooks",
    "scripts",
    "memory",
    "adapters",
    "release-manifests",
    "rehearsals",
}

TWIN_ARTIFACTS = {
    "charter.md",
    "mirror.md",
    "transcript.md",
    "transcript_report.md",
    "operator_log.md",
    "scorer_sheet.md",
}

ROOT_ONLY_SAFE = {
    "agents.md",
    "claude.md",
    "readme.md",
    "changelog.md",
    "security.md",
    "llms.txt",
    "llms-full.txt",
    "license",
    "contributing.md",
    "code_of_conduct.md",
    "replication_receipts.md",
    "stress_test_report.md",
}

TEXT_SCAN_EXTENSIONS = {
    ".md",
    ".markdown",
    ".mdx",
    ".txt",
    ".text",
    ".rst",
    ".rtf",
    ".html",
    ".htm",
    ".xml",
    ".csv",
    ".tsv",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ipynb",
    ".tex",
    ".adoc",
    ".asciidoc",
    ".org",
}

BINARY_CLAIM_CARRIERS = {
    ".pdf",
    ".docx",
    ".doc",
    ".pptx",
    ".ppt",
    ".xlsx",
    ".xls",
    ".pages",
    ".key",
    ".numbers",
    ".odt",
    ".odp",
}


def _parts(path):
    normalized = str(path).replace("\\", "/").lower()
    return normalized, [part for part in normalized.split("/") if part]


def should_scan_content(path):
    normalized, parts = _parts(path)
    if any(part in SKIP_SEGMENTS for part in parts):
        return False
    if "claims/" in normalized:
        return False
    name = parts[-1] if parts else normalized
    if name in TWIN_ARTIFACTS:
        return False
    if len(parts) == 1 and name in ROOT_ONLY_SAFE:
        return False
    if "." in name:
        ext = "." + name.rsplit(".", 1)[-1]
        return ext in TEXT_SCAN_EXTENSIONS
    return True


def binary_claim_carrier(path):
    normalized, parts = _parts(path)
    if any(part in SKIP_SEGMENTS for part in parts):
        return False
    if "claims/" in normalized:
        return False
    name = parts[-1] if parts else normalized
    if "." not in name:
        return False
    return ("." + name.rsplit(".", 1)[-1]) in BINARY_CLAIM_CARRIERS
