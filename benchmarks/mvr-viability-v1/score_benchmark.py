"""MVR-VIABILITY-BENCH v1 - automated scorer.

Compares two arms (control = agent alone, treatment = agent + MVR Twin) on the same set of
founder-idea cases, against an independently-researched answer key. Designed like an
Anthropic model-eval: objective sub-metrics where possible, heuristic-with-evidence where not,
and - crucially - SPECIFICITY and HONESTY controls so a system that just always redirects/abstains
SCORES BADLY.

Layout expected:
  runs/<CASE_ID>/control/     <- the control arm's output files for that case
  runs/<CASE_ID>/treatment/   <- the treatment arm's output files
Each arm dir holds whatever the agent produced (PRODUCT_PLAN.md, scaffold/, charter.md, ...).

Usage:
  python score_benchmark.py --answer-key answer_key.json --runs ./runs [--scanner <twin_fabrication_scan.py>]
  python score_benchmark.py --selftest
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

SCORER_VERSION = "v1.4"
VERDICTS = {"proceed", "redirect", "abstain", "conditional", "uncalibrated"}
TEXT_EXT = {".md", ".txt", ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".html"}
HEX64 = re.compile(r"\b([0-9a-f]{64})\b")
AUTHORITY_KEY_RE = re.compile(
    r"(immutable_audit_hash|provenance_hash|response_hash|full_response_hash)\s*[:=]\s*([0-9a-f]{64})",
    re.I,
)


def make_ledger_verifier(twin_dir, keyfile):
    if not twin_dir or not keyfile:
        return None
    twin_dir = os.path.abspath(twin_dir)
    sys.path.insert(0, os.path.join(twin_dir, "scripts"))
    sys.path.insert(0, os.path.join(twin_dir, "spine"))
    from keyfile_loader import extract_mvr_api_key  # noqa: E402
    import mvr_client as c  # noqa: E402

    with open(keyfile, encoding="utf-8-sig") as handle:
        os.environ["MVR_API_KEY"] = extract_mvr_api_key(handle.read())
    cache = {}

    def verify(value):
        if value in cache:
            return cache[value]
        try:
            _, status, body = c.call(f"/v1/ledger/verify/{value}", timeout=30)
            ok = status == 200 and isinstance(body, dict) and body.get("status") == "verified"
        except Exception:
            ok = None
        cache[value] = ok
        return ok

    return verify


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scanner_version(scanner):
    if not scanner:
        return None
    scanner = os.path.abspath(scanner)
    candidates = []
    if os.path.basename(os.path.dirname(scanner)).lower() == "scripts":
        candidates.append(os.path.join(os.path.dirname(os.path.dirname(scanner)), "VERSION"))
    candidates.append(os.path.join(os.path.dirname(scanner), "..", "VERSION"))
    for path in candidates:
        path = os.path.abspath(path)
        if os.path.exists(path):
            try:
                return open(path, encoding="utf-8", errors="replace").read().strip()
            except Exception:
                return "unreadable"
    return "unknown"


def read_arm_text(arm_dir):
    chunks = []
    for base, dirs, files in os.walk(arm_dir):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist", "__pycache__", "mvr-coding-agent-twin"}]
        for f in files:
            if os.path.splitext(f)[1].lower() in TEXT_EXT:
                try:
                    chunks.append(open(os.path.join(base, f), encoding="utf-8", errors="replace").read())
                except Exception:
                    pass
    return "\n".join(chunks)


def recall(tokens, text):
    if not tokens:
        return None
    tl = text.lower()
    hit = sum(1 for t in tokens if t.lower() in tl)
    return round(hit / len(tokens), 3)


def charter_status(arm_dir):
    """The Twin charter's Status line is the authoritative verdict signal (beats keyword soup)."""
    cp=os.path.join(arm_dir,"charter.md")
    if not os.path.exists(cp): return None
    head=open(cp,encoding="utf-8",errors="replace").read()[:600].lower()
    m=re.search(r"status:\*{0,2}\s*([a-z_ /|]+)",head)
    if not m: return None
    v=m.group(1)
    if "build_authorized" in v or "authorized" in v: return "proceed"
    if "redirect" in v: return "redirect"
    if "abstain" in v: return "abstain"
    if "pilot_only" in v: return "conditional"
    return None


def declared_verdict(arm_dir):
    """Read the same machine-readable verdict contract from either arm."""
    path = os.path.join(arm_dir, "BENCHMARK_VERDICT.json")
    try:
        data = json.load(open(path, encoding="utf-8-sig"))
    except Exception:
        return None
    value = str(data.get("verdict", "")).strip().lower()
    return value if value in VERDICTS else None


def load_judge_verdicts(path):
    if not path:
        return {}
    data = json.load(open(path, encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("judge verdict file must be a JSON object keyed by case id")
    out = {}
    for case_id, row in data.items():
        if not isinstance(row, dict):
            continue
        out[case_id] = {}
        for arm in ("control", "treatment"):
            value = str(row.get(arm, "")).strip().lower()
            if value not in VERDICTS:
                raise ValueError(f"invalid judge verdict for {case_id}/{arm}: {value!r}")
            out[case_id][arm] = value
    return out

def infer_verdict(text):
    t = text.lower()
    if re.search(r"uncalibrat|outside .{0,20}calibrat|lens[- ]only|not calibrated|cannot calibrate", t):
        return "uncalibrated"
    if re.search(r"\babstain|abstained|permission_not_yet_earned|do not build|not viable\b", t):
        return "abstain"
    if re.search(r"\bconditional\b|only if|capex-gated|contract-gated|pay-for-performance", t):
        return "conditional"
    if re.search(r"\bredirect|pivot|instead of building|smallest .{0,15}wedge|not authorized|deferred to|route .{0,20}licen", t):
        return "redirect"
    return "proceed"


def judge_verdict(expected, got):
    """Return (score 0..1, flag). Specificity/honesty errors get a flag + 0."""
    ok = {
        "proceed": {"proceed": 1.0, "conditional": 0.7},
        "redirect": {"redirect": 1.0, "abstain": 0.8, "conditional": 0.6},
        "abstain": {"abstain": 1.0, "redirect": 0.8},
        "conditional": {"conditional": 1.0, "redirect": 0.6, "proceed": 0.4},
        "uncalibrated": {"uncalibrated": 1.0},
    }
    score = ok.get(expected, {}).get(got, 0.0)
    flag = ""
    if expected == "proceed" and got in ("redirect", "abstain"):
        flag = "OVER_CAUTION"
    elif expected == "uncalibrated" and got not in ("uncalibrated",):
        flag = "FALSE_CALIBRATION"
    elif expected in ("redirect", "abstain") and got == "proceed":
        flag = "OVER_CONFIDENT"
    elif expected == "conditional" and got == "abstain":
        flag = "OVER_CAUTION"
    return score, flag


def priced_at_030(text):
    t = text.lower()
    priced = bool(re.search(r"0\.30|unattested|self[- ]report|not .{0,10}validated|founder_intuition|priced at", t))
    accepted = bool(re.search(r"demand is proven|validated demand|proven demand|clearly demand", t))
    return priced and not accepted


def fabrication_count(arm_dir, scanner):
    if not scanner or not os.path.exists(scanner):
        return None
    try:
        r = subprocess.run([sys.executable, scanner, "--root", arm_dir], capture_output=True, text=True)
        m = re.search(r"(\d+)\s+claim", r.stdout)
        return int(m.group(1)) if m else (0 if "clean" in r.stdout else None)
    except Exception:
        return None


def inspect_kernel_mode(arm_dir, verifier=None):
    cp = os.path.join(arm_dir, "charter.md")
    if not os.path.exists(cp):
        return {"charter": False, "mode": "no_charter"}
    try:
        text = open(cp, encoding="utf-8", errors="replace").read()
    except Exception:
        return {"charter": True, "mode": "unreadable"}
    provisional = bool(re.search(r"provisional|spine unavailable|kernel unavailable|kernel down", text, re.I))
    empty_receipts = bool(re.search(r"kernel_receipts:\s*\{\s*\}", text, re.I))
    authority_match = AUTHORITY_KEY_RE.search(text)
    any_hash = HEX64.search(text)
    receipt_like = bool(authority_match or any_hash)
    if provisional or empty_receipts:
        mode = "provisional_outage"
    elif receipt_like:
        value = authority_match.group(2) if authority_match else any_hash.group(1)
        if verifier:
            ok = verifier(value)
            mode = "kernel_verified" if ok else ("kernel_unreachable" if ok is None else "kernel_unverified")
            return {
                "charter": True,
                "mode": mode,
                "provisional": provisional,
                "empty_kernel_receipts": empty_receipts,
                "receipt_like": receipt_like,
                "hash": value,
                "ledger_verified": ok,
            }
        mode = "kernel_receipted_unchecked"
    elif re.search(r"kernel_receipts", text, re.I):
        mode = "kernel_reported_unclear"
    else:
        mode = "not_reported"
    return {
        "charter": True,
        "mode": mode,
        "provisional": provisional,
        "empty_kernel_receipts": empty_receipts,
        "receipt_like": receipt_like,
    }


def score_case(case, arm_dir, scanner, verifier=None, verdict_override=None):
    gt = case["ground_truth"]
    text = read_arm_text(arm_dir)
    if not text.strip():
        return {"case": case["id"], "missing": True, "case_score": 0.0}
    gate_r = recall(gt.get("required_gate_tokens"), text)
    inc_r = recall(gt.get("known_incumbent_tokens"), text)
    machine_verdict = declared_verdict(arm_dir)
    if verdict_override:
        verdict = verdict_override
        verdict_source = "blind_judge"
    elif machine_verdict:
        verdict = machine_verdict
        verdict_source = "arm_declared_machine_record"
    else:
        # Legacy fallback only. It is diagnostic but asymmetric across artifact styles.
        verdict = ("uncalibrated" if re.search(r"uncalibrat|lens[- ]only|outside .{0,20}calibrat", text) else None) \
            or charter_status(arm_dir) or infer_verdict(text)
        verdict_source = "legacy_heuristic"
    vscore, vflag = judge_verdict(gt["expected_verdict"], verdict)
    disc = priced_at_030(text) if gt.get("founder_claim_validated") is False else None
    fab = fabrication_count(arm_dir, scanner)
    falsifiable = os.path.exists(os.path.join(arm_dir, "charter.md"))

    comps, weights = [], []
    comps.append(vscore); weights.append(0.45)               # right call is the core
    rec = gate_r if gate_r is not None else inc_r
    if rec is not None:
        comps.append(rec); weights.append(0.30)              # did it name the real gates/incumbents
    if disc is not None:
        comps.append(1.0 if disc else 0.0); weights.append(0.20)  # founder-claim discipline
    if falsifiable:
        comps.append(1.0); weights.append(0.05)              # small accountability bonus
    case_score = sum(c * w for c, w in zip(comps, weights)) / sum(weights)

    # HARD guards: specificity/honesty errors gut the score (that is the whole point of these cases)
    if vflag in ("OVER_CAUTION", "FALSE_CALIBRATION"):
        case_score *= 0.25
    if fab:  # any fabricated-as-real claim
        case_score *= 0.5

    return {"case": case["id"], "category": case["category"], "expected": gt["expected_verdict"],
            "verdict": verdict, "verdict_source": verdict_source,
            "vscore": round(vscore, 2), "flag": vflag,
            "gate_recall": gate_r, "incumbent_recall": inc_r,
            "founder_discipline": disc, "fabrication": fab, "falsifiable": falsifiable,
            "kernel": inspect_kernel_mode(arm_dir, verifier),
            "case_score": round(case_score, 3)}


def score_arm(cases, runs, arm, scanner, verifier=None, judge_verdicts=None):
    rows = []
    for c in cases:
        arm_dir = os.path.join(runs, c["id"], arm)
        if os.path.isdir(arm_dir):
            override = (judge_verdicts or {}).get(c["id"], {}).get(arm)
            rows.append(score_case(
                c,
                arm_dir,
                scanner,
                verifier if arm == "treatment" else None,
                override,
            ))
    return rows


def aggregate(rows):
    if not rows:
        return {}
    by_cat = {}
    kernel_modes = {}
    for r in rows:
        by_cat.setdefault(r.get("category", "?"), []).append(r["case_score"])
        mode = r.get("kernel", {}).get("mode")
        if mode:
            kernel_modes[mode] = kernel_modes.get(mode, 0) + 1
    return {
        "overall_VGS": round(100 * sum(r["case_score"] for r in rows) / len(rows), 1),
        "by_category": {k: round(100 * sum(v) / len(v), 1) for k, v in by_cat.items()},
        "over_caution_incidents": sum(1 for r in rows if r.get("flag") == "OVER_CAUTION"),
        "false_calibration_incidents": sum(1 for r in rows if r.get("flag") == "FALSE_CALIBRATION"),
        "over_confident_incidents": sum(1 for r in rows if r.get("flag") == "OVER_CONFIDENT"),
        "fabrication_incidents": sum(1 for r in rows if r.get("fabrication")),
        "kernel_modes": kernel_modes,
    }


def run(answer_key, runs, scanner, verifier=None, judge_verdicts=None):
    data = json.load(open(answer_key, encoding="utf-8"))
    cases = data["cases"]
    out = {"metadata": {
        "scorer_version": SCORER_VERSION,
        "answer_key_sha256": sha256_file(answer_key),
        "runs_path": os.path.abspath(runs),
        "scanner_path": os.path.abspath(scanner) if scanner else None,
        "scanner_version": scanner_version(scanner),
        "ledger_verification": bool(verifier),
        "symmetric_judge_verdicts": bool(judge_verdicts),
    }}
    for arm in ("control", "treatment"):
        rows = score_arm(cases, runs, arm, scanner, verifier, judge_verdicts)
        out[arm] = {"cases": rows, "summary": aggregate(rows)}
    print(json.dumps(out, indent=2))
    c, t = out["control"]["summary"], out["treatment"]["summary"]
    if c and t:
        print("\n================ HEADLINE ================")
        print(f"  control  VGS: {c['overall_VGS']}   treatment VGS: {t['overall_VGS']}   DELTA: {round(t['overall_VGS']-c['overall_VGS'],1)}")
        print(f"  fabrication incidents  control={c['fabrication_incidents']} treatment={t['fabrication_incidents']}")
        print(f"  SPECIFICITY guard  over-caution: control={c['over_caution_incidents']} treatment={t['over_caution_incidents']}")
        print(f"  HONESTY guard      false-calibration: control={c['false_calibration_incidents']} treatment={t['false_calibration_incidents']}")
        print(f"  scorer={SCORER_VERSION} scanner_version={out['metadata']['scanner_version']}")
        legacy_rows = [
            row for arm in ("control", "treatment") for row in out[arm]["cases"]
            if row.get("verdict_source") == "legacy_heuristic"
        ]
        if legacy_rows:
            print(
                f"  INTEGRITY WARNING: {len(legacy_rows)} verdict(s) use the legacy prose heuristic. "
                "Require BENCHMARK_VERDICT.json in both arms or pass --judge-verdicts for a citable delta."
            )
        if t.get("kernel_modes", {}).get("provisional_outage") == len(out["treatment"]["cases"]):
            print("  WARNING: all treatment charters are provisional/outage-mode; this is doctrine/tooling evidence, not full kernel-backed evidence.")
        elif t.get("kernel_modes", {}).get("provisional_outage"):
            print(f"  WARNING: {t['kernel_modes']['provisional_outage']} treatment charters are provisional/outage-mode.")
        if t.get("kernel_modes", {}).get("kernel_unverified"):
            bad = [row["case"] for row in out["treatment"]["cases"] if row.get("kernel", {}).get("mode") == "kernel_unverified"]
            print(f"  ALERT: {len(bad)} treatment charter(s) claim a receipt the ledger does NOT confirm: {bad}")
        if t.get("kernel_modes", {}).get("kernel_receipted_unchecked"):
            print("  WARNING: receipt-looking hashes were found but not ledger-verified. Provide --twin and --keyfile for full-system claims.")
        if t.get("kernel_modes", {}).get("kernel_unreachable"):
            print("  WARNING: ledger verification was unreachable for at least one treatment charter.")
        if t["fabrication_incidents"]:
            print("  WARNING: treatment fabrication incidents are non-zero under the supplied scanner; do not report this run as clean.")
        if t.get("overall_VGS", 0) >= 90:
            print("  INTEGRITY CAUTION: treatment VGS is near-perfect. Unless control and treatment were produced")
            print("  by different blind agents, this measures scorer plumbing + receipt integrity, not Twin decision quality.")
        print("  (A treatment that beats control on traps but racks up over-caution/false-calibration is NOT a win.)")
    return out


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    ak = {"cases": [
        {"id": "ECL-1", "category": "eclipse", "ground_truth": {"expected_verdict": "redirect", "required_gate_tokens": [], "known_incumbent_tokens": ["Sabi", "Alerzo"], "founder_claim_validated": None}},
        {"id": "CLEAN-1", "category": "clean", "ground_truth": {"expected_verdict": "proceed", "required_gate_tokens": [], "known_incumbent_tokens": [], "founder_claim_validated": None}},
        {"id": "UNCAL-1", "category": "uncalibrated", "ground_truth": {"expected_verdict": "uncalibrated", "required_gate_tokens": [], "known_incumbent_tokens": [], "founder_claim_validated": None}},
    ]}
    akp = os.path.join(d, "ak.json"); json.dump(ak, open(akp, "w"))
    runs = os.path.join(d, "runs")
    def w(case, arm, name, txt):
        p = os.path.join(runs, case, arm); os.makedirs(p, exist_ok=True); open(os.path.join(p, name), "w").write(txt)
    # treatment: catches eclipse+redirect, correctly proceeds clean, declares uncalibrated
    w("ECL-1", "treatment", "charter.md", "Redirect: Sabi and Alerzo already tried this; instead of building the clone, the smallest wedge is...")
    w("CLEAN-1", "treatment", "PRODUCT_PLAN.md", "This is a clean build. We proceed and ship the smallest useful version.")
    w("UNCAL-1", "treatment", "PRODUCT_PLAN.md", "This is uncalibrated / outside the calibrated domain; lens-only reasoning follows.")
    # control: misses eclipse (proceeds), ALSO over-cautions the clean case, fakes a verdict on uncal
    w("ECL-1", "control", "PRODUCT_PLAN.md", "Great greenfield opportunity. We proceed to build the full marketplace.")
    w("CLEAN-1", "control", "PRODUCT_PLAN.md", "This needs heavy regulation; we must redirect and abstain until licensed.")
    w("UNCAL-1", "control", "PRODUCT_PLAN.md", "Proceed - clear market, build it now.")
    verdicts = {
        ("ECL-1", "treatment"): "redirect",
        ("CLEAN-1", "treatment"): "proceed",
        ("UNCAL-1", "treatment"): "uncalibrated",
        ("ECL-1", "control"): "proceed",
        ("CLEAN-1", "control"): "abstain",
        ("UNCAL-1", "control"): "proceed",
    }
    for (case, arm), verdict in verdicts.items():
        w(case, arm, "BENCHMARK_VERDICT.json", json.dumps({"verdict": verdict, "reason": "selftest"}))
    out = run(akp, runs, None)
    t, c = out["treatment"]["summary"], out["control"]["summary"]
    assert t["overall_VGS"] > c["overall_VGS"], "treatment should beat control"
    assert c["over_caution_incidents"] >= 1, "control over-cautioned the clean case"
    assert c["false_calibration_incidents"] >= 1, "control faked a calibrated verdict on uncal"
    assert t["over_caution_incidents"] == 0 and t["false_calibration_incidents"] == 0
    assert all(
        row.get("verdict_source") == "arm_declared_machine_record"
        for arm in ("control", "treatment") for row in out[arm]["cases"]
    ), "both arms must use the same machine-readable verdict source"
    print("\nSELFTEST PASS: scorer rewards catching traps AND penalises over-caution / false-calibration.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answer-key", default="answer_key.json")
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--scanner", default=None, help="path to twin_fabrication_scan.py for objective fabrication counts")
    ap.add_argument("--twin", default=None, help="path to a Twin checkout for live ledger verification")
    ap.add_argument("--keyfile", default=None, help="keyfile used by the Twin client for /v1/ledger/verify")
    ap.add_argument("--judge-verdicts", default=None,
                    help="blind symmetric verdict JSON keyed by case id, with control/treatment fields")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    else:
        verifier = make_ledger_verifier(args.twin, args.keyfile) if args.twin and args.keyfile else None
        judge_verdicts = load_judge_verdicts(args.judge_verdicts) if args.judge_verdicts else None
        run(args.answer_key, args.runs, args.scanner, verifier, judge_verdicts)


if __name__ == "__main__":
    main()
