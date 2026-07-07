"""Generate and verify release hash manifests with strict UTF-8 JSON.

Usage:
  python scripts/generate_manifest.py [package_dir] [output_manifest]

Default package_dir is the current working directory. Default output path is the
parent directory as HASH_MANIFEST_<VERSION>.json.

The manifest is written with Python's explicit UTF-8 encoder and no BOM. Do not
generate release manifests through shell JSON serialization.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


EXCLUDED_DIRS = {".git", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_RUNTIME_PATHS = {
    ("mvr", "state.json"),
    ("mvr", "passport.json"),
    ("mvr", "decision-log.json"),
    ("mvr", "gate-events.jsonl"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def included_files(package_dir):
    package_dir = Path(package_dir).resolve()
    files = []
    for root, dirs, names in os.walk(package_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        root_path = Path(root)
        for name in names:
            path = root_path / name
            rel = path.relative_to(package_dir)
            parts = tuple(rel.parts)
            if path.suffix in EXCLUDED_SUFFIXES:
                continue
            if parts in EXCLUDED_RUNTIME_PATHS:
                continue
            files.append(rel.as_posix().replace("/", "\\"))
    return sorted(files)


def build_manifest(package_dir):
    package_dir = Path(package_dir).resolve()
    version = (package_dir / "VERSION").read_text(encoding="utf-8").strip()
    return {
        "version": version,
        "generated": datetime.now().date().isoformat(),
        "files": {
            rel: sha256(package_dir / rel)
            for rel in included_files(package_dir)
        },
    }


def write_manifest(manifest, output_path):
    output_path = Path(output_path)
    text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
    output_path.write_text(text, encoding="utf-8")
    raw = output_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RuntimeError(f"{output_path} was written with a UTF-8 BOM")
    json.loads(raw.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", nargs="?", default=os.getcwd())
    parser.add_argument("output_manifest", nargs="?")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    manifest = build_manifest(package_dir)
    output = (
        Path(args.output_manifest)
        if args.output_manifest
        else package_dir.parent / f"HASH_MANIFEST_{manifest['version']}.json"
    )
    write_manifest(manifest, output)
    print(f"manifest={output}")
    print(f"version={manifest['version']} file_count={len(manifest['files'])}")


if __name__ == "__main__":
    main()
