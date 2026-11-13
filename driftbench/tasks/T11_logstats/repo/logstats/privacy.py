"""Privacy helpers used before sharing reports outside the ops team."""
from __future__ import annotations

import dataclasses
import hashlib

from .parser import LogRecord


def anonymize_ip(ip: str) -> str:
    """Zero the last octet of an IPv4 address: ``203.0.113.7 -> 203.0.113.0``."""
    parts = ip.split(".")
    if len(parts) == 4:
        parts[-1] = "0"
        return ".".join(parts)
    return ip


def pseudonymize(value: str, salt: str) -> str:
    """A stable, non-reversible token for ``value`` (12 hex characters)."""
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:12]


def scrub(record: LogRecord, salt: str) -> LogRecord:
    """Return a copy of ``record`` with the IP anonymised and the user pseudonymised."""
    user = pseudonymize(record.user, salt) if record.user else None
    return dataclasses.replace(record, ip=anonymize_ip(record.ip), user=user)
