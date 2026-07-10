"""Offline tests for the one-command committee orchestrator."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "spine"))

import twin_committee as T  # noqa: E402

FAILS = []


PLAYBOOK_A = {
    "minimum_guardian_map": [{"guardian_tier": "macro_regulator"}],
    "required_local_evidence": [
        {"stakeholder_class": "farmer", "minimum_signal_count": 25, "required_fields": ["trust"]}
    ],
    "board_questions": ["Which localized stakeholders can block adoption?"],
}
PLAYBOOK_B = {
    "minimum_guardian_map": [{"guardian_tier": "macro_regulator"}, {"guardian_tier": "meso_community"}],
    "required_local_evidence": [
        {"stakeholder_class": "farmer", "minimum_signal_count": 100, "required_fields": ["repeat_order"]}
    ],
    "board_questions": ["Which rail owner can veto the build?"],
}
SPARRING = {
    "unsafe_claims": [],
    "evidence_required": ["Missing core pack types: public_reality_pack"],
    "abstention_reason_codes": ["guardian_or_regulatory_evidence"],
    "immutable_audit_hash": "a" * 64,
    "response_hash": "b" * 64,
}
CALIBRATED = {
    "response_meta": {"country_calibration_scope": {"coverage_tier": "africa_home_market"}},
    "immutable_audit_hash": "c" * 64,
}


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    lanes = T.union_evidence([
        {"required_local_evidence": [{"stakeholder_class": "x", "minimum_signal_count": 10}]},
        {"required_local_evidence": [{"stakeholder_class": "x", "minimum_signal_count": 100}]},
    ])
    check("union takes higher minimum", lanes[0]["minimum_signal_count"] == 100)

    T.c.schema = lambda: (0.1, 200, {"api_version": "v6.32.0"})
    T.c.calibration_probe = lambda subject, archetype, country: (0.1, 200, CALIBRATED)
    T.c.category_playbook = lambda archetype: (0.1, 200, PLAYBOOK_A if archetype == "a" else PLAYBOOK_B)
    T.c.strategy_sparring = lambda claims, subject, market: (0.1, 200, SPARRING)

    with tempfile.TemporaryDirectory() as tempdir:
        old_argv = sys.argv[:]
        sys.argv = [
            "twin_committee.py",
            "--root",
            tempdir,
            "--idea",
            "test idea",
            "--archetype",
            "a",
            "--archetype",
            "b",
            "--subject",
            "subject",
            "--market",
            "UG-KE",
            "--claim",
            "claim one",
        ]
        try:
            T.main()
        finally:
            sys.argv = old_argv

        packet_path = os.path.join(tempdir, "mvr", "committee_packet.json")
        seed_path = os.path.join(tempdir, "mvr", "decision-log.seed.json")
        draft_path = os.path.join(tempdir, "charter.draft.md")
        packet = json.load(open(packet_path, encoding="utf-8"))
        seed = json.load(open(seed_path, encoding="utf-8"))[0]
        draft = open(draft_path, encoding="utf-8").read()

        check("packet written", os.path.exists(packet_path))
        check("not provisional when kernel up", packet["provisional"] is False)
        check("guardian map deduped", [g["guardian_tier"] for g in packet["guardian_map"]] == ["macro_regulator", "meso_community"])
        check("abstention captured", packet["sparring"]["abstention_reason_codes"] == ["guardian_or_regulatory_evidence"])
        check("receipts captured", packet["kernel_receipts"].get("immutable_audit_hash") == "a" * 64)
        check("calibration is kernel-measured", packet["calibration_scope"]["coverage_tier"] == "africa_home_market")
        check("seed carries priors dims", seed["market_scope"] == "UG-KE" and seed["archetype"] == "a")
        check("seed remains internal planning only", seed["decision_authorization"]["authorized_use"] == ["internal_planning"])
        check("draft leaves judgment to model", "{MODEL" in draft and "test idea" in draft)
        check("live draft exposes normal statuses", "{pilot_only|build_authorized|redirected}" in draft)
        check("evidence bill takes higher lane", ">=100 signals" in draft)

    # Outage path: no exception, provisional packet, still no claim authorization.
    T.c.schema = lambda: (0.1, 0, {"error": "kernel_unreachable"})
    T.c.calibration_probe = lambda subject, archetype, country: (0.1, 0, {"error": "kernel_unreachable"})
    T.c.category_playbook = lambda archetype: (0.1, 0, {"error": "kernel_unreachable"})
    T.c.strategy_sparring = lambda claims, subject, market: (0.1, 0, {"error": "kernel_unreachable"})
    with tempfile.TemporaryDirectory() as tempdir:
        old_argv = sys.argv[:]
        sys.argv = [
            "twin_committee.py",
            "--root",
            tempdir,
            "--idea",
            "offline idea",
            "--archetype",
            "a",
            "--subject",
            "subject",
            "--market",
            "UG",
        ]
        try:
            T.main()
        finally:
            sys.argv = old_argv
        packet = json.load(open(os.path.join(tempdir, "mvr", "committee_packet.json"), encoding="utf-8"))
        seed = json.load(open(os.path.join(tempdir, "mvr", "decision-log.seed.json"), encoding="utf-8"))[0]
        draft = open(os.path.join(tempdir, "charter.draft.md"), encoding="utf-8").read()
        check("outage packet is provisional", packet["provisional"] is True)
        check("outage seed still denies claims", "national_rollout" in seed["decision_authorization"]["not_authorized_use"])
        check("outage draft cannot mark build authorized", "provisional_not_authorized" in draft and "build_authorized" not in draft.splitlines()[2])
        check("outage draft warns regulated scaffolds", "regulated implementation details" in draft)

    # Law 6 path: reachable spine, but outside calibrated market scope.
    T.c.schema = lambda: (0.1, 200, {"api_version": "v6.32.0"})
    T.c.calibration_probe = lambda subject, archetype, country: (
        0.1, 200,
        {"response_meta": {"country_calibration_scope": {"coverage_tier": "global_provisional_high_context"}},
         "immutable_audit_hash": "d" * 64},
    )
    T.c.category_playbook = lambda archetype: (0.1, 200, PLAYBOOK_A)
    T.c.strategy_sparring = lambda claims, subject, market: (0.1, 200, SPARRING)
    with tempfile.TemporaryDirectory() as tempdir:
        old_argv = sys.argv[:]
        sys.argv = [
            "twin_committee.py", "--root", tempdir, "--idea", "German fleet tool",
            "--archetype", "a", "--subject", "subject", "--market", "DE/Berlin",
        ]
        try:
            T.main()
        finally:
            sys.argv = old_argv
        packet = json.load(open(os.path.join(tempdir, "mvr", "committee_packet.json"), encoding="utf-8"))
        seed = json.load(open(os.path.join(tempdir, "mvr", "decision-log.seed.json"), encoding="utf-8"))[0]
        draft = open(os.path.join(tempdir, "charter.draft.md"), encoding="utf-8").read()
        check("uncalibrated market is measured, not outage", packet["provisional"] is False and packet["calibration_scope"]["verdict"] == "uncalibrated")
        check("uncalibrated seed is explicit", seed["verdict"] == "uncalibrated")
        check("uncalibrated draft is lens-only", "uncalibrated_lens_only" in draft and "LAW 6" in draft)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - one-command committee plumbing verified.")


if __name__ == "__main__":
    main()
