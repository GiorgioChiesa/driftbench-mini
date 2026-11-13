"""Group requests into endpoints: the method plus a path template.

``GET /api/users/42?full=1`` and ``GET /api/users/7/`` both belong to ``GET /api/users/{id}``:
numeric segments and UUIDs are replaced by ``{id}`` and the query string is dropped.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

_ID = re.compile(r"^(?:\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", re.IGNORECASE)
STATIC_SUFFIXES = (".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff2")


def path_template(path: str) -> str:
    raw = urlsplit(path).path
    segments = ["{id}" if _ID.match(s) else s for s in raw.split("/") if s]
    return "/" + "/".join(segments)


def endpoint_key(record) -> str:
    """The endpoint a record belongs to, e.g. ``'GET /api/users/{id}'``."""
    return f"{record.method} {path_template(record.path)}"


def is_static_asset(path: str) -> bool:
    return urlsplit(path).path.lower().endswith(STATIC_SUFFIXES)
