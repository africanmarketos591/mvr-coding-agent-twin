"""MVR Twin spine client — the un-prompt-able seat.

Thin, dependency-free client for the MVR kernel (v6.32.x). Auth via env MVR_API_KEY.
IMPORTANT: the kernel edge rejects default Python user agents; this client sets a real UA.
Never hardcode keys. Never widen output parsing to hide abstentions — abstentions are results.
"""
import json, os, tempfile, time, uuid, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = os.environ.get("MVR_BASE_URL", "https://africanmarketos.com")
UA = "mvr-coding-agent-twin/1.0 (spine-client)"


class SpineError(RuntimeError):
    pass


def _key():
    k = os.environ.get("MVR_API_KEY", "").strip()
    if not k:
        raise SpineError(
            "MVR_API_KEY not set. Sandbox STANDARD key: mvr-demo-key-2026 "
            "(non-commercial; full smoke requires PRO/ENTERPRISE-scope access)."
        )
    return k


def _project_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def _state_path(project_dir=None):
    return os.path.join(project_dir or _project_root(), "mvr", "state.json")


def _as_list(value):
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _load_state(path):
    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as handle:
                state = json.load(handle)
                if isinstance(state, dict):
                    return state
    except Exception:
        pass
    return {}


def _atomic_json(path, value):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".state.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _extract_blockers(data):
    for key in ("top_blockers", "evidence_gaps", "abstention_reason_codes", "evidence_required", "unsafe_claims"):
        value = data.get(key)
        if isinstance(value, list) and value:
            blockers = []
            for item in value[:3]:
                if isinstance(item, dict):
                    blockers.append(item.get("claim") or item.get("question") or item.get("reason") or json.dumps(item, ensure_ascii=False)[:160])
                else:
                    blockers.append(str(item))
            return blockers
    return []


def update_state(route, data, charter_ref=None, passport_status=None, settlement_next=None, project_dir=None):
    """Merge a kernel response into mvr/state.json for the heartbeat hook.

    This cache is intentionally small: no raw evidence, no private payloads, no keys.
    The decision log remains the audit trail; state.json is just the current context.
    """
    if not isinstance(data, dict):
        return
    path = _state_path(project_dir)
    state = _load_state(path)
    state["last_kernel_sync"] = datetime.now(timezone.utc).isoformat()
    state["last_route"] = route
    routes = _as_list(state.get("routes_called"))
    if route not in routes:
        routes.append(route)
    state["routes_called"] = routes[-12:]
    if charter_ref:
        state["charter_ref"] = charter_ref
    if passport_status:
        state["passport_status"] = passport_status
    if settlement_next:
        state["settlement_next"] = settlement_next

    verdict = data.get("verdict") or data.get("terminal_verdict") or data.get("status")
    if verdict:
        state["verdict"] = verdict
    if data.get("confidence") is not None:
        state["confidence"] = data.get("confidence")

    auth = data.get("decision_authorization")
    if isinstance(auth, dict):
        state["authorized_use"] = _as_list(auth.get("authorized_use"))
        state["not_authorized_use"] = _as_list(auth.get("not_authorized_use") or auth.get("not_authorized_for"))

    blockers = _extract_blockers(data)
    if blockers:
        state["top_blockers"] = blockers

    if data.get("calibrated_market") is False:
        state["calibrated_market"] = False
    elif "calibrated_market" not in state:
        state["calibrated_market"] = True

    _atomic_json(path, state)


def call(path, body=None, method=None, profile="full_advisory", timeout=120, idempotency_key=None):
    """Returns (latency_s, status, parsed_json). 4xx bodies are returned, not raised —
    kernel validation errors are compiler diagnostics and callers must read them."""
    method = method or ("POST" if body is not None else "GET")
    headers = {
        "X-API-Key": _key(),
        "Content-Type": "application/json",
        "User-Agent": UA,
        "X-Response-Profile": profile,
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method=method,
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return round(time.time() - t0, 2), r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return round(time.time() - t0, 2), e.code, json.loads(raw)
        except Exception:
            return round(time.time() - t0, 2), e.code, {"error": "non_json_response", "raw": raw[:500]}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # OFFLINE / OUTAGE: never crash the host. Status 0 = no HTTP response.
        # Doctrine (CLAUDE.md Section 7, Outage Rule): building proceeds, charters are
        # marked provisional, claims stay default-denied (no fresh log entry = gate
        # fails closed, which is correct). NEVER simulate a verdict locally - an
        # offline spine that invents answers is a counterfeit spine.
        return round(time.time() - t0, 2), 0, {
            "error": "kernel_unreachable",
            "detail": str(getattr(e, "reason", e))[:200],
            "outage_rule": "Build proceeds; charter provisional; claim authorization impossible until the kernel is reachable. Do not simulate verdicts locally.",
        }


# ---- Checkpoint calls (see checkpoints.md for when each is MANDATORY) ----

def category_playbook(archetype):
    """Pre-charter, always. Evidence demand schedule, guardian map (incl. veto holders),
    failure modes, board questions. ~0.2s, static."""
    result = call(f"/v1/category-playbook/{archetype}")
    if result[1] == 200:
        update_state(f"/v1/category-playbook/{archetype}", result[2])
    return result


def strategy_sparring(claims, subject, market_scope):
    """Pre-charter, always. Deterministic red-team of the Advocate's claims.
    Quote outputs verbatim in the charter; never paraphrase away unsafe_claims."""
    result = call("/v1/strategy-sparring", {
        "claims": claims[:10], "subject": subject, "market_scope": market_scope,
    })
    if result[1] == 200:
        update_state("/v1/strategy-sparring", result[2])
    return result


def decision_check(payload):
    """Whenever any evidence pack exists; mandatory pre-claim. Abstention codes are the
    next-blocker ladder — they are the product, not an error."""
    result = call("/v1/decision-check", payload)
    if result[1] == 200:
        update_state("/v1/decision-check", result[2])
    return result


def evidence_completeness(payload):
    """Pre-claim companion: what is missing before the requested decision level."""
    result = call("/v1/evidence-completeness", payload)
    if result[1] == 200:
        update_state("/v1/evidence-completeness", result[2])
    return result


def request_attestation(project_id, signal_type, country, target_stakeholder, questions, region=None):
    """Create a consented field-signal request.

    Store the returned field_signal_request_id in the relevant Operator Passport
    counterparty's attestation_ref. Do not add unadvertised passport_id or
    counterparty_id fields to this payload until the API contract exposes them.
    """
    payload = {
        "project_id": project_id,
        "signal_type": signal_type,
        "country": country,
        "target_stakeholder": target_stakeholder,
        "questions": questions,
    }
    if region:
        payload["region"] = region
    return call(
        "/v1/field-signal/request",
        payload,
        idempotency_key=f"fsr-{uuid.uuid4()}",
    )


def submit_field_signal(field_signal_request_id, respondent_type, responses, consent_confirmed=True):
    """Submit respondent answers as pending-review evidence candidates."""
    return call(
        "/v1/field-signal/submit",
        {
            "field_signal_request_id": field_signal_request_id,
            "respondent_type": respondent_type,
            "consent_confirmed": bool(consent_confirmed),
            "responses": responses,
        },
        idempotency_key=f"fss-{uuid.uuid4()}",
    )


def get_attestation_status(request_id):
    """Refuse to invent a status route.

    v6.32.0 advertises /v1/field-signal/request and /v1/field-signal/submit,
    but no field-signal status endpoint. Use the tenant/admin channel until the
    API publishes a status route.
    """
    raise SpineError(
        f"No public field-signal status route is advertised for {request_id!r}. "
        "Check tenant/admin records or add an official status endpoint before automating this."
    )


def schema():
    """Auth + liveness probe (auth-check is currently unregistered upstream)."""
    return call("/v1/schema")
