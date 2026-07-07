"""Advisory response sentinel for claim-shaped assistant prose.

The artifact gates are authority: claim_gate.py and pre_commit_claim_gate.py fail
closed for claim files. Chat/prose is different. This hook is counsel: it detects
obvious claim-shaped assistant output and writes an advisory receipt, but exits 0.

Use as an optional Stop/response hook where the host supports final-response
inspection. It never authorizes, never blocks, and never replaces PRE-CLAIM.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from claim_gate import classify_content  # noqa: E402


TEXT_KEYS = {
    "response", "assistant_response", "message", "content", "text", "output",
    "final", "completion", "answer",
}


def collect_text(value, depth=0):
    if depth > 6:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        chunks = []
        for item in value:
            chunks.extend(collect_text(item, depth + 1))
        return chunks
    if isinstance(value, dict):
        chunks = []
        for key, item in value.items():
            if str(key) in TEXT_KEYS:
                chunks.extend(collect_text(item, depth + 1))
            elif isinstance(item, (dict, list)):
                chunks.extend(collect_text(item, depth + 1))
        return chunks
    return []


def write_receipt(project_dir, record):
    try:
        path = os.path.join(project_dir, "mvr", "response-sentinel.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record["ts"] = datetime.now(timezone.utc).isoformat()
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def emit_context(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": context,
        }
    }))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CURSOR_PROJECT_DIR") or os.getcwd()
    text = "\n".join(collect_text(payload))[:50000]
    claim_class, reason = classify_content("assistant-response.md", text)
    if not claim_class:
        return
    record = {
        "event": "response_claim_warning",
        "claim_class": claim_class,
        "reason": reason,
        "action": "advisory_only_run_pre_claim_before_external_use",
    }
    write_receipt(project_dir, record)
    emit_context(
        f"[MVR TWIN RESPONSE SENTINEL] Your draft response appears claim-bearing "
        f"({claim_class}: {reason}). This is advisory only, not a block. Before any "
        "external artifact or user-facing market claim, move the claim into claims/ "
        "and run PRE-CLAIM; do not treat chat prose as authorization."
    )


if __name__ == "__main__":
    main()
