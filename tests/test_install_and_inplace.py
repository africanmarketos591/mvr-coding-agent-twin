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
        cursor_rule = os.path.join(d, ".cursor", "rules", "mvr-twin.mdc")
        cursor_hooks = os.path.join(d, ".cursor", "hooks.json")
        cursor_mcp = os.path.join(d, ".cursor", "mcp.json")
        check("Cursor rule installed", os.path.exists(cursor_rule) and "MVR Twin" in open(cursor_rule, encoding="utf-8").read())
        hooks = json.load(open(cursor_hooks, encoding="utf-8"))
        check("Cursor preToolUse hook installed",
              any("pretooluse_claim_gate.py" in h.get("command", "") for h in hooks.get("hooks", {}).get("preToolUse", [])))
        check("Cursor heartbeat hook installed",
              any("before_submit_heartbeat.py" in h.get("command", "") for h in hooks.get("hooks", {}).get("beforeSubmitPrompt", [])))
        mcp = json.load(open(cursor_mcp, encoding="utf-8"))
        check("Cursor MCP config installed", mcp.get("mcpServers", {}).get("mvr", {}).get("url") == "https://africanmarketos.com/mcp")
        rc2, _ = run([os.path.join(PKG, "scripts", "install.py"), "--root", d])
        hooks2 = json.load(open(cursor_hooks, encoding="utf-8"))
        cursor_commands = [
            h.get("command", "")
            for entries in hooks2.get("hooks", {}).values()
            for h in entries
            if isinstance(h, dict)
        ]
        cursor_hook_count = sum(
            1 for command in cursor_commands
            if "pretooluse_claim_gate.py" in command or "before_submit_heartbeat.py" in command
        )
        check("install is idempotent", rc2 == 0 and open(hook).read().count("pre_commit_claim_gate.py") == 1 and cursor_hook_count == 2)

    # --- preregister --in-place ---
    with tempfile.TemporaryDirectory() as d:
        ch = os.path.join(d, "draft.md")
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
