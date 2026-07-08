"""Tests for instrument-by-default product telemetry."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KIT = os.path.join(ROOT, "adapters", "product_kit", "mvr_telemetry.py")

spec = importlib.util.spec_from_file_location("mvr_telemetry", KIT)
mvr_telemetry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mvr_telemetry)
MVRTelemetry = mvr_telemetry.MVRTelemetry
ConsentError = mvr_telemetry.ConsentError

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        buffer = os.path.join(tempdir, "buffer.jsonl")
        tel = MVRTelemetry(
            "pilot",
            {"country": "UG", "city": "Tororo", "town_or_zone": "central"},
            "consent",
            buffer_path=buffer,
        )
        tel.observe("orders_placed_rate", 42)
        tel.observe("orders_honored_rate", 0.5)

        try:
            MVRTelemetry("bad", {"country": "UG"}, "made_up")
            check("bad consent rejected", False)
        except ConsentError:
            check("bad consent rejected", True)

        try:
            tel.observe("customer_email", 10)
            check("PII metric rejected", False)
        except ConsentError:
            check("PII metric rejected", True)

        try:
            tel.observe("orders", 420)
            check("out-of-range rejected", False)
        except ValueError:
            check("out-of-range rejected", True)

        payload = tel.pack()
        check("payload has telemetry_data", "structured_values" in payload["telemetry_data"])
        check("payload has evidence_geography", payload["evidence_geography"]["country"] == "UG")
        check("payload has privacy envelope", payload["privacy_envelope"]["redaction_status"] == "aggregated")
        check("fraction scaled", payload["telemetry_data"]["structured_values"]["orders_honored_rate"] == 50.0)
        check("source class is capped telemetry", payload["source_class"] == "telemetry_internal")
        check("silence detector works", tel.seconds_since_last() is not None)

    with tempfile.TemporaryDirectory() as tempdir:
        product = os.path.join(tempdir, "product")
        result = subprocess.run(
            [
                sys.executable,
                os.path.join(ROOT, "scripts", "twin_instrument.py"),
                "--root",
                product,
                "--project-id",
                "pilot",
                "--country",
                "UG",
                "--city",
                "Tororo",
                "--map",
                "orders_placed_rate:t+90d >=3 unions place an aggregate order",
            ],
            capture_output=True,
            text=True,
        )
        check("instrument exits 0", result.returncode == 0, result.stderr)
        check("kit dropped", os.path.exists(os.path.join(product, "mvr_telemetry.py")))
        check("settlement map written", os.path.exists(os.path.join(product, "mvr", "settlement_map.json")))
        check("instrumentation doc written", os.path.exists(os.path.join(product, "INSTRUMENTATION.md")))

        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "twin_settlement_read.py"), "--root", product],
            capture_output=True,
            text=True,
        )
        check("silent product presumed dead", result.returncode == 0 and "presumed_dead" in result.stdout)

        product_kit = os.path.join(product, "mvr_telemetry.py")
        spec = importlib.util.spec_from_file_location("product_mvr_telemetry", product_kit)
        product_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(product_module)
        tel = product_module.MVRTelemetry(
            "pilot",
            {"country": "UG"},
            "consent",
            buffer_path=os.path.join(product, "mvr_telemetry.buffer.jsonl"),
        )
        tel.observe("orders_placed_rate", 55)
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "twin_settlement_read.py"), "--root", product],
            capture_output=True,
            text=True,
        )
        draft = json.load(open(os.path.join(product, "mvr", "settlement-draft.json"), encoding="utf-8"))
        check("usage gives leading life", "leading_life_needs_corroboration" in result.stdout)
        check("draft never settles", draft["draft"] is True and draft["settled"] is None)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - instrument-by-default loop verified.")


if __name__ == "__main__":
    main()
