"""Tests for the cheap pre-code preflight reflex."""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_preflight.py")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import twin_preflight as P  # noqa: E402

FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def main():
    queries = P.eclipse_queries("auto-save app for boda riders", "UG")
    check("eclipse queries mention country", any("UG" in query for query in queries))
    check("eclipse queries carry generation test", any("AI can generate" in query for query in queries))

    with tempfile.TemporaryDirectory() as tempdir:
        out = os.path.join(tempdir, "PREFLIGHT.md")
        env = dict(os.environ, MVR_API_KEY="x", MVR_BASE_URL="https://127.0.0.1:9")
        result = subprocess.run(
            [
                sys.executable,
                SCRIPT,
                "--root",
                tempdir,
                "--idea",
                "boda auto-save, loans, and insurance",
                "--archetype",
                "fintech_lending",
                "--country",
                "UG",
                "--out",
                out,
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        check("runs clean offline", result.returncode == 0, result.stderr[:120])
        check("preflight written", os.path.exists(out))
        body = open(out, encoding="utf-8").read()
        for token in ("ECLIPSE", "PERMISSION", "RAILS", "0.30", "Do not proceed"):
            check(f"card contains {token}", token in body)
        check("card pushes public research pack", "twin_public_research.py --init" in body)
        check("offline names guardian tiers", "macro_regulator" in body)
        check("offline does not authorize", "does not authorize claims" in body)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - preflight writes the pre-code reasoning brake.")


if __name__ == "__main__":
    main()
