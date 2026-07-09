"""Generate an MVR Delta Report for a completed Twin-guided build.

The report makes the Twin's value visible without inventing a strawman:

- grounded fields come from `charter.md` and `mvr/decision-log.json`;
- claim authorization comes only from the decision log;
- the "unconstrained agent" section is a labelled hypothesis for the host model
  to complete, not a factual claim.

Usage:
  python scripts/twin_delta_report.py --root . [--idea "..."]

Writes `MVR_DELTA_REPORT.md` by default.
"""
import argparse
import json
import os
import re


MODEL_FILL = "<!-- MODEL: complete from the session. Do not assert market facts or claims. -->"
AUTHORITY_KEYS = (
    "immutable_audit_hash",
    "provenance_hash",
    "response_hash",
    "full_response_hash",
    "immutable_receipt_hash",
    "strategy_sparring_immutable_receipt_hash",
)


def _load_latest_entry(root):
    for name in ("decision-log.json", "decision-log.seed.json"):
        path = os.path.join(root, "mvr", name)
        if not os.path.exists(path):
            continue
        try:
            data = json.load(open(path, encoding="utf-8-sig"))
            entries = data if isinstance(data, list) else [data]
            for entry in reversed(entries):
                if isinstance(entry, dict) and entry.get("entry_type") != "settlement":
                    return entry, name
        except Exception:
            pass
    return None, None


def _section(markdown, header_regex):
    if not markdown:
        return ""
    match = re.search(header_regex, markdown, re.I)
    if not match:
        return ""
    start = match.end()
    nxt = re.search(r"\n#{1,3}\s", markdown[start:])
    return markdown[start:start + (nxt.start() if nxt else len(markdown))].strip()


def _first_line(text, fallback):
    for line in (text or "").splitlines():
        line = line.strip(" -*\t")
        if line:
            return line
    return fallback


def _receipt_hash(receipts):
    if not isinstance(receipts, dict):
        return None, None
    for key in AUTHORITY_KEYS:
        value = receipts.get(key)
        if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
            return key, value
    for key, value in receipts.items():
        lowered = str(key).lower()
        if (
            isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{64}", value)
            and ("receipt_hash" in lowered or "audit_hash" in lowered or "response_hash" in lowered)
            and "content_hash" not in lowered
        ):
            return key, value
    return None, None


def build_report(root, idea=None):
    entry, source_log = _load_latest_entry(root)
    charter_path = os.path.join(root, "charter.md")
    charter = open(charter_path, encoding="utf-8", errors="replace").read() if os.path.exists(charter_path) else ""

    auth = []
    not_auth = []
    verdict = None
    receipt_key = receipt_value = None
    if entry:
        decision_authorization = entry.get("decision_authorization") or {}
        auth = decision_authorization.get("authorized_use") or []
        not_auth = decision_authorization.get("not_authorized_use") or []
        verdict = entry.get("verdict")
        receipt_key, receipt_value = _receipt_hash(entry.get("kernel_receipts") or {})

    idea_text = idea or _first_line(_section(charter, r"idea as received"), MODEL_FILL)
    pivot = _section(charter, r"##.*pivot") or MODEL_FILL
    build = _section(charter, r"##.*the build|build this") or MODEL_FILL
    not_building = _section(charter, r"not building|explicitly not") or MODEL_FILL
    settlement = _section(charter, r"##.*settlement") or MODEL_FILL
    missing = _section(charter, r"evidence still missing|missing evidence|evidence bill") or MODEL_FILL

    claim_line = ", ".join(auth) if auth else "internal_planning (default; no authorizing entry found)"
    blocked_line = ", ".join(not_auth) if not_auth else MODEL_FILL

    if receipt_value:
        receipt_line = (
            f"Kernel receipt: `{receipt_value}` ({receipt_key}). "
            f"Verify with: `python scripts/verify_receipts.py mvr/{source_log}`."
        )
    else:
        receipt_line = "No kernel receipt on file. This is lens-only reasoning until the live committee runs."

    lines = [
        "# MVR Delta Report",
        "",
        "What changed when the market co-processor sat beside the coding agent. Grounded facts come from",
        "`charter.md` and `mvr/decision-log.json`; the counterfactual is labelled as a hypothesis.",
        "",
        "## What the user originally asked for",
        idea_text,
        "",
        "## What an unconstrained coding agent would likely have built",
        "> Hypothesis, not a market claim: the literal request taken at face value.",
        MODEL_FILL,
        "",
        "## What MVR changed",
        f"- Kernel verdict at pre-charter: {verdict or MODEL_FILL}",
        f"- Claim level authorized today: {claim_line}",
        f"- Classes still blocked: {blocked_line}",
        f"- Changed first feature: {_first_line(build, MODEL_FILL)}",
        f"- Added missing-evidence task: {_first_line(missing, MODEL_FILL)}",
        f"- Added settlement metric: {_first_line(settlement, MODEL_FILL)}",
        "",
        "## Why the MVR version is stronger",
        MODEL_FILL,
        "",
        "## The redirect, if any",
        pivot,
        "",
        "## Explicitly not building",
        not_building,
        "",
        "## What remains unproven",
        missing,
        "",
        "## External trust check",
        receipt_line,
        "",
        "---",
        "A working demo proves buildability. This report exists so buildability is never mistaken for market validation.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--idea")
    parser.add_argument("--out")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    out = args.out or os.path.join(root, "MVR_DELTA_REPORT.md")
    report = build_report(root, args.idea)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(report)
    entry, _ = _load_latest_entry(root)
    grounded = bool(entry and (entry.get("decision_authorization") or {}).get("authorized_use"))
    print(f"wrote {out}")
    print(f"claim level grounded in decision-log: {'yes' if grounded else 'no (default internal_planning)'}")


if __name__ == "__main__":
    main()
