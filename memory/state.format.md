# Market Context Cache — `mvr/state.json`

The single file that makes market truth ambient. Written at every spine checkpoint (pre-charter, pre-claim, pre-export) and by settlement runs; read by `hooks/heartbeat.py` on every user prompt and injected into context invisibly. Host-agnostic by design: it is a plain file, so Claude Code, Codex CLI, and Antigravity hosts all speak it — the file is the lingua franca; MCP is one producer of it, never the only reader path.

```json
{
  "charter_ref": "charters/CH-....md",
  "verdict": "pilot_only",
  "confidence": 0.35,
  "authorized_use": ["internal_planning", "pilot_design"],
  "not_authorized_use": ["national_rollout", "capital_allocation", "board_reporting"],
  "top_blockers": ["consumer weighted sample 67 (minimum: 100)", "guardian_or_regulatory_evidence"],
  "passport_status": "self_reported",
  "calibrated_market": true,
  "last_kernel_sync": "2026-07-06T14:00:00Z",
  "settlement_next": "2026-10-06",
  "settled_summary": "12 charters settled: pilot-survival 3.1x control base rate; 2 misses published",
  "notes": "one line, settlement-reader voice"
}
```

`settled_summary` is the **borrowed-consequences wire**: once real settlements exist, the settlement process (never the authoring agent) writes a one-line calibration digest here, and the heartbeat injects it every turn as `Track record: …`. This is the sentence no frontier model can say alone — it must always be derived from settled ledger entries, misses included, and must never be written speculatively.

Rules:
- Producers: committee flow (after kernel calls) and `scripts/settle.py` outcomes. Never hand-edited to look better — the decision log is the audit trail; state.json is its cache.
- The heartbeat injects ≤120 words: verdict, authorization, top 3 blockers, passport status, staleness, calibration boundary.
- Staleness IS state: >7d flagged, >30d the digest declares authorization void (mirrors the claim gate's rule — counsel and authority never disagree about time).
- Counsel channel fails SILENT (a broken heartbeat never bricks a session); the claim gate remains the fail-CLOSED authority.
```
Protocol in one line: spine writes state → heartbeat makes it ambient every turn → gates enforce it at the moments that matter → user sees only better builds.
```
