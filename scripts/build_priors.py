"""Build advisory outcome priors from settled Twin decision logs.

This does NOT mutate the MVR kernel. It turns settled charter outcomes into a
local, advisory summary that can be read during PRE-CHARTER. Kernel calibration
ingestion remains a governed API-side process.

Usage:
  python scripts/build_priors.py --log mvr/decision-log.json --out governance/outcome_priors.json
"""
import argparse
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone


OUTCOMES = ("hit", "partial", "miss", "unresolvable")


def load_entries(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise SystemExit(f"{path} must be a JSON array")
    return data


def normalize(value, fallback):
    if value is None:
        return fallback
    text = str(value).strip().lower().replace(" ", "_")
    return text or fallback


def base_entry_for(entries, settlement):
    charter_ref = settlement.get("charter_ref")
    charter_hash = settlement.get("charter_hash")
    candidates = []
    for entry in entries:
        if entry.get("entry_type") == "settlement":
            continue
        if charter_ref and entry.get("charter_ref") == charter_ref:
            candidates.append(entry)
        elif charter_hash and entry.get("charter_hash") == charter_hash:
            candidates.append(entry)
    return candidates[-1] if candidates else {}


def prior_key(base):
    return {
        "archetype": normalize(base.get("archetype") or base.get("calibration_scope"), "unknown_archetype"),
        "market": normalize(base.get("market_scope") or base.get("country") or base.get("geo_scope"), "unknown_market"),
        "verdict": normalize(base.get("verdict"), "unknown_verdict"),
        "redirect_pattern": normalize(base.get("redirect_pattern"), "unknown_redirect"),
    }


def key_id(key):
    return "|".join(key[name] for name in ("archetype", "market", "verdict", "redirect_pattern"))


def build(entries, min_n):
    buckets = defaultdict(lambda: {"counts": {name: 0 for name in OUTCOMES}, "examples": []})
    for entry in entries:
        if entry.get("entry_type") != "settlement":
            continue
        settlement = entry.get("settlement") or {}
        outcome = settlement.get("outcome")
        if outcome not in OUTCOMES:
            continue
        base = base_entry_for(entries, entry)
        key = prior_key(base)
        bucket = buckets[key_id(key)]
        bucket["key"] = key
        bucket["counts"][outcome] += 1
        if len(bucket["examples"]) < 5:
            bucket["examples"].append({
                "charter_ref": entry.get("charter_ref"),
                "outcome": outcome,
                "summary": settlement.get("summary", ""),
                "sources": settlement.get("sources", [])[:3],
            })

    priors = []
    for _, bucket in sorted(buckets.items()):
        counts = bucket["counts"]
        n = sum(counts.values())
        resolved = counts["hit"] + counts["partial"] + counts["miss"]
        priors.append({
            **bucket["key"],
            "n": n,
            "resolved_n": resolved,
            "counts": counts,
            "hit_rate": round(counts["hit"] / resolved, 3) if resolved else None,
            "miss_rate": round(counts["miss"] / resolved, 3) if resolved else None,
            "prior_status": "usable_advisory_prior" if n >= min_n else "insufficient_prior",
            "minimum_n": min_n,
            "examples": bucket["examples"],
        })
    return priors


def atomic_write(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".outcome-priors.", suffix=".tmp", dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=os.path.join("mvr", "decision-log.json"))
    parser.add_argument("--out", default=os.path.join("governance", "outcome_priors.json"))
    parser.add_argument("--min-n", type=int, default=5)
    args = parser.parse_args()

    entries = load_entries(args.log)
    data = {
        "format": "mvr_outcome_priors_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_log": args.log,
        "policy": "advisory_only_no_kernel_mutation_no_claim_authorization",
        "minimum_n": args.min_n,
        "priors": build(entries, args.min_n),
    }
    atomic_write(args.out, data)
    print(json.dumps({"out": args.out, "priors": len(data["priors"]), "minimum_n": args.min_n}, indent=2))


if __name__ == "__main__":
    main()
