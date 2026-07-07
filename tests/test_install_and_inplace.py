"""Offline tests for install.py, preregister --in-place, and offline client degradation."""
import json, os, re, subprocess, sys, tempfile

PKG = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def run(args, cwd=None, env_extra=None):
    env = dict(os.environ, **(env_extra or {}))
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd, env=env)
    return p.returncode, p.stdout + p.stderr


def main():
    # --- install.py ---
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "-C", d, "init", "-q"], capture_output=True)
        rc, out = run([os.path.join(PKG, "scripts", "install.py"), "--root", d])
        check("install completes", rc == 0, out.strip().splitlines()[-1] if out else "")
        check("mvr/.gitignore installed", os.path.exists(os.path.join(d, "mvr", ".gitignore")))
        hook = os.path.join(d, ".git", "hooks", "pre-commit")
        check("pre-commit shim installed with sh shebang",
              os.path.exists(hook) and open(hook).read().startswith("#!/bin/sh"))
        check("shim wires the claim gate", "pre_commit_claim_gate.py" in open(hook).read())
        rc2, _ = run([os.path.join(PKG, "scripts", "install.py"), "--root", d])
        check("install is idempotent", rc2 == 0 and open(hook).read().count("pre_commit_claim_gate.py") == 1)

    # --- preregister --in-place ---
    with tempfile.TemporaryDirectory() as d:
        ch = os.path.join(d, "charter.md")
        open(ch, "w", encoding="utf-8").write(
            "# CH\n**Preregistration hash:** {{sha256}} (anchors: {{anchor_refs}})\n\nprediction text\n")
        rc, out = run([os.path.join(PKG, "scripts", "preregister.py"), "--in-place", ch])
        check("--in-place embeds and self-verifies", rc == 0 and "self-verified" in out)
        rc, out = run([os.path.join(PKG, "scripts", "preregister.py"), "--verify", ch])
        check("independent --verify passes after in-place", rc == 0)
        body = open(ch, encoding="utf-8").read()
        check("anchors marked pending, not fabricated", "anchors: pending" in body)

    # --- offline client degradation (Outage Rule, never a crash) ---
    code = (
        "import sys, os; sys.path.insert(0, r'%s');"
        "os.environ['MVR_API_KEY']='x'; os.environ['MVR_BASE_URL']='https://127.0.0.1:9';"
        "import mvr_client as c; lat, st, d = c.call('/v1/schema');"
        "print(st, d.get('error'), 'outage_rule' in d)" % os.path.join(PKG, "spine")
    )
    rc, out = run(["-c", code])
    check("offline spine degrades gracefully (no crash)", rc == 0, out.strip()[:80])
    check("offline returns kernel_unreachable + outage rule", "0 kernel_unreachable True" in out)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}"); sys.exit(1)
    print("ALL PASS - install / in-place / offline degradation verified.")


if __name__ == "__main__":
    main()
