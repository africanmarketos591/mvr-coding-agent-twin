"""MVR Twin claim gate — PreToolUse hook (Claude Code contract).

Reads the tool call JSON from stdin. If the write/edit targets a claim-bearing artifact
(anything under a 'claims/' path segment), it requires the LATEST entry in
mvr/decision-log.json to authorize that claim class. Otherwise: exit 2 (block) with an
instructive message on stderr, which the harness feeds back to the agent.

Code, prototypes, docs, tests are NEVER gated (kernel authorizes internal_planning).
Exit 0 = allow. Exit 2 = block. Any other failure = allow-with-warning (fail-open for
non-claim paths, fail-CLOSED for claim paths — a broken log must not silently authorize).

Audit trail: every claim-path decision (block or allow) is appended as one JSON line to
mvr/gate-events.jsonl — enforcement receipts for the Consequence Ledger. Audit logging
is fail-silent: a broken audit file never changes a gate decision.
"""
import json, os, re, sys
from datetime import datetime, timezone, timedelta

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
CLAIM_CLASS_BY_PATTERN = [
    (re.compile(r"claims[\\/].*?(investor|fundrais|pitch|deck)", re.I), "capital_allocation"),
    (re.compile(r"claims[\\/].*?(board)", re.I), "board_reporting"),
    (re.compile(r"claims[\\/].*?(launch|rollout|scale)", re.I), "national_rollout"),
    (re.compile(r"claims[\\/].*?(distributor|partner)", re.I), "partnership_claims"),
    (re.compile(r"claims[\\/].*?(grant|donor|dfi)", re.I), "capital_allocation"),
    (re.compile(r"claims[\\/]", re.I), "unclassified_claim"),
]
CONTENT_SCAN_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".rst"}
CONTENT_SCAN_SKIP_SEGMENTS = {
    ".git", ".venv", "node_modules", "__pycache__",
    "mvr-coding-agent-twin", "mvr-twin", "twin",
    "mvr", "src", "tests", "hooks", "scripts", "memory", "adapters",
    "release-manifests", "rehearsals",
}
CONTENT_SCAN_SAFE_FILENAMES = {
    "charter.md", "mirror.md", "transcript.md", "transcript_report.md",
    "operator_log.md", "scorer_sheet.md", "readme.md", "changelog.md",
    "security.md", "license",
}
MAX_LOG_AGE_DAYS = 30


def audit(project_dir, record):
    """Append one enforcement receipt. Fail-silent: auditing never alters a decision."""
    try:
        path = os.path.join(project_dir, "mvr", "gate-events.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record["ts"] = datetime.now(timezone.utc).isoformat()
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def block(msg):
    sys.stderr.write("[MVR CLAIM GATE] " + msg + "\n")
    sys.exit(2)


def tool_paths(tool_input):
    if not isinstance(tool_input, dict):
        return []
    paths = []
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if value:
            paths.append(str(value))
    for key in ("edits", "files"):
        values = tool_input.get(key)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    for path_key in ("file_path", "path", "notebook_path"):
                        value = item.get(path_key)
                        if value:
                            paths.append(str(value))
    return paths


def tool_text(tool_input):
    if not isinstance(tool_input, dict):
        return ""
    chunks = []
    for key in ("content", "new_string", "old_string", "text"):
        value = tool_input.get(key)
        if isinstance(value, str):
            chunks.append(value)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for item in edits:
            if isinstance(item, dict):
                for key in ("new_string", "old_string", "content", "text"):
                    value = item.get(key)
                    if isinstance(value, str):
                        chunks.append(value)
    return "\n".join(chunks)


def should_scan_content(path):
    normalized = path.replace("\\", "/").lower()
    parts = [p for p in normalized.split("/") if p]
    if any(part in CONTENT_SCAN_SKIP_SEGMENTS for part in parts):
        return False
    name = parts[-1] if parts else normalized
    if name in CONTENT_SCAN_SAFE_FILENAMES:
        return False
    if "." in name:
        ext = "." + name.rsplit(".", 1)[-1]
        if ext not in CONTENT_SCAN_EXTENSIONS:
            return False
    return "claims/" not in normalized


def classify_content(path, text):
    if not text or not should_scan_content(path):
        return None, ""
    haystack = (path + "\n" + text[:50000]).lower()
    if any(term in haystack for term in ("pitch deck", "investor memo", "investment memo", "fundraising", "series a", "valuation", "grant application", "dfi funding", "capital allocation")):
        return "capital_allocation", "capital/funding claim language outside claims/"
    if any(term in haystack for term in ("board pack", "board memo", "board report")):
        return "board_reporting", "board-reporting claim language outside claims/"
    regulated_money = any(term in haystack for term in ("wallet", "escrow", "e-money", "deposit", "savings", "custody of funds", "customer funds"))
    rollout_terms = any(term in haystack for term in ("terms", "launch", "rollout", "go-to-market", "scale", "nationwide", "national"))
    if regulated_money and rollout_terms:
        return "national_rollout", "regulated money/launch claim language outside claims/"
    if any(term in haystack for term in ("launch plan", "rollout plan", "ready to scale", "scale nationally", "national rollout")):
        return "national_rollout", "rollout claim language outside claims/"
    partner_terms = any(term in haystack for term in ("distributor", "supplier", "partner", "wholesaler", "certified", "regulatory clearance"))
    claim_terms = any(term in haystack for term in ("terms", "approval", "certification", "pitch", "launch"))
    if partner_terms and claim_terms:
        return "partnership_claims", "partnership/distributor claim language outside claims/"
    return None, ""


def classify_path(path):
    for pattern, cls in CLAIM_CLASS_BY_PATTERN:
        if pattern.search(path):
            return cls
    return None


def as_list(value):
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def signed_human_review(latest):
    review = latest.get("human_review")
    if not isinstance(review, dict):
        return False, "missing human_review object"
    reviewer = str(review.get("reviewer") or "").strip()
    signature = str(review.get("signature_ref") or "").strip()
    if reviewer and signature:
        return True, ""
    return False, "human_review requires both reviewer and signature_ref"


def authorization_result(latest, claim_class):
    decision_authorization = latest.get("decision_authorization") or {}
    if not isinstance(decision_authorization, dict):
        decision_authorization = {}
    authorized = as_list(decision_authorization.get("authorized_use"))
    not_authorized = as_list(decision_authorization.get("not_authorized_use"))
    gaps = latest.get("evidence_gaps") or latest.get("abstention_reason_codes") or []

    if claim_class not in authorized:
        return False, "not_authorized", (
            f"Claim class '{claim_class}' is NOT in authorized_use {authorized} "
            f"(not_authorized_use: {not_authorized}). Outstanding evidence: {gaps}. "
            "Options: (1) gather the listed evidence and rerun PRE-CLAIM; (2) downgrade the artifact to the "
            "authorized level (e.g. internal_planning memo); (3) request named-human review for an override - "
            "overrides are logged, never silent."
        ), {}

    review = latest.get("human_review") if isinstance(latest.get("human_review"), dict) else {}
    if review.get("required") is True:
        ok, reason = signed_human_review(latest)
        if not ok:
            return False, "human_review_unsigned", (
                f"Claim class '{claim_class}' is listed in authorized_use, but human_review.required=true "
                f"and the review is unsigned ({reason}). Add reviewer + signature_ref or rerun PRE-CLAIM."
            ), {}

    basis = str(latest.get("authorization_basis") or latest.get("authorization_source") or "").strip()
    basis_lower = basis.lower()
    override_note = str(latest.get("override_note") or "").strip()
    is_override = "override" in basis_lower or bool(override_note)
    kernel_authorized = as_list(latest.get("kernel_authorized_use"))

    if kernel_authorized and claim_class not in kernel_authorized and not is_override:
        return False, "ambiguous_local_authorization", (
            f"Claim class '{claim_class}' appears in local authorized_use but not in kernel_authorized_use "
            f"{kernel_authorized}. If this is a named-human override, mark authorization_basis='named_human_override', "
            "add override_note, and sign human_review. Otherwise rerun PRE-CLAIM."
        ), {}

    if is_override:
        if not kernel_authorized:
            return False, "override_missing_kernel_baseline", (
                "Named-human overrides must record kernel_authorized_use so auditors can distinguish local override "
                "from kernel-backed authorization. Add kernel_authorized_use from the live receipt."
            ), {}
        ok, reason = signed_human_review(latest)
        if not ok:
            return False, "override_unsigned", (
                f"Named-human override for '{claim_class}' is unsigned ({reason}). "
                "Overrides require reviewer + signature_ref."
            ), {}
        if not override_note:
            return False, "override_note_missing", (
                f"Named-human override for '{claim_class}' needs override_note explaining that this is local-only "
                "and not kernel authorization."
            ), {}
        return True, "allow_override_claim", "", {
            "authorization_basis": basis or "named_human_override",
            "kernel_authorized_use": kernel_authorized,
        }

    return True, "allow_claim", "", {"authorized_use": authorized}


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # not a parseable tool call — never brick the session

    tool = payload.get("tool_name", "")
    if tool not in WRITE_TOOLS:
        sys.exit(0)
    path = ""
    claim_class = None
    tool_input = payload.get("tool_input") or {}
    candidates = tool_paths(tool_input)
    text = tool_text(tool_input)
    for candidate in candidates:
        candidate_class = classify_path(candidate)
        if candidate_class:
            path = candidate
            claim_class = candidate_class
            break
    if claim_class is None:
        for candidate in candidates:
            candidate_class, reason = classify_content(candidate, text)
            if candidate_class:
                project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
                audit(project_dir, {"event": "block", "claim_class": candidate_class,
                                    "path": candidate, "reason": "claim_content_outside_claims",
                                    "detail": reason, "tool": tool})
                block(
                    f"'{candidate}' appears claim-bearing ({candidate_class}) but is outside claims/. "
                    f"Detector: {reason}. Move the artifact under claims/ with an explicit name and run PRE-CLAIM; "
                    "writing claim-shaped content elsewhere is path evasion."
                )
        sys.exit(0)  # not a claim artifact - building is always allowed

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    def deny(msg, reason_code):
        audit(project_dir, {"event": "block", "claim_class": claim_class,
                            "path": path, "reason": reason_code, "tool": tool})
        block(msg)

    # Locate decision log relative to project root (hook cwd = project dir per contract)
    log_path = os.path.join(project_dir, "mvr", "decision-log.json")
    if not os.path.exists(log_path):
        deny(
            f"'{path}' is a claim-bearing artifact ({claim_class}) but mvr/decision-log.json does not exist. "
            "Run the PRE-CLAIM checkpoint first: decision_check + evidence_completeness on the current pack, "
            "append the entry, then retry. Building code is never blocked - claims require authorization.",
            "no_decision_log",
        )
    try:
        entries = json.load(open(log_path, encoding="utf-8-sig"))
        latest = entries[-1] if isinstance(entries, list) and entries else None
    except Exception as e:
        deny(f"mvr/decision-log.json is unreadable ({e}). A broken log cannot authorize claims. Fix the log, rerun PRE-CLAIM.",
             "log_unreadable")
    if not latest:
        deny("mvr/decision-log.json is empty. Run PRE-CLAIM and append the decision entry first.", "log_empty")
    if not isinstance(latest, dict):
        deny("Latest decision-log entry is not an object. A malformed log cannot authorize claims. Rerun PRE-CLAIM.",
             "log_malformed")

    # Freshness (PRE-EXPORT staleness rule)
    ts = latest.get("timestamp", "")
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if age > timedelta(days=MAX_LOG_AGE_DAYS):
            stale_gaps = latest.get("evidence_gaps") or latest.get("abstention_reason_codes") or []
            deny(
                f"Latest decision-log entry is {age.days} days old (max {MAX_LOG_AGE_DAYS}). "
                f"Renewal path: (1) refresh the evidence pack - last known outstanding gaps: {stale_gaps or 'none recorded'}; "
                "(2) rerun PRE-CLAIM (decision_check + evidence_completeness on the CURRENT pack); "
                "(3) append the new entry via the decision-log skeleton. Old evidence may have aged out too - "
                "the kernel's freshness rules decide, not this hook.",
                "authorization_stale",
            )
    except Exception:
        deny("Latest decision-log entry has no valid ISO timestamp. Rerun PRE-CLAIM.", "timestamp_invalid")

    if claim_class == "unclassified_claim":
        deny(
            f"'{path}' sits under claims/ but matches no known claim class. Name it so its class is explicit "
            "(investor/board/launch/distributor/grant), or move it out of claims/ if it is not claim-bearing.",
            "unclassified_claim",
        )
    ok, event, message, extra = authorization_result(latest, claim_class)
    if not ok:
        deny(message, event)
    record = {"event": event, "claim_class": claim_class,
              "path": path, "entry_id": latest.get("entry_id"), "tool": tool}
    record.update(extra)
    audit(project_dir, record)
    sys.exit(0)


if __name__ == "__main__":
    main()
