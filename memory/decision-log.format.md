# Decision Log Format — `mvr/decision-log.json`

Append-only JSON array. The claim gate reads the LAST entry; humans read the companion `mvr/decision-log.md` if the team wants prose. Machine file is canonical.

Each entry (append on every PRE-CHARTER and PRE-CLAIM checkpoint):

```json
{
  "entry_id": "DL-<uuid>",
  "timestamp": "2026-07-06T14:00:00Z",
  "checkpoint": "pre_charter | pre_claim | pre_export",
  "charter_ref": "charters/CH-....md",
  "charter_hash": "<canonical sha256 from scripts/preregister.py>",
  "charter_hash_mode": "canonical-charter-v2",
  "archetype": "agritech_aggregator",
  "market_scope": "UG-KE",
  "redirect_pattern": "coordination_over_wallet | null",
  "kernel_receipts": {
    "decision_check_id": "...",
    "semantic_decision_hash": "...",
    "routes_called": ["/v1/category-playbook/fintech_platform", "/v1/strategy-sparring", "/v1/decision-check"]
  },
  "verdict": "permission_not_yet_earned | pilot_only | pilot_ready | ready_to_scale | abstained",
  "confidence": 0.15,
  "abstention_reason_codes": ["..."],
  "kernel_authorized_use": ["internal_planning"],
  "authorization_basis": "kernel_receipt | named_human_override",
  "decision_authorization": {
    "authorized_use": ["internal_planning"],
    "not_authorized_use": ["national_rollout", "capital_allocation", "board_reporting"]
  },
  "evidence_gaps": ["consumer weighted sample 67 (minimum: 100)", "guardian_or_regulatory_evidence"],
  "operator_passport_status": "self_reported | partially_attested | attested",
  "settlement": {
    "preregistered": true,
    "anchor_refs": ["<git-commit>", "<wayback-url>"],
    "checkpoints": [
      { "at": "2026-10-06", "criterion": "pilot live in >=1 named school; >=1 instrumented event stream active" },
      { "at": "2027-07-06", "criterion": "product emitting events (alive) AND arrears-recovery delta reported vs baseline" }
    ],
    "settled": null
  },
  "human_review": { "required": false, "reviewer": null, "signature_ref": null },
  "override_note": null,
  "build_contract_override": {
    "basis": "named_human_override",
    "reviewer": "<named reviewer>",
    "signature_ref": "<signature or approval artifact>",
    "note": "Why the prior implementation constraint is no longer applicable.",
    "allow_removed_capabilities": ["digital_lending"],
    "allow_removed_constraint_ids": ["<16-char constraint id from prior build_spec.json>"]
  },
  "notes_for_settlement_reader": "One plain sentence you are willing to be judged by later."
}
```

Rules:
- Entries are never edited or deleted; corrections are new entries referencing the old `entry_id`.
- The charter hash MUST verify with `python scripts/preregister.py --verify <charter.md>`. A pasted hash that does not verify is not preregistration evidence.
- `archetype`, `market_scope`, and `redirect_pattern` are advisory dimensions consumed only by `scripts/build_priors.py`. They never affect claim authorization. Absent values bucket as `unknown_*` and are safe, just uninformative.
- `settlement.settled` is written ONLY by the settlement process (scripts/settle.py output or instrumentation silence detection) — never by the authoring agent.
- If `human_review.required` is true and unsigned, the claim gate treats the entry as non-authorizing regardless of `authorized_use`.
- `kernel_authorized_use` is the live kernel baseline copied from the receipt. If local `decision_authorization.authorized_use` exceeds it, the entry MUST be a signed `named_human_override` with `override_note`; otherwise the gate fails closed as ambiguous local authorization.
- Override receipts are emitted as `allow_override_claim`, never `allow_claim`. A human override is local discipline, not kernel authorization, and external parties must verify the kernel receipt before trusting exported claims.
- `build_contract_override` is separate from claim authorization. It is required only when a re-emitted build contract removes a previously active implementation constraint. It must cover every removed capability and constraint ID; partial or unsigned removal fails closed and carries the old constraint forward.
