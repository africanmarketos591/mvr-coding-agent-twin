"""Reusable outbound claim scanner for MCP proxies, CI, and webhook wrappers.

The git gate stops claim-shaped content at commit time. Claims can also leave via
email, dashboards, CI/runtime deploy text, MCP tool calls, or copy-paste. This
library does the honest package-level part: scan text with the same keyword floor
plus semantic/multilingual escalation tier the gates use. The host enforces.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks"))
from claim_gate import classify_escalating_content  # noqa: E402


def scan_egress(text, path_hint="egress://payload.md", mode="advisory"):
    claim_class, reason, tier = classify_escalating_content(path_hint, text or "")
    if not claim_class:
        return {"claim_class": None, "tier": "none", "reason": "", "action": "allow"}
    action = "block" if mode == "block" else "flag"
    return {"claim_class": claim_class, "tier": tier, "reason": reason, "action": action}


def guard(text, mode="block", path_hint="egress://payload.md"):
    return scan_egress(text, path_hint=path_hint, mode=mode)["action"] != "block"
