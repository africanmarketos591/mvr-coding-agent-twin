"""Kernel context wrappers and measured Law 6 calibration scope."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "spine"))
import mvr_client as client  # noqa: E402


FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    home = client.calibration_scope_from_response({
        "response_meta": {"country_calibration_scope": {"coverage_tier": "africa_home_market"}}
    })
    global_scope = client.calibration_scope_from_response({
        "response_meta": {"country_calibration_scope": {"coverage_tier": "global_provisional_high_context"}}
    })
    unknown = client.calibration_scope_from_response({})
    check("Africa home tier is calibrated", home["verdict"] == "calibrated")
    check("global provisional tier triggers Law 6", global_scope["verdict"] == "uncalibrated" and "lens-only" in global_scope["boundary"])
    check("missing kernel scope remains unknown", unknown["verdict"] == "unknown")

    old_call, old_update, old_decision = client.call, client.update_state, client.decision_check
    calls = []
    try:
        client.update_state = lambda *args, **kwargs: None
        client.call = lambda path, *args, **kwargs: (calls.append((path, args, kwargs)) or (0.01, 200, {"ok": True}))
        client.calibration_health()
        client.market_profile("ke", "Nairobi CBD")
        client.market_calendar("ug")
        paths = [item[0] for item in calls]
        check("calibration health route wired", "/v1/calibration-health" in paths)
        check("market zone is URL-safe", "/v1/market-profile/KE/Nairobi%20CBD" in paths)
        check("market calendar route wired", "/v1/market-calendar/UG" in paths)

        captured = {}
        def fake_decision(payload):
            captured.update(payload)
            return 0.01, 200, {"response_meta": {}}
        client.decision_check = fake_decision
        client.calibration_probe("Case", "fintech_platform", "ke")
        check("calibration probe uses actual subject", captured["subject"]["entity_name"] == "Case")
        check("calibration probe normalizes country", captured["market_scope"]["country"] == "KE")
        check("calibration probe carries no invented evidence", captured["compiled_pack"] == {"public_reality_pack": [], "telemetry_proxy_pack": []})
    finally:
        client.call, client.update_state, client.decision_check = old_call, old_update, old_decision

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - kernel context and calibration-scope contracts verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
