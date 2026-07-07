"""MVR Twin claim gate - git pre-commit edition (host-agnostic authority).

Agent-harness hooks vary by host (Claude Code and Antigravity 2.0 have them; Cursor
partially; Codex CLI differently). Every host commits code. This script enforces the
SAME claim-gate contract at the git level, so authority survives on any host:

  staged file under claims/  ->  latest mvr/decision-log.json entry must authorize
                                 that claim class, fresh within 30 days. Else the
                                 commit is rejected with the same instructive message.

Install (once per repo):
  echo 'python mvr-coding-agent-twin/hooks/pre_commit_claim_gate.py || exit 1' >> .git/hooks/pre-commit
  (or wire via the pre-commit framework; see README Host Support Matrix)

Same doctrine as claim_gate.py: code is never gated; claims are denied by default;
broken/stale logs fail CLOSED for claims; every decision is receipted to
mvr/gate-events.jsonl (fail-silent auditing).
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from claim_gate import MAX_LOG_AGE_DAYS, audit, authorization_result, classify_escalating_content, classify_path  # noqa: E402

from datetime import datetime, timezone, timedelta  # noqa: E402


def repo_root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return os.environ.get("CLAUDE_PROJECT_DIR", ".")


def staged_paths():
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             capture_output=True, text=True, check=True)
        return [line.strip() for line in out.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def read_text_for_scan(root, path):
    full = os.path.join(root, path)
    try:
        if os.path.getsize(full) > 512 * 1024:
            return ""
        with open(full, "r", encoding="utf-8-sig") as handle:
            return handle.read(50000)
    except (UnicodeDecodeError, OSError):
        return ""


def fail(root, claim_class, path, reason_code, msg):
    audit(root, {"event": "block", "claim_class": claim_class, "path": path,
                 "reason": reason_code, "tool": "git-pre-commit"})
    sys.stderr.write("[MVR CLAIM GATE / pre-commit] " + msg + "\n")
    sys.exit(1)


def main():
    root = repo_root()
    paths = staged_paths()
    for path in paths:
        if classify_path(path):
            continue
        claim_class, reason, tier = classify_escalating_content(path, read_text_for_scan(root, path))
        if claim_class:
            fail(root, claim_class, path, "claim_content_outside_claims",
                 f"staged '{path}' appears claim-bearing ({claim_class}) but is outside claims/. "
                 f"Detector ({tier}): {reason}. Move it under claims/ with an explicit name and run PRE-CLAIM; "
                 "writing claim-shaped content elsewhere is path evasion.")

    claim_files = [(p, classify_path(p)) for p in paths]
    claim_files = [(p, c) for p, c in claim_files if c]
    if not claim_files:
        sys.exit(0)  # no claim artifacts staged - commits of code are never gated

    log_path = os.path.join(root, "mvr", "decision-log.json")
    for path, claim_class in claim_files:
        if not os.path.exists(log_path):
            fail(root, claim_class, path, "no_decision_log",
                 f"staged '{path}' is claim-bearing ({claim_class}) but mvr/decision-log.json does not exist. "
                 "Run the PRE-CLAIM checkpoint, append the entry, then commit.")
        try:
            entries = json.load(open(log_path, encoding="utf-8-sig"))
            latest = entries[-1] if isinstance(entries, list) and entries else None
        except Exception as e:
            fail(root, claim_class, path, "log_unreadable",
                 f"mvr/decision-log.json is unreadable ({e}). A broken log cannot authorize claims.")
        if not isinstance(latest, dict):
            fail(root, claim_class, path, "log_malformed",
                 "Latest decision-log entry is missing or malformed. Rerun PRE-CLAIM.")
        ts = latest.get("timestamp", "")
        try:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            fail(root, claim_class, path, "timestamp_invalid",
                 "Latest decision-log entry has no valid ISO timestamp. Rerun PRE-CLAIM.")
        if age > timedelta(days=MAX_LOG_AGE_DAYS):
            stale_gaps = latest.get("evidence_gaps") or latest.get("abstention_reason_codes") or []
            fail(root, claim_class, path, "authorization_stale",
                 f"Latest decision-log entry is {age.days} days old (max {MAX_LOG_AGE_DAYS}). "
                 f"Renewal path: refresh evidence (last known gaps: {stale_gaps or 'none recorded'}), "
                 "rerun PRE-CLAIM on the current pack, append the new entry, then commit.")
        if claim_class == "unclassified_claim":
            fail(root, claim_class, path, "unclassified_claim",
                 f"staged '{path}' sits under claims/ but matches no known claim class. Name it explicitly "
                 "(investor/board/launch/distributor/grant) or move it out of claims/.")
        ok, event, message, extra = authorization_result(latest, claim_class)
        if not ok:
            fail(root, claim_class, path, event, message)
        record = {"event": event, "claim_class": claim_class, "path": path,
                  "entry_id": latest.get("entry_id"), "tool": "git-pre-commit"}
        record.update(extra)
        audit(root, record)
    sys.exit(0)


if __name__ == "__main__":
    main()
