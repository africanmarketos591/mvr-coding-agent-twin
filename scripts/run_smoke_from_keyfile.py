"""Run the live smoke test using a local internal key file without printing the key.

Usage:
  python scripts/run_smoke_from_keyfile.py path/to/keyfile.txt
"""
import os
import subprocess
import sys
from pathlib import Path

from keyfile_loader import extract_mvr_api_key


def main():
    if len(sys.argv) != 2:
        print("usage: run_smoke_from_keyfile.py <keyfile>")
        return 2

    keyfile = Path(sys.argv[1])
    text = keyfile.read_text(encoding="utf-8-sig")
    key = extract_mvr_api_key(text)

    env = os.environ.copy()
    env["MVR_API_KEY"] = key
    print(f"Loaded explicit key field from {keyfile} (redacted, length={len(key)}).")
    smoke = Path(__file__).resolve().parents[1] / "tests" / "smoke_test.py"
    return subprocess.call([sys.executable, str(smoke)], env=env)


if __name__ == "__main__":
    raise SystemExit(main())
