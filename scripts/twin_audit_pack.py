"""Create a reviewer pack from the artifacts the Twin actually verified.

The command never invents a decision log, review target, or receipt. It derives
them from the project, records command exits, and refuses to copy common secret
carriers. The key file is used for live verification but is never packaged.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone


HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "twin_verify_run.py")
BUILD_SPEC = os.path.join(HERE, "twin_build_spec.py")

GOVERNANCE_PATHS = (
    "AGENTS.md", "PREFLIGHT.md", "charter.md", "MIRROR.md", "MVR_DELTA_REPORT.md",
    "README.md", "mvr/user-brief.txt", "mvr/committee_packet.json",
    "mvr/decision-log.json", "mvr/decision-log.seed.json", "mvr/build_spec.json",
    "mvr/build-contract-history.jsonl", "mvr/semantic-review-request.json",
    "mvr/semantic-review.json", "mvr/semantic-review-2.json", "mvr/gate-events.jsonl",
    "mvr/final-status.json",
)
SENSITIVE_NAMES = {
    ".env", "credentials.json", "passport.json", "secrets.json", "service-account.json",
}


def read_json(path, fallback=None):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return fallback


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inside(root, path):
    try:
        return os.path.commonpath([root, path]) == root
    except ValueError:
        return False


def sensitive(relative):
    parts = [part.lower() for part in relative.replace("\\", "/").split("/")]
    name = parts[-1] if parts else ""
    return (
        name in SENSITIVE_NAMES
        or name.startswith(".env.")
        or any(token in name for token in ("api-key", "api_key", "keyfile", "private-key", "secret"))
    )


def run_command(command, cwd):
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    output = completed.stdout
    if completed.stderr:
        output += ("\n" if output else "") + completed.stderr
    return completed.returncode, output


def copy_into(root, staging, relative, omitted):
    source = os.path.abspath(os.path.join(root, relative))
    normalized = os.path.relpath(source, root).replace("\\", "/")
    if not inside(root, source) or not os.path.isfile(source):
        return False
    if sensitive(normalized):
        omitted.append({"path": normalized, "reason": "secret_or_private_carrier", "sha256": sha256_file(source)})
        return False
    target = os.path.join(staging, normalized.replace("/", os.sep))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(source, target)
    return True


def deterministic_zip(staging, output):
    entries = []
    for base, _dirs, files in os.walk(staging):
        for name in files:
            path = os.path.join(base, name)
            entries.append((os.path.relpath(path, staging).replace("\\", "/"), path))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, path in sorted(entries):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with open(path, "rb") as handle:
                archive.writestr(info, handle.read())


def main():
    parser = argparse.ArgumentParser(description="Build a hash-manifested MVR Twin reviewer package.")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--output", required=True)
    parser.add_argument("--keyfile")
    parser.add_argument("--stage", choices=("build", "export"), default="export")
    parser.add_argument("--include-product", action="store_true")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    request = read_json(os.path.join(root, "mvr", "semantic-review-request.json"), {})
    targets = request.get("targets") if isinstance(request, dict) else []
    targets = targets if isinstance(targets, list) else []

    build_command = [sys.executable, BUILD_SPEC, "--root", root, "--check", *targets, "--require-independent-review"]
    if not targets:
        build_exit, build_output = 2, "No targets found in mvr/semantic-review-request.json; check not run.\n"
    else:
        build_exit, build_output = run_command(build_command, root)

    verify_command = [
        sys.executable, VERIFY, "--root", root, "--stage", args.stage,
        "--json",
    ]
    if args.keyfile:
        verify_command.extend(["--keyfile", os.path.abspath(args.keyfile)])
    verify_exit, verify_output = run_command(verify_command, root)
    verify_result = None
    try:
        verify_result = json.loads(verify_output)
    except Exception:
        verify_result = {"status": "unreadable", "raw_output_recorded": True}

    temp_parent = os.path.dirname(output)
    with tempfile.TemporaryDirectory(prefix="mvr-audit-pack-", dir=temp_parent) as staging:
        omitted = []
        copied = []
        for relative in GOVERNANCE_PATHS:
            if copy_into(root, staging, relative, omitted):
                copied.append(relative)
        if args.include_product:
            for item in (request.get("files") or []) + (request.get("opaque_files") or []):
                relative = item.get("path") if isinstance(item, dict) else None
                if relative and copy_into(root, staging, relative, omitted):
                    copied.append(relative)

        if isinstance(verify_result, dict) and verify_result.get("status"):
            status_path = os.path.join(staging, "mvr", "final-status.json")
            os.makedirs(os.path.dirname(status_path), exist_ok=True)
            with open(status_path, "w", encoding="utf-8", newline="\n") as handle:
                json.dump({
                    "format": "mvr_final_status_v1",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "stage": verify_result.get("stage"),
                    "status": verify_result.get("status"),
                    "final_response_banner": verify_result.get("final_response_banner"),
                    "dimensions": verify_result.get("dimensions") or {},
                    "boundary": verify_result.get("boundary"),
                }, handle, indent=2, ensure_ascii=False)
                handle.write("\n")

        outputs = os.path.join(staging, "verification_outputs")
        os.makedirs(outputs, exist_ok=True)
        with open(os.path.join(outputs, "build_spec_check.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(build_output)
        with open(os.path.join(outputs, "twin_verify_run.json"), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(verify_result, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

        records = []
        for base, _dirs, files in os.walk(staging):
            for name in files:
                path = os.path.join(base, name)
                relative = os.path.relpath(path, staging).replace("\\", "/")
                records.append({"path": relative, "size": os.path.getsize(path), "sha256": sha256_file(path)})
        manifest = {
            "format": "mvr_twin_audit_pack_v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "stage": args.stage,
            "review_targets": targets,
            "commands": [
                {
                    "name": "build_spec_check",
                    "display": "python scripts/twin_build_spec.py --root . --check <targets-from-request> --require-independent-review",
                    "exit_code": build_exit,
                },
                {
                    "name": "twin_verify_run",
                    "display": f"python scripts/twin_verify_run.py --root . --stage {args.stage} --keyfile <keyfile> --json",
                    "exit_code": verify_exit,
                },
            ],
            "included_product_files": bool(args.include_product),
            "copied_sources": sorted(set(copied)),
            "omitted_sensitive_sources": omitted,
            "files": sorted(records, key=lambda item: item["path"]),
            "boundary": (
                "The pack records verifier evidence and exact review targets. It does not convert a rejected "
                "or incomplete run into a pass, and it never packages the API key."
            ),
        }
        with open(os.path.join(staging, "AUDIT_MANIFEST.json"), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        deterministic_zip(staging, output)

    print(f"MVR AUDIT PACK: {output}")
    print(f"  build_spec_check exit: {build_exit}")
    print(f"  twin_verify_run exit: {verify_exit}")
    print(f"  sha256: {sha256_file(output)}")
    return 0 if build_exit == 0 and verify_exit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
