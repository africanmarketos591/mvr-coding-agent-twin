"""Offline tests for canonical preregistration hashing."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import preregister
import twin_claim_coverage


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "charter.md")
        template = (
            "# BUILD CHARTER - Test\n\n"
            "**Status:** build_authorized | **Preregistration hash:** {{canonical_sha256}} "
            "(anchors: {{anchor_refs}})\n\n"
            "Body claim.\n"
            "- t+90d: test\n"
        )
        write(path, template)
        digest = preregister.digest_for(path)
        write(path, template.replace("{{canonical_sha256}}", digest).replace("{{anchor_refs}}", "<git>, <wayback>"))
        check("embedded hash verifies after insertion", preregister.embedded_hash(path) == preregister.digest_for(path))

        before = preregister.digest_for(path)
        with open(path, "a", encoding="utf-8") as f:
            f.write("New prediction text.\n")
        after = preregister.digest_for(path)
        check("body changes alter canonical hash", before != after)

        no_hash = os.path.join(d, "no_hash.md")
        write(no_hash, "# BUILD CHARTER - Missing\n")
        check("missing embedded hash returns None", preregister.embedded_hash(no_hash) is None)

        dup = os.path.join(d, "duplicate.md")
        write(
            dup,
            "# BUILD CHARTER - Duplicate\n\n"
            "**Preregistration hash:** {{canonical_sha256}} (anchors: pending)\n\n"
            "**Preregistration hash:** 0000000000000000000000000000000000000000000000000000000000000000 (anchors: fake)\n\n"
            "Body claim.\n",
        )
        check("duplicate hash headers counted as ambiguous", preregister.preregistration_header_count(dup) == 2)

        skeleton = os.path.join(d, "skeleton.md")
        write(skeleton, template)
        proc = subprocess.run([sys.executable, preregister.__file__, skeleton], capture_output=True, text=True)
        check("decision-log skeleton carries priors dimensions", all(
            key in proc.stdout for key in ('"archetype"', '"market_scope"', '"redirect_pattern"')
        ))

        auto = os.path.join(d, "charter.md")
        auto_template = template.replace("build_authorized", "internal_planning_only")
        write(auto, auto_template)
        mvr_dir = os.path.join(d, "mvr")
        os.makedirs(mvr_dir, exist_ok=True)
        brief = "Build an internal planning prototype for a simple record ledger."
        write(os.path.join(mvr_dir, "user-brief.txt"), brief)
        claims, coverage = twin_claim_coverage.build_coverage(
            brief,
            {"kind": "file", "path": "mvr/user-brief.txt"},
            ["simple record ledger"],
            "record-ledger",
        )
        with open(os.path.join(mvr_dir, "committee_packet.json"), "w", encoding="utf-8") as handle:
            json.dump({
                "provisional": False,
                "claims_sent": claims,
                "claim_coverage": coverage,
                "kernel_receipts": {"immutable_audit_hash": "a" * 64},
            }, handle)
        with open(os.path.join(mvr_dir, "decision-log.json"), "w", encoding="utf-8") as handle:
            json.dump([{
                "charter_ref": "charter.md",
                "verdict": "internal_planning_only",
                "decision_authorization": {"authorized_use": ["internal_planning"]},
                "kernel_receipts": {"immutable_audit_hash": "a" * 64},
            }], handle)
        proc = subprocess.run(
            [sys.executable, preregister.__file__, "--in-place", auto],
            capture_output=True,
            text=True,
        )
        check("in-place preregistration emits build contract",
              proc.returncode == 0 and os.path.exists(os.path.join(d, "mvr", "build_spec.json")), proc.stderr)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        raise SystemExit(1)
    print("ALL PASS - preregistration contract verified.")


if __name__ == "__main__":
    main()
