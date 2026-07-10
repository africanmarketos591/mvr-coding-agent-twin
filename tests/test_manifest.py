"""Offline tests for strict manifest generation."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import generate_manifest


FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "VERSION"), "w", encoding="utf-8").write("test-version\n")
        open(os.path.join(d, "README.md"), "w", encoding="utf-8").write("# Demo\n")
        os.makedirs(os.path.join(d, "mvr"))
        open(os.path.join(d, "mvr", "state.json"), "w", encoding="utf-8").write("{}\n")
        out = os.path.join(d, "HASH_MANIFEST_test-version.json")
        open(out, "w", encoding="utf-8").write("{\"old\": true}\n")
        manifest = generate_manifest.build_manifest(d)
        generate_manifest.write_manifest(manifest, out)

        raw = open(out, "rb").read()
        check("manifest has no UTF-8 BOM", not raw.startswith(b"\xef\xbb\xbf"))
        parsed = json.loads(raw.decode("utf-8"))
        check("strict JSON parse succeeds", parsed["version"] == "test-version")
        check("canonical text hash mode declared", parsed["hash_mode"] == "sha256-canonical-lf-text-v1")
        check("runtime mvr/state.json excluded", "mvr\\state.json" not in parsed["files"])
        check("normal files included", "README.md" in parsed["files"])
        check("manifest never hashes itself", "HASH_MANIFEST_test-version.json" not in parsed["files"])

        crlf = os.path.join(d, "line-endings.txt")
        open(crlf, "wb").write(b"first\r\nsecond\r\n")
        crlf_hash = generate_manifest.sha256(crlf)
        open(crlf, "wb").write(b"first\nsecond\n")
        check("LF and CRLF release text hash identically", generate_manifest.sha256(crlf) == crlf_hash)

    print()
    if FAILS:
        print(f"FAILURES: {FAILS}")
        raise SystemExit(1)
    print("ALL PASS - manifest generation contract verified.")


if __name__ == "__main__":
    main()
