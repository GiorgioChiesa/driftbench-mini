"""Path helpers shared by the router and the app."""
from __future__ import annotations

from urllib.parse import quote, unquote, urlencode


def normalize_path(path: str) -> str:
    """Return the canonical form of a request path.

    The query string and fragment are dropped, repeated slashes are collapsed and the trailing
    slash is removed (the root stays ``/``).
    """
    path = path.split("#", 1)[0].split("?", 1)[0]
    parts = [p for p in path.split("/") if p]
    return "/" + "/".join(parts)


def split_path(path: str) -> list[str]:
    """Split a path into percent-decoded segments: ``'/a/b%20c' -> ['a', 'b c']``."""
    normalized = normalize_path(path)
    if normalized == "/":
        return []
    return [unquote_segment(s) for s in normalized[1:].split("/")]


def quote_segment(value) -> str:
    """Percent-encode a single path segment (a ``/`` inside the value is encoded too)."""
    return quote(str(value), safe="")


def unquote_segment(segment: str) -> str:
    """Decode a single percent-encoded path segment."""
    return unquote(segment)


def build_query(params: dict) -> str:
    """Encode ``params`` as a query string with keys in sorted order ('' when empty)."""
    if not params:
        return ""
    return urlencode(sorted(params.items()))


def join_path(*segments) -> str:
    """Join already-encoded segments into a normalized path."""
    return normalize_path("/" + "/".join(str(s).strip("/") for s in segments))
