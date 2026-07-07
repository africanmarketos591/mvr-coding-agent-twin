"""Safe local key-file parsing for internal rehearsals.

Only explicit key-bearing fields are accepted. This prevents a human label such
as `mark-mvr-...` from being mistaken for the actual enterprise credential.
"""
import re


FIELD_PATTERNS = [
    re.compile(r"(?im)^\s*X-API-Key\s*:\s*([^\s#]+)"),
    re.compile(r"(?im)^\s*MVR_API_KEY\s*[:=]\s*([^\s#]+)"),
    re.compile(r"(?im)^\s*API_KEY\s*[:=]\s*([^\s#]+)"),
    re.compile(r"(?im)^\s*Authorization\s*:\s*Bearer\s+([^\s#]+)"),
]


def extract_mvr_api_key(text):
    """Return the first explicit key field from text.

    Deliberately does not fallback to arbitrary token scanning. A label is not a
    credential, and a hash is not a credential.
    """
    for pattern in FIELD_PATTERNS:
        match = pattern.search(text)
        if match:
            key = match.group(1).strip().strip('"').strip("'")
            if key:
                return key
    raise ValueError(
        "No explicit MVR key field found. Expected one of: X-API-Key:, "
        "MVR_API_KEY=, API_KEY=, or Authorization: Bearer <key>."
    )
