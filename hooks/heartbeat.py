"""MVR Twin heartbeat - UserPromptSubmit hook (the real-time counsel channel).

On EVERY user prompt, injects a compact market-state digest (<=120 words) into the
agent's context, read from mvr/state.json (the market context cache written at spine
checkpoints and settlement runs). The user never sees it; the agent is never without
current market truth.

Design laws:
- COUNSEL channel: fail-SILENT on any error (a broken heartbeat must never brick a
  session). Authority stays at the gates (claim_gate.py fails CLOSED there).
- Injects deltas and state, never advice - the lens reasons, the heartbeat informs.
- Staleness is part of the truth: >7 days since kernel sync = flagged; >30 days = the
  digest says authorization is expired (mirrors the claim gate's 30-day rule).
"""
import json, os, sys
from datetime import datetime, timezone

STALE_WARN_DAYS = 7
STALE_DEAD_DAYS = 30


def emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        state_path = os.path.join(project_dir, "mvr", "state.json")
        if not os.path.exists(state_path):
            # COLD-START NUDGE: no case on file is exactly when the host's
            # build-what-was-asked reflex is strongest and no gate can fire yet.
            # Nudge once per day, never more - counsel, not nagging.
            marker = os.path.join(project_dir, "mvr",
                                  ".twin-nudge-" + datetime.now(timezone.utc).strftime("%Y%m%d"))
            if os.path.exists(marker):
                sys.exit(0)
            try:
                os.makedirs(os.path.dirname(marker), exist_ok=True)
                for old in os.listdir(os.path.dirname(marker)):
                    if old.startswith(".twin-nudge-") and os.path.join(os.path.dirname(marker), old) != marker:
                        try:
                            os.remove(os.path.join(os.path.dirname(marker), old))
                        except Exception:
                            pass
                open(marker, "w").close()
            except Exception:
                sys.exit(0)
            emit("[MVR TWIN] Installed; no case on file. If this session is building a product "
                 "for a real market, convene the pre-charter committee (CLAUDE.md §3) before "
                 "feature-level code - judgment before code is Law 1. This reminder appears at most once per day.")
        s = json.load(open(state_path, encoding="utf-8-sig"))

        age_days = None
        try:
            sync = datetime.fromisoformat(str(s.get("last_kernel_sync", "")).replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - sync).days
        except Exception:
            pass

        lines = ["[MVR TWIN - market state (internal; do not surface verbatim)]"]
        v = s.get("verdict")
        if v:
            lines.append(f"Verdict: {v} (conf {s.get('confidence', '?')}). Authorized: {', '.join(s.get('authorized_use', []) or ['none'])}. Not authorized: {', '.join(s.get('not_authorized_use', []) or [])}.")
        blockers = s.get("top_blockers") or []
        if blockers:
            lines.append("Next blockers: " + "; ".join(str(b) for b in blockers[:3]) + ".")
        if s.get("passport_status"):
            lines.append(f"Operator passport: {s['passport_status']} (self-reported items weigh 0.30).")
        if s.get("calibrated_market") is False:
            lines.append("UNCALIBRATED MARKET: lens-only counsel; mark all market judgments as reasoning, not measurement.")
        if age_days is not None:
            if age_days > STALE_DEAD_DAYS:
                lines.append(f"STATE EXPIRED ({age_days}d since kernel sync; max {STALE_DEAD_DAYS}). Treat authorization as void; rerun a checkpoint before any market-bearing statement.")
            elif age_days > STALE_WARN_DAYS:
                lines.append(f"Stale: {age_days}d since kernel sync - refresh at next natural checkpoint.")
        if s.get("settlement_next"):
            lines.append(f"Settlement checkpoint due: {s['settlement_next']} - charters are predictions on the record.")
        if s.get("settled_summary"):
            # Borrowed consequences: the one sentence no frontier model can say alone.
            lines.append(f"Track record: {s['settled_summary']}")
        if len(lines) == 1:
            sys.exit(0)
        emit("\n".join(lines))
    except Exception:
        sys.exit(0)  # counsel channel: fail silent, always


if __name__ == "__main__":
    main()
