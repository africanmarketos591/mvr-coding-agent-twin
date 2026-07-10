# Cursor beta.35 retry audit

Date: 2026-07-10

## Verdict

**Kernel-authenticated, build-rejected.** This retry proves that the full Twin package and live enterprise-scope spine ran. It does not prove that the generated application passed its fitted build contract or was ready to use.

## What independently verified

- The downloaded package matched all 248 tracked files in the tagged beta.35 release.
- The installer completed all 34 offline suites.
- The live kernel reported v6.32.0 and returned a ledger-verifiable `immutable_audit_hash`.
- The committee packet and decision log shared authority hashes.
- The charter's canonical preregistration hash verified.

## Why the run failed

- The mandatory build check exited 1 with two `fund_custody` lexical hits on its declared product surface.
- The semantic-review file used `model_id: auto` and was written by the launcher itself; it did not identify an actual reviewing model.
- The application import check exited 1 because Flask was not installed.
- The launcher set its overall `ok` flag to true without requiring those failed steps to pass.

The beta.35 run verifier authenticated authority and artifact consistency but did not re-run the product tripwire. That allowed a genuine receipt and a failed build check to coexist with a misleading `verified` summary. Beta.36 closes that verifier gap.

## Product spot-check

After installing the declared dependency in an isolated audit environment, the generated prototype still failed basic operational controls:

- An anonymous request could seed all 20 members.
- Twenty anonymous KES 1 contribution records queued a fixed KES 40,000 payout.
- An anonymous payout confirmation with an empty M-Pesa reference succeeded.
- The resulting ledger balance became KES -39,980.
- Member phone numbers were visible on the anonymous page.

These are application defects, not evidence that the kernel failed. They demonstrate why Twin run-evidence verification must never be presented as app test, security, or production-readiness certification.

## Permanent regression

Beta.36 makes `twin_verify_run.py --stage build|export` re-run the deterministic tripwire over the exact hash-bound review targets, rejects placeholder semantic-review identities, and states the product-test boundary in the CLI/docs. The exact live-receipt plus failed-tripwire construction is now a regression test.
