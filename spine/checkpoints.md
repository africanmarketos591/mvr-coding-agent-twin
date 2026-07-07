# The Counsel/Authority Contract — Spine Checkpoints

The lens advises everywhere. The spine COMMANDS at exactly three checkpoints. Skipping a checkpoint is a defect regardless of how confident the host model feels — confidence without calibration is the failure mode this file exists to stop.

| Checkpoint | Trigger | Mandatory spine calls | The spine's word is final on |
|---|---|---|---|
| **PRE-CHARTER** | Committee convened, before Build Charter is written | `category_playbook(archetype)` + `strategy_sparring(advocate_claims)` (+ `decision_check` if any evidence pack exists) | Evidence demand schedule; unsafe/overclaim register; discount weights |
| **PRE-CLAIM** | Any artifact under `claims/` is about to be created or finalized | `decision_check` + `evidence_completeness` on the current pack | Whether `authorized_use` covers the claim class. Enforced by `hooks/claim_gate.py` — not by memory |
| **PRE-EXPORT** | The case leaves the repo (sent to investor, board, lender, partner) | Latest decision-log entry verified fresh (≤30 days) against current pack | Staleness; export carries the hash + authorization block verbatim |

Boundary rule (verbatim from CLAUDE.md §3): market claims — spine wins; engineering matters — host wins.

## Route facts the dev team must not rediscover the hard way
- Edge rejects default Python UAs → always use `spine/mvr_client.py` (sets UA).
- 422 responses carry `example_valid_item` and exact unknown-key names — they are documentation; read them, iterate once, done.
- `evidence_type` has a compatibility matrix with `collection_method`/`origin` (e.g. partner pack accepts `"interview"` + `structured_field_research`, rejects `"field_interview"` in that combination).
- `retention_class: "90d"` style enums; `structured_values` keys must come from the MVR ontology (trust, reciprocity, embeddedness, channel_permission, guardian_strength, belonging, cultural_fit, narrative_looping, absence_sensitivity…).
- Telemetry lane is live: `telemetry_proxy_pack` + `source_class: telemetry_internal` + privacy envelope = admissible evidence; self-telemetry alone never clears `critical_evidence_missing` (by design — do not fight it).
- `/v1/auth-check` currently 403 not-registered upstream; probe liveness with `/v1/schema`.
- Idea-stage `decision_check` on an empty pack abstains identically for all ideas (`zero_geo_matches` refers to YOUR pack's geography, not the corpus). That is correct behavior: at time zero the spine contributes the demand schedule and discounts, not verdicts. Differentiation at time zero comes from research + operator seats.
