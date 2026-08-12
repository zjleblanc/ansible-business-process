# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Zachary LeBlanc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared Gmail helpers for the business.google collection.

Provides Gmail search-query construction and message parsing so every
module in this collection that reads Gmail messages behaves consistently.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import re

WHITESPACE_RE = re.compile(r"\s")


def _quote_term(value):
    """Quote a query term for Gmail search if it contains whitespace."""
    value = str(value)
    if value.startswith('"') and value.endswith('"'):
        return value
    if WHITESPACE_RE.search(value):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def build_query(from_addr=None, to=None, subject=None, labels=None,
                 after=None, before=None, query=None):
    """Assemble a Gmail search query string from convenience filters.

    Each provided filter is ANDed together (Gmail's default search
    behavior). Any raw `query` is appended last so advanced users can
    combine hand-written search operators with the convenience filters.
    """
    clauses = []

    if from_addr:
        clauses.append(f"from:{_quote_term(from_addr)}")
    if to:
        clauses.append(f"to:{_quote_term(to)}")
    if subject:
        clauses.append(f"subject:{_quote_term(subject)}")
    for label in labels or []:
        clauses.append(f"label:{_quote_term(label)}")
    if after:
        clauses.append(f"after:{after}")
    if before:
        clauses.append(f"before:{before}")
    if query:
        clauses.append(query)

    return " ".join(clauses)


def get_header(headers, name):
    """Return the value of a header by name (case-insensitive), or None."""
    if not headers:
        return None
    name_lower = name.lower()
    for header in headers:
        if header.get("name", "").lower() == name_lower:
            return header.get("value")
    return None


def _decode_base64url(data):
    """Decode a Gmail base64url-encoded body part into text."""
    if not data:
        return None
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return None


def _extract_body(payload):
    """Recursively find and decode a message body, preferring text/plain."""
    if not payload:
        return None

    mime_type = payload.get("mimeType", "")
    data = (payload.get("body") or {}).get("data")
    if data and mime_type in ("text/plain", "text/html"):
        return _decode_base64url(data)

    plain_text = None
    html_text = None
    for part in payload.get("parts") or []:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain" and plain_text is None:
            plain_text = _extract_body(part)
        elif part_mime == "text/html" and html_text is None:
            html_text = _extract_body(part)
        elif part_mime.startswith("multipart/") and plain_text is None:
            plain_text = _extract_body(part)

    return plain_text if plain_text is not None else html_text


def parse_message(raw_msg, msg_format="metadata"):
    """Extract structured fields from a Gmail API message resource.

    Handles `minimal`, `metadata`, and `full` response formats gracefully;
    fields that aren't present in the requested format are simply None.
    """
    payload = raw_msg.get("payload") or {}
    headers = payload.get("headers") or []

    parsed = {
        "id": raw_msg.get("id"),
        "thread_id": raw_msg.get("threadId"),
        "label_ids": raw_msg.get("labelIds", []),
        "snippet": raw_msg.get("snippet"),
        "from": get_header(headers, "From"),
        "to": get_header(headers, "To"),
        "subject": get_header(headers, "Subject"),
        "date": get_header(headers, "Date"),
    }

    if msg_format == "full":
        parsed["body"] = _extract_body(payload)

    return parsed
