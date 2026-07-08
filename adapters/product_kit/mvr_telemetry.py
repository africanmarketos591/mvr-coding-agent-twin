"""Consented product telemetry kit for Twin-guided builds.

This file is meant to be copied into the product the Twin helps build. It turns
aggregate product usage into a dry-run `/v1/telemetry-translate` payload so the
charter can later be settled from reality. It is deliberately modest:

- aggregate 0-100 values only
- PII-looking metric names are refused
- dry-run by default
- self-telemetry is a leading demand signal, not proof of market fit
"""
import json
import os
import re
from datetime import datetime, timezone

CONSENT_BASIS = {
    "consent",
    "contract",
    "legitimate_interest",
    "public_interest",
    "legal_obligation",
    "not_applicable",
}
RETENTION_CLASS = {"session_only", "30d", "90d", "1y", "7y", "contractual"}
REDACTION_STATUS = {"raw", "minimized", "redacted", "aggregated"}

PII_KEY = re.compile(
    r"(email|phone|msisdn|name|nid|passport|gps|lat|lon|address|dob|user_id|customer_id)",
    re.I,
)


class ConsentError(ValueError):
    pass


class MVRTelemetry:
    def __init__(
        self,
        project_id,
        geography,
        consent_basis,
        retention_class="90d",
        buffer_path="mvr_telemetry.buffer.jsonl",
    ):
        if consent_basis not in CONSENT_BASIS:
            raise ConsentError(f"consent_basis must be one of {sorted(CONSENT_BASIS)}")
        if retention_class not in RETENTION_CLASS:
            raise ValueError(f"retention_class must be one of {sorted(RETENTION_CLASS)}")
        if not (geography or {}).get("country"):
            raise ValueError("geography requires at least country")
        self.project_id = str(project_id)
        self.geography = {
            "country": geography.get("country"),
            "city": geography.get("city", ""),
            "town_or_zone": geography.get("town_or_zone", ""),
        }
        self.consent_basis = consent_basis
        self.retention_class = retention_class
        self.buffer_path = buffer_path

    def observe(self, metric, value, redaction_status="aggregated"):
        """Record one aggregate metric on the 0-100 scale."""
        if redaction_status not in REDACTION_STATUS:
            raise ValueError(f"redaction_status must be one of {sorted(REDACTION_STATUS)}")
        metric = str(metric)
        if PII_KEY.search(metric):
            raise ConsentError(f"metric name {metric!r} looks like personal data")
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise ValueError("value must be numeric aggregate data")
        if 0 <= numeric <= 1:
            numeric *= 100
        if not 0 <= numeric <= 100:
            raise ValueError("value must be on the 0-100 aggregate scale")
        record = {
            "metric": metric,
            "value": round(numeric, 2),
            "redaction_status": redaction_status,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        with open(self.buffer_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def buffered(self):
        if not os.path.exists(self.buffer_path):
            return []
        rows = []
        with open(self.buffer_path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def seconds_since_last(self):
        rows = self.buffered()
        if not rows:
            return None
        latest = max(datetime.fromisoformat(row["ts"]) for row in rows)
        return (datetime.now(timezone.utc) - latest).total_seconds()

    def pack(self):
        rows = self.buffered()
        structured = {}
        first_seen = None
        last_seen = None
        for row in rows:
            structured[row["metric"]] = row["value"]
            ts = row["ts"]
            first_seen = ts if first_seen is None or ts < first_seen else first_seen
            last_seen = ts if last_seen is None or ts > last_seen else last_seen
        return {
            "project_id": self.project_id,
            "telemetry_data": {
                "structured_values": structured,
                "observation_count": len(rows),
                "window": {"first_seen": first_seen, "last_seen": last_seen},
            },
            "evidence_geography": self.geography,
            "privacy_envelope": {
                "consent_basis": self.consent_basis,
                "retention_class": self.retention_class,
                "redaction_status": "aggregated",
            },
            "source_class": "telemetry_internal",
            "honesty_note": (
                "Self-telemetry is a capped leading demand signal only; it needs "
                "field corroboration before stronger claims."
            ),
        }

    def flush(self, submit=False, client=None):
        payload = self.pack()
        if not submit:
            print("mvr_telemetry dry-run payload:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return payload
        if client is None:
            raise RuntimeError("submit=True requires spine/mvr_client or a compatible client")
        latency, status, body = client.call("/v1/telemetry-translate", payload)
        return {"latency": latency, "status": status, "response": body}
