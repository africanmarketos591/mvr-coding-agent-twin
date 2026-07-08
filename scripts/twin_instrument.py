"""Drop the self-settling telemetry kit into a product root.

This generator writes:
  - mvr_telemetry.py
  - INSTRUMENTATION.md
  - mvr/settlement_map.json

It never fabricates data and never authorizes claims. The generated kit is dry-run
by default and produces capped leading demand evidence for later human-reviewed
settlement.
"""
import argparse
import json
import os
import shutil
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(HERE)
KIT = os.path.join(PACKAGE_ROOT, "adapters", "product_kit", "mvr_telemetry.py")


def parse_mapping(items):
    criteria = []
    for item in items:
        metric, separator, criterion = item.partition(":")
        if not separator or not metric.strip() or not criterion.strip():
            raise ValueError("--map must look like metric:criterion")
        checkpoint = "t+90d" if "90d" in criterion else "t+365d" if "365d" in criterion else "unspecified"
        criteria.append({
            "metric": metric.strip(),
            "criterion": criterion.strip(),
            "checkpoint": checkpoint,
        })
    return criteria


def main():
    parser = argparse.ArgumentParser(description="Instrument a product for draft-only MVR settlement.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--city", default="")
    parser.add_argument("--zone", default="")
    parser.add_argument("--consent-basis", default="consent")
    parser.add_argument("--map", action="append", default=[], help="metric:settlement criterion")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "mvr"), exist_ok=True)
    shutil.copy2(KIT, os.path.join(root, "mvr_telemetry.py"))

    criteria = parse_mapping(args.map)
    settlement_map = {
        "project_id": args.project_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "geography": {
            "country": args.country,
            "city": args.city,
            "town_or_zone": args.zone,
        },
        "consent_basis": args.consent_basis,
        "criteria": criteria,
        "silence_rule": "no telemetry since launch is a presumed-dead signal",
        "cap": "self-telemetry is a leading demand signal only and requires field corroboration",
    }
    with open(os.path.join(root, "mvr", "settlement_map.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(settlement_map, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    rows = "\n".join(
        f"| `{item['metric']}` | {item['checkpoint']} | {item['criterion']} |"
        for item in criteria
    ) or "| (none mapped yet) | | |"
    doc = f"""# INSTRUMENTATION - {args.project_id}

This product is instrumented so real aggregate usage can inform the Build Charter settlement.

```python
from mvr_telemetry import MVRTelemetry

tel = MVRTelemetry(
    project_id="{args.project_id}",
    geography={{"country": "{args.country}", "city": "{args.city}", "town_or_zone": "{args.zone}"}},
    consent_basis="{args.consent_basis}",
)
tel.observe("<metric>", <0-100 aggregate>)
tel.flush()  # dry-run, no network
```

## Metric to Settlement Map

| product metric | checkpoint | charter criterion |
|---|---|---|
{rows}

## Boundaries

- Aggregates only. Do not record names, phone numbers, precise locations, IDs, or emails.
- Self-telemetry is a leading demand signal, not proof of market fit.
- Field corroboration is required before stronger claims.
- Read a draft with `python scripts/twin_settlement_read.py --root <product-root>`.
"""
    with open(os.path.join(root, "INSTRUMENTATION.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(doc)

    print(f"instrumented {root}")
    print("  wrote mvr_telemetry.py")
    print("  wrote INSTRUMENTATION.md")
    print("  wrote mvr/settlement_map.json")


if __name__ == "__main__":
    main()
