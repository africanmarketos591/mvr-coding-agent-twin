# How to run MVR-VIABILITY-BENCH v1

## Layout
```
mvr-twin-benchmark-v1/
  answer_key.json
  score_benchmark.py
  BENCHMARK_SPEC.md
  runs/
    REG-1/control/   REG-1/treatment/
    REG-2/control/   REG-2/treatment/
    ...
```

## Per Case
Repeat for all 12 ids in `answer_key.json`.

1. Control arm: fresh dir `runs/<ID>/control/`. Give the target model only the case `brief` plus `founder_claim` if present. Do not mention MVR, regulation, validation, or expected traps. Ask for the usual deliverables: `PRODUCT_PLAN.md`, `scaffold/`, `GO_TO_MARKET.md`, `SUMMARY.md`, plus the symmetric verdict record below.
2. Treatment arm: fresh dir `runs/<ID>/treatment/`. Clone the Twin with the canonical folder name:
   `git clone --depth 1 --branch v1.1.0-beta.31 https://github.com/africanmarketos591/mvr-coding-agent-twin mvr-coding-agent-twin`
   Give the same brief plus the standard Twin preamble: install with `--verify`; run preflight step 0 with the case market/archetype; run public research; run committee; write and preregister the charter; run the fabrication scan. Load `MVR_API_KEY` from the keyfile, never print it.
3. Same model and decoding for both arms. Record tokens, tool calls, and wall time per arm.

Both arms must write the same machine-readable file, without seeing the answer key:

```json
{
  "verdict": "proceed | redirect | abstain | conditional | uncalibrated",
  "reason": "one sentence pointing to the arm's own output"
}
```

Save it as `BENCHMARK_VERDICT.json`. This removes the old asymmetry where the treatment had a `Status:` line but the control was interpreted from keyword soup. If a legacy run lacks these files, use a third blind judge for both arms and pass its JSON with `--judge-verdicts`; do not mix machine status for one arm with heuristic prose for the other.

For the UNCAL cases, still give the treatment arm the Twin. The test is whether it declares uncalibrated under Law 6 instead of faking an African-market verdict.

## Score
```
python score_benchmark.py --answer-key answer_key.json --runs ./runs \
  --scanner runs/REG-1/treatment/mvr-coding-agent-twin/scripts/twin_fabrication_scan.py \
  --twin runs/REG-1/treatment/mvr-coding-agent-twin \
  --keyfile <path-to-keyfile>
```

`--scanner` is optional, but required for publishable fabrication counts. `--twin` plus `--keyfile` is required for publishable full-system/kernel-backed claims; otherwise the scorer can only report receipt-looking hashes as unchecked.

For a legacy blind run with a symmetric third-party judgment:

```
python score_benchmark.py ... --judge-verdicts runs/_judge_verdicts.json
```

A publishable headline must show no `legacy_heuristic` verdict sources.

The scorer prints `scorer_version`, `scanner_version`, `answer_key_sha256`, `ledger_verification`, and `kernel_modes`. Quote those fields with any headline number. If treatment charters show `PROVISIONAL`, `spine unavailable`, or `kernel_receipts: {}`, label the result as doctrine/tooling outage-mode evidence, not a full kernel-backed Twin result. If the scorer reports `kernel_receipted_unchecked`, rerun with `--twin` and `--keyfile`. If it reports `kernel_unverified`, treat the charter as a possible forged or mismatched receipt until investigated.

## Required Run Manifest
Save a `run_manifest.json` beside `runs/` for every benchmark run:

```json
{
  "model_id": "",
  "decoding": "",
  "date": "",
  "twin_version": "",
  "twin_commit": "",
  "scanner_version": "",
  "score_benchmark_version": "",
  "answer_key_sha256": "",
  "arm_authorship": {
    "control_author": "",
    "treatment_author": "",
    "blind_to_answer_key": true
  },
  "kernel_reachable_before_run": true,
  "kernel_version": "",
  "kernel_mode": "kernel_receipted | provisional_outage | mixed",
  "notes": ""
}
```

Full-system claims require a reachable kernel and non-empty kernel receipts in the treatment charters. If the kernel is down, the run is still valuable: it tests how much the Twin's doctrine, tools, research layer, and export scanners preserve judgment under outage conditions.

## What To Send For Review
Send the whole `runs/` tree, both arms for all cases, plus per-arm token/time costs and the reproducibility manifest. Include model id, twin commit from `git rev-parse HEAD`, kernel version from `/v1/schema`, scanner version, scorer version, kernel mode, and date.

The reviewer should rerun the scorer, verify charter hashes and fabrication scans, spot-check verdict inference against the actual text, and flag any case where ground truth needs refreshing.

## Honest Expectations
- If the Twin is real, treatment should win big on REG/ECL/DEM/ECON-1, tie-or-win on distribution, ship zero fabrications, proceed on CLEAN, and declare uncalibrated on UNCAL while control walks into the graveyards or fakes calibration.
- The interesting failures to watch for: does treatment over-kill ECON-2 by reflexively abstaining on a viable capex model? Does it over-caution a CLEAN case because the committee habit is to redirect? Those are real Twin gaps, which is exactly what this benchmark exists to surface.
