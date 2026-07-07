"""Cursor preToolUse adapter for the MVR Twin claim gate.

Cursor hook payloads are normalized into the same stdin contract used by
hooks/claim_gate.py. The git pre-commit gate remains the universal fallback;
this adapter gives Cursor users earlier write-time feedback where their Cursor
version fires preToolUse for write/edit tools.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def project_dir(payload):
    for key in ("CURSOR_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        value = os.environ.get(key)
        if value:
            return value
    roots = payload.get("workspace_roots")
    if isinstance(roots, list) and roots:
        return str(roots[0])
    return os.getcwd()


def package_dir(root):
    candidates = [
        Path(root) / "mvr-coding-agent-twin",
        Path(root) / "mvr-twin",
        Path(__file__).resolve().parents[2],
    ]
    for candidate in candidates:
        if (candidate / "hooks" / "claim_gate.py").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


def emit(action, message=None):
    out = {"action": action}
    if message:
        out["message"] = message
    print(json.dumps(out))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit("allow")
        return
    root = project_dir(payload)
    pkg = package_dir(root)
    normalized = {
        "tool_name": payload.get("tool_name") or payload.get("toolName") or payload.get("name") or "",
        "tool_input": payload.get("tool_input") or payload.get("toolInput") or payload.get("input") or {},
    }
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    proc = subprocess.run(
        [sys.executable, str(pkg / "hooks" / "claim_gate.py")],
        input=json.dumps(normalized),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode == 2:
        emit("deny", proc.stderr.strip() or "MVR claim gate blocked this write.")
        return
    if proc.returncode not in (0, 2):
        # Cursor write-time counsel should not brick the session on adapter errors.
        emit("allow", "MVR claim gate adapter warning: hook error; git pre-commit gate remains active.")
        return
    emit("allow")


if __name__ == "__main__":
    main()
