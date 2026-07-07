"""One-command Twin install - kills first-run friction (the contagion killer).

Usage, from the PROJECT ROOT (the repo the developer is building in):
  python <twin-package>/scripts/install.py [--verify]

Does, idempotently and Windows-safely:
  1. mvr/.gitignore from templates/mvr.gitignore (passport-leak prevention, REQUIRED).
  2. .git/hooks/pre-commit shim (sh shebang; correct on Git-for-Windows and POSIX)
     invoking hooks/pre_commit_claim_gate.py - host-agnostic claim authority.
  3. Prints the Claude Code settings-hooks merge instruction (harness-level channel).
  4. --verify: runs the offline suite set and reports PASS/FAIL per suite.

An installer that does not verify is a liability; use --verify on first install.
Never touches keys. Never contacts the network.
"""
import argparse
import os
import shutil
import subprocess
import sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rel_to_root(path, root):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path  # different drive - absolute path is fine in the shim


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Run offline suites after install.")
    parser.add_argument("--root", default=os.getcwd(), help="Project root (default: cwd).")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    ok = True

    # 1. mvr/.gitignore
    mvr_dir = os.path.join(root, "mvr")
    os.makedirs(mvr_dir, exist_ok=True)
    src = os.path.join(PKG, "templates", "mvr.gitignore")
    dst = os.path.join(mvr_dir, ".gitignore")
    if os.path.exists(dst):
        print(f"OK    mvr/.gitignore already present (left untouched)")
    else:
        shutil.copy2(src, dst)
        print(f"DONE  mvr/.gitignore installed (passport-leak prevention)")

    # 2. git pre-commit shim
    hooks_dir = os.path.join(root, ".git", "hooks")
    if not os.path.isdir(hooks_dir):
        print("WARN  no .git/hooks here - run 'git init' first, then rerun install for the commit gate.")
        ok = False
    else:
        gate = rel_to_root(os.path.join(PKG, "hooks", "pre_commit_claim_gate.py"), root).replace("\\", "/")
        shim_path = os.path.join(hooks_dir, "pre-commit")
        shim_line = f'python "{gate}" || exit 1'
        if os.path.exists(shim_path):
            existing = open(shim_path, encoding="utf-8", errors="replace").read()
            if "pre_commit_claim_gate.py" in existing:
                print("OK    pre-commit hook already wires the claim gate (left untouched)")
            else:
                with open(shim_path, "a", encoding="utf-8", newline="\n") as f:
                    f.write("\n" + shim_line + "\n")
                print("DONE  claim gate appended to existing pre-commit hook")
        else:
            with open(shim_path, "w", encoding="utf-8", newline="\n") as f:
                f.write("#!/bin/sh\n" + shim_line + "\n")
            try:
                os.chmod(shim_path, 0o755)
            except Exception:
                pass  # Windows: git honors the shebang regardless
            print("DONE  .git/hooks/pre-commit installed (sh shebang, Windows-safe)")

    # 3. Harness hooks instruction (cannot be merged automatically without clobber risk)
    print("NEXT  Claude Code hosts: merge the 'hooks' block from settings-hooks.json into .claude/settings.json")
    print("      Other hosts: see adapters/ for your host's wiring; the git gate above already enforces claims.")

    # 4. Optional verification
    if args.verify:
        tests_dir = os.path.join(PKG, "tests")
        offline = [t for t in sorted(os.listdir(tests_dir))
                   if t.startswith("test_") and t.endswith(".py")]
        print(f"\nVERIFY: running {len(offline)} offline suites...")
        for t in offline:
            p = subprocess.run([sys.executable, os.path.join(tests_dir, t)],
                               capture_output=True, text=True)
            tail = (p.stdout.strip().splitlines() or ["(no output)"])[-1]
            print(f"  {'PASS' if p.returncode == 0 else 'FAIL'}  {t}: {tail}")
            if p.returncode != 0:
                ok = False

    print("\n" + ("INSTALL COMPLETE - the Twin is wired." if ok else "INSTALL INCOMPLETE - resolve WARN/FAIL lines above."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
