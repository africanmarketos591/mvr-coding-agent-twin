"""Dependency-free settlement pulse collectors.

The Twin observes and packages outcomes; it does not settle them. These collectors
gather automatable public signals for a human settlement worksheet. Every collector
fails to "unknown" rather than inventing a pulse.
"""
import json
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone


UA = "mvr-coding-agent-twin/1.0 (settlement-pulse)"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _signal(name, value, provenance, detail=""):
    return {
        "signal": name,
        "value": value,
        "provenance": provenance,
        "detail": detail,
        "checked_at": _now(),
    }


def domain_resolves(host):
    host = host.replace("https://", "").replace("http://", "").split("/")[0].strip()
    try:
        socket.getaddrinfo(host, None)
        return _signal("domain_resolves", True, f"dns:{host}")
    except socket.gaierror:
        return _signal("domain_resolves", False, f"dns:{host}", "NXDOMAIN / no address")
    except Exception as exc:
        return _signal("domain_resolves", "unknown", f"dns:{host}", str(exc)[:120])


def url_alive(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _signal("url_alive", 200 <= resp.status < 400, f"http:{url}", f"status {resp.status}")
    except urllib.error.HTTPError as exc:
        return _signal("url_alive", exc.code < 400, f"http:{url}", f"status {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return _signal("url_alive", False, f"http:{url}", f"unreachable: {str(getattr(exc, 'reason', exc))[:80]}")


def github_repo_pulse(owner_repo, timeout=10):
    try:
        url = f"https://api.github.com/repos/{owner_repo}"
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        return _signal("repo_last_push", data.get("pushed_at"), f"github:{owner_repo}")
    except Exception as exc:
        return _signal("repo_last_push", "unknown", f"github:{owner_repo}", str(exc)[:100])


def collect(targets):
    signals = []
    if targets.get("domain"):
        signals.append(domain_resolves(targets["domain"]))
    if targets.get("url"):
        signals.append(url_alive(targets["url"]))
    if targets.get("repo"):
        signals.append(github_repo_pulse(targets["repo"]))
    return signals


def presumed_dead(signals):
    liveness = [s["value"] for s in signals if s.get("signal") in ("domain_resolves", "url_alive")]
    return bool(liveness) and all(value is False for value in liveness)
