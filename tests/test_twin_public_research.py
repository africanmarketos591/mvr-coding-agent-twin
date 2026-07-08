"""Tests for scripts/twin_public_research.py."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_public_research.py")
FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        result = run(
            "--root",
            tempdir,
            "--init",
            "--idea",
            "Boda savings wallet",
            "--country",
            "UG",
            "--archetype",
            "fintech_lending",
        )
        check("init exits 0", result.returncode == 0, result.stderr[:120])
        ledger_path = os.path.join(tempdir, "mvr", "public_research", "source_ledger.json")
        todo_path = os.path.join(tempdir, "mvr", "public_research", "PUBLIC_RESEARCH.md")
        check("ledger written", os.path.exists(ledger_path))
        check("research todo written", os.path.exists(todo_path))
        todo = open(todo_path, encoding="utf-8").read()
        check("todo instructs browser/search research", "Use browser/search tools" in todo)

        result = run("--validate", "--ledger", ledger_path)
        check("unknown-only skeleton validates with warning", result.returncode == 0 and "WARN" in result.stdout)

        ledger = json.load(open(ledger_path, encoding="utf-8"))
        ledger["entries"][0].update(
            {
                "claim": "Example incumbent exists",
                "claim_class": "incumbent",
                "source_name": "Example",
                "source_type": "company",
                "url": "https://example.com",
                "access_date": "2026-07-08",
                "status": "verified",
                "used_for": "eclipse",
                "notes": "public page",
            }
        )
        with open(ledger_path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)
        result = run("--validate", "--ledger", ledger_path)
        check("verified http source validates", result.returncode == 0 and "OK" in result.stdout)

        ledger["entries"][0].update(
            {
                "claim": "A payment licence requires UGX 250M capital.",
                "claim_class": "licence_cost",
                "source_type": "news",
                "source_name": "Practitioner blog",
                "url": "https://example.com/blog",
                "access_date": "2026-07-08",
                "status": "verified",
            }
        )
        with open(ledger_path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)
        result = run("--validate", "--ledger", ledger_path)
        check("verified licence cost requires authority-grade source", result.returncode == 1 and "source_type must" in result.stdout)

        ledger["entries"][0]["source_type"] = "regulator"
        with open(ledger_path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)
        result = run("--validate", "--ledger", ledger_path)
        check("authority-grade licence source validates", result.returncode == 0 and "OK" in result.stdout)

        ledger["entries"][0]["url"] = "not-a-url"
        with open(ledger_path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)
        result = run("--validate", "--ledger", ledger_path)
        check("verified non-url rejected", result.returncode == 1 and "must be http" in result.stdout)

        del ledger["entries"][0]["access_date"]
        with open(ledger_path, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle)
        result = run("--validate", "--ledger", ledger_path)
        check("missing access date rejected", result.returncode == 1 and "missing access_date" in result.stdout)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        sys.exit(1)
    print("ALL PASS - public research pack validates source/date/status discipline.")


if __name__ == "__main__":
    main()
