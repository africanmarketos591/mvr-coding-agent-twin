# Peer Critique Response: beta.33 Carrier Coverage

## Verdict

Accepted. The narrower controlled-beta capability claim stands, but beta.33's semantic-review scope had a domain-relevant carrier gap.

The supplied regression reproduced against beta.33: `.dart`, `.mjs`, and `.prisma` files were absent from both the lexical scan and the hash-bound semantic-review request. Because freshness validation reused the same extension allowlist, those files could change after a passing review without invalidating it.

## Correction

- Semantic scope no longer uses a source-extension allowlist.
- Every first-party non-binary text file under the declared target paths is classified by bytes, listed, and hash-bound.
- Known or byte-detected opaque files are listed with hashes and reasons. Reviewers must acknowledge them, while the record states plainly that their behavior was not semantically analyzed.
- The Git pre-commit entry point uses the same content policy, so a Dart-only or extensionless-text commit cannot bypass the build contract.
- Host-model self-review remains available for local accountability, but `--require-independent-review` rejects it for PRE-EXPORT and capability evaluation.

## Permanent Tests

`tests/test_carrier_coverage_gap.py` covers Dart, MJS, Prisma, GraphQL, Gradle, Elixir, extensionless text, opaque-file accounting, byte-change invalidation, and reviewer independence. `tests/test_pre_commit_gate.py` contains a Dart-only allow/block pair.

## Remaining Boundary

Text coverage is not program proof. Opaque bytes are freshness-bound, not semantically interpreted. An independent reviewer can still be wrong. The deterministic spine continues to authorize finite claim classes only; code behavior remains reviewer-attested.
