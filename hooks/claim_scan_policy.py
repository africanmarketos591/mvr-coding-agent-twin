"""Hardened content-scan policy for the claim gate.

The claim gate must scan obvious claim-shaped text files outside claims/. This
policy covers document, data, and notebook formats where market claims are likely
to be hidden, while avoiding source-code false positives.
"""
import os

SKIP_SEGMENTS_ANY = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "mvr-coding-agent-twin",
    "mvr-twin",
    "release-manifests",
    "rehearsals",
}

MVR_MANAGED_EXACT = {
    ("mvr", ".gitignore"),
    ("mvr", "state.json"),
    ("mvr", "passport.json"),
    ("mvr", "decision-log.json"),
    ("mvr", "decision-log.seed.json"),
    ("mvr", "gate-events.jsonl"),
    ("mvr", "committee_packet.json"),
    ("mvr", "build_spec.json"),
    ("mvr", "build-contract-history.jsonl"),
    ("mvr", "semantic-review-request.json"),
    ("mvr", "semantic-review.json"),
    ("mvr", "settlement_map.json"),
    ("mvr", "settlement-draft.json"),
}

MVR_MANAGED_PREFIXES = {
    ("mvr", "checkpoints"),
    ("mvr", "public_research"),
}

PACKAGE_MANAGED_PREFIXES = {
    ("benchmarks", "mvr-viability-v1"),
}

PACKAGE_MANAGED_EXACT = {
    ("adapters", "agents.md"),
    ("adapters", "antigravity-knowledge.md"),
    ("adapters", "cursor-rules.md"),
    ("memory", "decision-log.format.md"),
    ("reviews", "peer_critique_response_beta32.md"),
    ("reviews", "peer_critique_response_beta33.md"),
}

TWIN_ARTIFACTS = {
    "preflight.md",
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
    "capability_claim.md",
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
    ".svg",
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
    raw = str(path)
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if root:
        try:
            abs_path = os.path.abspath(raw)
            abs_root = os.path.abspath(root)
            common = os.path.commonpath([abs_path, abs_root])
            if os.path.normcase(common) == os.path.normcase(abs_root):
                raw = os.path.relpath(abs_path, abs_root)
        except Exception:
            pass
    normalized = raw.replace("\\", "/").lower()
    return normalized, [part for part in normalized.split("/") if part]


def _is_mvr_managed(parts):
    tuple_parts = tuple(parts)
    if tuple_parts in MVR_MANAGED_EXACT:
        return True
    return any(tuple_parts[:len(prefix)] == prefix for prefix in MVR_MANAGED_PREFIXES)


def _is_package_managed(parts):
    tuple_parts = tuple(parts)
    if tuple_parts in PACKAGE_MANAGED_EXACT:
        return True
    return any(tuple_parts[:len(prefix)] == prefix for prefix in PACKAGE_MANAGED_PREFIXES)


def should_scan_content(path):
    normalized, parts = _parts(path)
    if any(part in SKIP_SEGMENTS_ANY for part in parts):
        return False
    if _is_mvr_managed(parts):
        return False
    if _is_package_managed(parts):
        return False
    if "claims/" in normalized:
        return False
    name = parts[-1] if parts else normalized
    if len(parts) == 1 and name in TWIN_ARTIFACTS:
        return False
    if len(parts) == 1 and name in ROOT_ONLY_SAFE:
        return False
    if "." in name:
        ext = "." + name.rsplit(".", 1)[-1]
        return ext in TEXT_SCAN_EXTENSIONS
    return True


def binary_claim_carrier(path):
    normalized, parts = _parts(path)
    if any(part in SKIP_SEGMENTS_ANY for part in parts):
        return False
    if _is_mvr_managed(parts):
        return False
    if _is_package_managed(parts):
        return False
    if "claims/" in normalized:
        return False
    name = parts[-1] if parts else normalized
    if "." not in name:
        return False
    return ("." + name.rsplit(".", 1)[-1]) in BINARY_CLAIM_CARRIERS
