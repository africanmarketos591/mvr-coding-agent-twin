# Response To The beta.32 Peer Critique

## Verdict

Accepted. Codex reproduced all four reported evasions against `v1.1.0-beta.32`:

1. Inline prose could produce an empty capability list.
2. Semantic renaming could clear the lexical scan.
3. SQL and Solidity were outside the scanned carrier set.
4. Re-emitting from a weakened charter forgot the prior cut list.

The critic also correctly identified that the public wording overstated a syntactic detector as behavioral enforcement. A deterministic program cannot decide arbitrary semantic properties of arbitrary programs. The correction therefore changes both code and claim, rather than adding regex and repeating the same promise.

## Corrective architecture

- `--check` is a **naive-capability tripwire**. A clear result states that it is not semantic assurance.
- A fresh host-model or human semantic review is required for code governed by charter constraints. The review is bound to the exact contract and exact file hashes.
- The semantic review is labelled **model-attested, not deterministic proof**.
- Redirect-like charters with no extracted cut list fail as `extraction_suspect` unless they explicitly declare a capability-free disposition.
- Raw charter constraints are retained even when they do not map to the finite regulated-capability vocabulary.
- SQL, Solidity, notebooks, common IaC/config formats, Docker/Compose, and other realistic carriers enter the tripwire surface.
- Re-emitting a weaker contract carries prior constraints forward. Removal requires a complete `named_human_override` naming the removed constraint IDs and capabilities, reviewer, signature reference, and reason.
- A charter referenced by `decision-log.json` need not live at repository root; deletion or an invalid reference fails contract validation.

## Regression evidence

`tests/test_build_spec_redteam.py` turns the critic's four attacks into permanent regressions. It also includes a clean fitted-code control so the fix cannot pass merely by blocking everything. `tests/test_twin_build_spec.py` separately verifies model-review freshness, history release by signed override, extraction failure, non-root charter discovery, and carrier coverage.

## Remaining limit

A model reviewer can still be wrong or manipulated. Local logs remain tamper-evident, not tamper-proof. Enterprise deployments should use an independent reviewer or controlled model endpoint for the semantic step and preserve its receipt. The kernel remains authoritative only over its finite claim-class contract.
