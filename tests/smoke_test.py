"""Live smoke test - MUST print ALL PASS before first use of the Twin.

Verifies: auth + liveness, playbook (pre-charter organ), sparring (skeptic seat incl.
overclaim tripwire), idea-stage decision-check (constant-abstention contract), latency
budget. Requires env MVR_API_KEY.
"""
import atexit, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spine"))
import mvr_client as spine

FAILS = []
SKIPS = []
_TEMP_PROJECT = None

if "CLAUDE_PROJECT_DIR" not in os.environ:
    _TEMP_PROJECT = tempfile.TemporaryDirectory()
    os.environ["CLAUDE_PROJECT_DIR"] = _TEMP_PROJECT.name
    atexit.register(_TEMP_PROJECT.cleanup)


def standard_scope_ok():
    key = os.environ.get("MVR_API_KEY", "").strip()
    return key == "mvr-demo-key-2026" or os.environ.get("MVR_ALLOW_STANDARD_SCOPE", "").strip() == "1"


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def skip(name, detail=""):
    print(f"SKIP  {name}  {detail}")
    SKIPS.append(name)


def latency_budget(name, cond, detail=""):
    """Latency is a budget, not a contract: single-call network jitter must never
    fail the deployment gate. WARN and continue; investigate if it warns repeatedly."""
    print(f"{'PASS' if cond else 'WARN'}  {name}  {detail}")


def main():
    lat, st, d = spine.schema()
    check("liveness+auth (/v1/schema)", st == 200 and "api_version" in d, f"{st} {lat}s v={d.get('api_version')}")

    lat, st, d = spine.category_playbook("fintech_platform")
    check("playbook returns demand schedule", st == 200 and "required_local_evidence" in d, f"{st} {lat}s")
    check("playbook has guardian map", isinstance(d.get("minimum_guardian_map"), list) and len(d["minimum_guardian_map"]) > 0)
    latency_budget("playbook latency < 3s", lat < 3, f"{lat}s")

    claims = [
        "Parents in Kampala need a dedicated school-fee app",
        "After a 3-school pilot the product is ready to scale across Uganda with no risk",
    ]
    lat, st, d = spine.strategy_sparring(
        claims,
        {"entity_name": "TwinSmoke", "entity_type": "company", "entity_archetype": "fintech_platform"},
        {"country": "UG", "region": "Kampala"},
    )
    if st == 403 and "Required plan" in str(d.get("message", "")):
        print(f"INFO  strategy-sparring plan gate  {d.get('message')}")
        if standard_scope_ok():
            print("INFO  STANDARD-scope sandbox verifies public-scope spine routes; full Twin smoke requires PRO/ENTERPRISE.")
            skip("strategy-sparring gated on STANDARD scope", d.get("message", ""))
        else:
            check("sparring challenge_ready", False, f"{st} {lat}s {d.get('message', '')}")
    else:
        check("sparring challenge_ready", st == 200 and d.get("status") == "challenge_ready", f"{st} {lat}s {d.get('message', '')}")
        unsafe = [u.get("claim", "") for u in d.get("unsafe_claims", [])]
        check("overclaim tripwire fires", any("no risk" in c for c in unsafe), f"unsafe={len(unsafe)}")
        check("evidence bill present", len(d.get("evidence_required", [])) > 0)
    latency_budget("sparring latency < 6s", lat < 6, f"{lat}s")

    idea = {
        "mode": "compiled_evidence", "case_type": "greenfield_entry",
        "subject": {"entity_name": "TwinSmoke", "entity_type": "company", "entity_archetype": "fintech_platform"},
        "market_scope": {"country": "UG", "region": "Kampala", "regulatory_velocity": "stable"},
        "stakeholder_scope": ["consumer", "guardian", "channel_gatekeeper", "distributor"],
        "analysis_date": "2026-07-06",
        "compiled_pack": {k: [] for k in [
            "public_reality_pack", "localized_observed_pack", "survey_pack", "retail_audit_pack",
            "ngo_program_pack", "evaluation_pack", "administrative_data_pack", "partner_network_pack",
            "social_listening_pack", "telemetry_proxy_pack"]},
    }
    lat, st, d = spine.decision_check(idea)
    codes = d.get("abstention_reason_codes") or []
    check("idea-stage abstains (constant-verdict contract)", st == 200 and len(codes) > 0, f"{st} {lat}s codes={codes[:3]}")
    auth = (d.get("decision_authorization") or {})
    check("internal_planning authorized at idea stage", "internal_planning" in (auth.get("authorized_use") or []))
    check("scale claims not authorized at idea stage", "national_rollout" in (auth.get("not_authorized_use") or []))
    scope = spine.calibration_scope_from_response(d)
    check("Law 6 calibration scope is kernel-measured", scope.get("coverage_tier") == "africa_home_market", scope)
    latency_budget("decision-check latency < 8s", lat < 8, f"{lat}s")

    lat, st, d = spine.calibration_health()
    check("calibration health route reachable", st == 200 and isinstance(d, dict), f"{st} {lat}s")

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    if SKIPS:
        print(f"STANDARD-SCOPE PASS - public-scope spine verified; skipped: {SKIPS}")
        print("Use a PRO/ENTERPRISE-scope key for full Twin committee verification.")
        return
    print("ALL PASS - Twin spine verified against live kernel.")


if __name__ == "__main__":
    main()
