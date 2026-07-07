"""Cursor beforeSubmitPrompt adapter for the MVR Twin heartbeat.

Where supported, this prepends the compact mvr/state.json digest to the prompt
Cursor sends the model. If a Cursor build ignores updated_input for this hook,
the adapter still fails open and the git gate remains authoritative.
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
        if (candidate / "hooks" / "heartbeat.py").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


def emit_allow(prompt=None):
    out = {"action": "allow"}
    if prompt is not None:
        out["updated_input"] = {"prompt": prompt}
    print(json.dumps(out))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit_allow()
        return
    root = project_dir(payload)
    pkg = package_dir(root)
    prompt = str(payload.get("prompt") or payload.get("input") or "")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    proc = subprocess.run(
        [sys.executable, str(pkg / "hooks" / "heartbeat.py")],
        capture_output=True,
        text=True,
        env=env,
    )
    context = ""
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            data = json.loads(proc.stdout)
            context = data.get("hookSpecificOutput", {}).get("additionalContext", "")
        except Exception:
            context = ""
    if context and prompt:
        emit_allow(context + "\n\n" + prompt)
    elif context:
        emit_allow(context)
    else:
        emit_allow()


if __name__ == "__main__":
    main()
