"""Offline tests for the git pre-commit claim gate - host-agnostic authority."""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone

GATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hooks", "pre_commit_claim_gate.py"))
BUILD_SPEC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "twin_build_spec.py"))
sys.path.insert(0, os.path.dirname(BUILD_SPEC))
import twin_build_spec as build_spec  # noqa: E402
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def run_gate(repo):
    p = subprocess.run([sys.executable, GATE], capture_output=True, text=True, cwd=repo,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=repo))
    return p.returncode, p.stderr


def semantic_pass(repo, targets):
    contract = build_spec.load_contract(repo)
    request, _ = build_spec.write_review_request(repo, targets, contract)
    review = {
        "format": "mvr_semantic_code_review_v1",
        "request_sha256": request["request_sha256"],
        "reviewer_kind": "host_model",
        "reviewer_id": "precommit-test-session",
        "model_id": "precommit-test-model",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "pass",
        "findings": [],
        "attestation": "I reviewed behavior against every forbidden constraint in the request.",
    }
    with open(os.path.join(repo, build_spec.REVIEW_PATH), "w", encoding="utf-8") as handle:
        json.dump(review, handle)


def main():
    with tempfile.TemporaryDirectory() as d:
        git(d, "init", "-q")
        git(d, "config", "user.email", "t@t.t"); git(d, "config", "user.name", "t")

        # 1. Staged code only -> allowed
        os.makedirs(os.path.join(d, "src"), exist_ok=True)
        open(os.path.join(d, "src", "app.py"), "w").write("print('x')\n")
        git(d, "add", "src/app.py")
        rc, _ = run_gate(d)
        check("staged code never gated", rc == 0)

        # 2. Staged claim without log -> rejected
        os.makedirs(os.path.join(d, "claims"), exist_ok=True)
        open(os.path.join(d, "claims", "investor-deck.md"), "w").write("# deck\n")
        git(d, "add", "claims/investor-deck.md")
        rc, err = run_gate(d)
        check("staged claim blocked without log", rc == 1 and "decision-log.json does not exist" in err)

        # 2b. Claim-shaped document outside claims/ -> rejected before path evasion
        git(d, "reset", "-q")
        os.makedirs(os.path.join(d, "docs"), exist_ok=True)
        open(os.path.join(d, "docs", "parent-wallet-terms.md"), "w").write(
            "# Parent tuition savings wallet launch terms\n"
            "The app will hold parent deposits, run escrow, and launch to schools.\n"
        )
        git(d, "add", "docs/parent-wallet-terms.md")
        rc, err = run_gate(d)
        check("pre-commit blocks claim-shaped docs outside claims",
              rc == 1 and "outside claims/" in err and "national_rollout" in err)

        # 2c. Ordinary documentation still commits without a decision log
        git(d, "reset", "-q")
        open(os.path.join(d, "docs", "architecture-note.md"), "w").write(
            "# Architecture\nInternal attendance scorecard data flow only.\n"
        )
        git(d, "add", "docs/architecture-note.md")
        rc, _ = run_gate(d)
        check("pre-commit allows ordinary docs outside claims", rc == 0)

        # 2d. Renamed Twin artifacts and skip-zone lookalikes are not safe when nested
        for rel in ("docs/charter.md", "twin/notes.md", "mvr/deck.md"):
            git(d, "reset", "-q")
            full = os.path.join(d, *rel.split("/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            open(full, "w").write(
                "Fundraising KES 200M at a KES 2B valuation. "
                "Pitch deck, investment memo, capital allocation to national rollout.\n"
            )
            git(d, "add", rel)
            rc, err = run_gate(d)
            check(f"pre-commit blocks renamed bypass {rel}",
                  rc == 1 and "outside claims/" in err and "capital_allocation" in err)

        # 3. Unauthorized -> rejected with gaps
        git(d, "reset", "-q")
        git(d, "add", "claims/investor-deck.md")
        os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
        json.dump([{"entry_id": "DL-1", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "decision_authorization": {"authorized_use": ["internal_planning"], "not_authorized_use": ["capital_allocation"]},
                    "evidence_gaps": ["guardian_or_regulatory_evidence"]}],
                  open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        rc, err = run_gate(d)
        check("unauthorized staged claim rejected", rc == 1 and "capital_allocation" in err and "guardian" in err)

        # 4. Authorized -> commit allowed, receipt written
        json.dump([{"entry_id": "DL-2", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []}}],
                  open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        rc, _ = run_gate(d)
        events = [json.loads(x) for x in open(os.path.join(d, "mvr", "gate-events.jsonl"), encoding="utf-8") if x.strip()]
        check("authorized staged claim allowed", rc == 0)
        check("pre-commit decisions receipted", any(e.get("tool") == "git-pre-commit" and e.get("event") == "allow_claim" for e in events))

        # 5. Ambiguous hand-edited local authorization beyond kernel baseline -> rejected
        json.dump([{"entry_id": "DL-3", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "kernel_authorized_use": ["internal_planning"],
                    "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []}}],
                  open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        rc, err = run_gate(d)
        check("pre-commit rejects ambiguous local authorization",
              rc == 1 and "not in kernel_authorized_use" in err)

        # 6. Explicit named-human override -> allowed but receipted as override, not kernel allow
        json.dump([{"entry_id": "DL-4", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "kernel_authorized_use": ["internal_planning"],
                    "authorization_basis": "named_human_override",
                    "decision_authorization": {"authorized_use": ["capital_allocation"], "not_authorized_use": []},
                    "human_review": {"required": True, "reviewer": "test_reviewer", "signature_ref": "sig-test"},
                    "override_note": "Local-only override for test; kernel did not authorize this claim class."}],
                  open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        rc, _ = run_gate(d)
        events = [json.loads(x) for x in open(os.path.join(d, "mvr", "gate-events.jsonl"), encoding="utf-8") if x.strip()]
        check("pre-commit explicit override allowed", rc == 0)
        check("pre-commit override receipted distinctly",
              any(e.get("tool") == "git-pre-commit" and e.get("event") == "allow_override_claim" and e.get("entry_id") == "DL-4" for e in events))

    # The build-constraint contract and semantic review are mandatory once a Twin case and code coexist.
    with tempfile.TemporaryDirectory() as d:
        git(d, "init", "-q")
        git(d, "config", "user.email", "t@t.t"); git(d, "config", "user.name", "t")
        os.makedirs(os.path.join(d, "src"), exist_ok=True)
        os.makedirs(os.path.join(d, "mvr"), exist_ok=True)
        open(os.path.join(d, "charter.md"), "w").write(
            "# Charter\n**Status:** redirect\n## 5. THE BUILD\n"
            "- **Build:** a wage ledger.\n"
            "- **Explicitly NOT building:** a digital loan book.\n"
        )
        open(os.path.join(d, "src", "app.py"), "w").write("def ledger(): return True\n")
        json.dump([{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_authorization": {
                "authorized_use": ["internal_planning"],
                "not_authorized_use": ["national_rollout"],
            },
            "kernel_receipts": {"immutable_audit_hash": "a" * 64},
        }], open(os.path.join(d, "mvr", "decision-log.json"), "w"))
        json.dump({"provisional": False, "claims_sent": ["digital loans"]},
                  open(os.path.join(d, "mvr", "committee_packet.json"), "w"))
        git(d, "add", "charter.md", "src/app.py", "mvr/decision-log.json", "mvr/committee_packet.json")
        rc, err = run_gate(d)
        check("code plus charter requires build contract", rc == 1 and "build_spec.json is missing" in err)

        emitted = subprocess.run(
            [sys.executable, BUILD_SPEC, "--root", d, "--emit"],
            capture_output=True, text=True,
        )
        semantic_pass(d, ["src/app.py"])
        git(d, "add", "mvr/build_spec.json", "mvr/build-contract-history.jsonl",
            "mvr/semantic-review-request.json", "mvr/semantic-review.json")
        rc, err = run_gate(d)
        check("current build contract permits fitted code", emitted.returncode == 0 and rc == 0, err)

        open(os.path.join(d, "src", "app.py"), "w").write(
            "def approve_loan(user): return issue_loan(user)\n"
        )
        git(d, "add", "src/app.py")
        rc, err = run_gate(d)
        check("tripwire blocks obvious redirected capability at commit", rc == 1 and "digital_lending" in err)

        open(os.path.join(d, "src", "app.py"), "w").write("def ledger(): return True\n")
        open(os.path.join(d, "charter.md"), "a").write("Changed constraint.\n")
        git(d, "add", "charter.md", "src/app.py")
        rc, err = run_gate(d)
        check("stale build contract blocks code", rc == 1 and "no longer matches" in err)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}"); sys.exit(1)
    print("ALL PASS - pre-commit gate contract verified.")


if __name__ == "__main__":
    main()
