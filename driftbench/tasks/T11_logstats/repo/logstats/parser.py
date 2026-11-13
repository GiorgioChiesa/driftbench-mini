"""Parse access-log lines in the Combined Log Format plus a trailing request time.

Example line (the last field is nginx's ``$request_time`` in seconds, ``-`` when unknown)::

    203.0.113.7 - alice [10/Oct/2023:13:55:36 +0200] "GET /api/users/42?full=1 HTTP/1.1" 200 2326 "https://example.com/" "Mozilla/5.0" 0.042
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .timeutil import parse_clf_time

_LINE = re.compile(
    r'^(?P<ip>[\d.]+) (?P<ident>\S+) (?P<user>\S+) \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d{3}) (?P<size>\d+|-)'
    r'(?: "(?P<referer>[^"]*)" "(?P<agent>[^"]*)")?(?: (?P<rt>[\d.]+|-))?$'
)


class ParseError(ValueError):
    def __init__(self, line: str, lineno: int | None = None):
        where = f"line {lineno}: " if lineno is not None else ""
        super().__init__(f"{where}cannot parse {line[:80]!r}")
        self.line = line
        self.lineno = lineno


@dataclass(frozen=True)
class LogRecord:
    ip: str
    user: str | None
    time: datetime
    method: str
    path: str
    protocol: str
    status: int
    size: int
    referer: str | None = None
    agent: str | None = None
    duration_ms: float | None = None  # request time in milliseconds, None when not logged


def _dash(value: str | None) -> str | None:
    return None if value in (None, "", "-") else value


def _seconds_to_ms(raw: str | None) -> float | None:
    if raw in (None, "-"):
        return None
    return round(float(raw) * 1000, 3)


def parse_line(line: str) -> LogRecord:
    m = _LINE.match(line.strip())
    if not m:
        raise ParseError(line)
    return LogRecord(
        ip=m["ip"], user=_dash(m["user"]), time=parse_clf_time(m["time"]), method=m["method"],
        path=m["path"], protocol=m["protocol"], status=int(m["status"]),
        size=0 if m["size"] == "-" else int(m["size"]), referer=_dash(m["referer"]),
        agent=_dash(m["agent"]), duration_ms=_seconds_to_ms(m["rt"]),
    )


def parse_lines(lines: Iterable[str], strict: bool = False) -> list[LogRecord]:
    """Parse many lines, skipping blank ones. Malformed lines are skipped unless ``strict``."""
    records = []
    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            records.append(parse_line(line))
        except (ParseError, ValueError, KeyError) as exc:
            if strict:
                raise ParseError(line, lineno) from exc
    return records


def parse_file(path, strict: bool = False) -> list[LogRecord]:
    with Path(path).open(encoding="utf-8", errors="replace") as fh:
        return parse_lines(fh, strict=strict)
