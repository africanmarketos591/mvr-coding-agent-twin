"""Offline tests for outcome feedback bridge, receipt helper, and egress scanner."""
import json
import os
import subprocess
import sys
import tempfile


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "hooks"))
sys.path.insert(0, os.path.join(ROOT, "adapters"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def settled_log(directory):
    mvr = os.path.join(directory, "mvr")
    os.makedirs(mvr, exist_ok=True)
    path = os.path.join(mvr, "decision-log.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump([
            {
                "entry_id": "DL-1",
                "charter_ref": "charter.md",
                "charter_hash": "a" * 64,
                "archetype": "agritech_aggregator",
                "market_scope": "UG-KE",
                "verdict": "permission_not_yet_earned",
            },
            {
                "entry_id": "SET-1",
                "entry_type": "settlement",
                "charter_ref": "charter.md",
                "timestamp": "2026-10-06T00:00:00+00:00",
                "settlement": {"outcome": "miss", "summary": "no orders honoured", "sources": []},
            },
        ], handle)
    return path


def main():
    import submit_outcome_feedback as feedback  # noqa: E402

    with tempfile.TemporaryDirectory() as directory:
        log = settled_log(directory)
        entries = json.load(open(log, encoding="utf-8"))
        payload = feedback.build_payload(entries, entries[-1], "EastAgriGate", None)
        check("bridge builds a contract-valid payload", feedback.missing_required(payload) == [], str(feedback.missing_required(payload)))
        missing = feedback.missing_required({
            "entity_name": "x",
            "predicted_verdict": "v",
            "outcome_date": "2026-01-01",
        })
        check("bridge fails payload missing outcome", "actual_outcome" in missing)
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "submit_outcome_feedback.py"), "--log", log, "--entity", "EastAgriGate"],
            capture_output=True,
            text=True,
        )
        check("dry-run is default and exits clean", proc.returncode == 0 and "DRY-RUN" in proc.stdout)

    import verify_authorizing_receipt as verifier  # noqa: E402

    ledger = {"a" * 64}
    verifier.c.call = lambda path, **kwargs: (
        (0.0, 200, {"status": "verified"})
        if path.rsplit("/", 1)[-1] in ledger
        else (0.0, 404, {"status": "unverified"})
    )

    def mk(receipts):
        directory = tempfile.mkdtemp()
        mvr = os.path.join(directory, "mvr")
        os.makedirs(mvr)
        with open(os.path.join(mvr, "decision-log.json"), "w", encoding="utf-8") as handle:
            json.dump([{"entry_id": "DL-1", "kernel_receipts": receipts}], handle)
        return directory

    old_key = os.environ.get("MVR_API_KEY")
    try:
        os.environ["MVR_API_KEY"] = "test-key"
        check("real receipt verifies", verifier.authorizing_receipt_status(mk({"immutable_audit_hash": "a" * 64}))[0] == "verified")
        check(
            "descriptive sparring receipt verifies",
            verifier.authorizing_receipt_status(mk({"strategy_sparring_immutable_receipt_hash": "a" * 64}))[0] == "verified",
        )
        check(
            "content hash alone is not authority",
            verifier.authorizing_receipt_status(mk({"stable_content_hash": "a" * 64}))[0] == "no_receipt",
        )
        check("forged receipt is caught", verifier.authorizing_receipt_status(mk({"immutable_audit_hash": "f" * 64}))[0] == "unverified")
        check("no-receipt entry is explicit", verifier.authorizing_receipt_status(mk({}))[0] == "no_receipt")
        verifier.c.call = lambda path, **kwargs: (0.0, 0, {"error": "kernel_unreachable"})
        check("offline is a distinct state", verifier.authorizing_receipt_status(mk({"immutable_audit_hash": "a" * 64}))[0] == "offline")
    finally:
        if old_key is None:
            os.environ.pop("MVR_API_KEY", None)
        else:
            os.environ["MVR_API_KEY"] = old_key
    check("missing key is a clean state", verifier.authorizing_receipt_status(mk({"immutable_audit_hash": "a" * 64}))[0] == "no_key")

    import egress_scanner as egress  # noqa: E402

    check("egress blocks keyword claim", egress.scan_egress("national escrow wallet at rollout", mode="block")["action"] == "block")
    check(
        "egress blocks semantic paraphrase",
        egress.scan_egress("we hold members money in trust until dispatch", mode="block")["tier"] == "semantic",
    )
    check("egress allows benign", egress.scan_egress("internal data model design", mode="block")["action"] == "allow")
    check("advisory mode flags but does not block", egress.scan_egress("national escrow wallet at rollout")["action"] == "flag")
    check("guard refuses a claim send", egress.guard("national escrow wallet at rollout") is False and egress.guard("data model") is True)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - outcome bridge, receipt helper, and egress scanner verified.")


if __name__ == "__main__":
    main()
