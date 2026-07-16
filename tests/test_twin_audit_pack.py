"""Audit packaging derives its evidence from the run instead of inventing it."""
import json
import os
import subprocess
import sys
import tempfile
import zipfile


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "scripts", "twin_audit_pack.py")
FAILS = []


def check(name, condition, detail=""):
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
    if not condition:
        FAILS.append(name)


def write(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "w"
    with open(path, mode, encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def main():
    with tempfile.TemporaryDirectory() as root:
        write(os.path.join(root, "src", "app.py"), "print('demo')\n")
        write(
            os.path.join(root, "mvr", "decision-log.seed.json"),
            json.dumps([{"entry_id": "DL-seed-only", "kernel_receipts": {}}]),
        )
        write(os.path.join(root, "mvr", "committee_packet.json"), json.dumps({"provisional": True}))
        write(os.path.join(root, "mvr", "build_spec.json"), json.dumps({"format": "intentionally-invalid"}))
        write(
            os.path.join(root, "mvr", "semantic-review-request.json"),
            json.dumps({
                "format": "mvr_semantic_review_request_v3",
                "targets": ["src/app.py"],
                "files": [{"path": "src/app.py", "sha256": "0" * 64}],
                "opaque_files": [],
            }),
        )
        output = os.path.join(root, "review.zip")
        completed = subprocess.run(
            [sys.executable, SCRIPT, "--root", root, "--output", output, "--stage", "export", "--include-product"],
            text=True,
            capture_output=True,
            check=False,
        )
        check("a rejected run still produces an honest audit pack", completed.returncode == 1 and os.path.isfile(output))
        with zipfile.ZipFile(output) as archive:
            names = set(archive.namelist())
            manifest = json.loads(archive.read("AUDIT_MANIFEST.json"))
        check("actual decision-log seed is preserved", "mvr/decision-log.seed.json" in names)
        check("missing finalized decision log is not invented", "mvr/decision-log.json" not in names)
        check("review targets come from the request", manifest["review_targets"] == ["src/app.py"], manifest["review_targets"])
        check("exact product review carrier can be included", "src/app.py" in names)
        exits = {item["name"]: item["exit_code"] for item in manifest["commands"]}
        check("both verifier exits are recorded", set(exits) == {"build_spec_check", "twin_verify_run"}, exits)

    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    print("ALL PASS - audit pack preserves actual evidence, targets, and failures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
