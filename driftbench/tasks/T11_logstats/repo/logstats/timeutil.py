"""Timestamp helpers for access logs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

MONTHS = {name: i for i, name in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}


def parse_clf_time(value: str) -> datetime:
    """Parse a CLF timestamp such as ``10/Oct/2023:13:55:36 +0200`` into an aware datetime."""
    stamp, _, tz = value.strip().partition(" ")
    date, hh, mm, ss = stamp.split(":")
    day, mon, year = date.split("/")
    offset = timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5]))
    if tz[0] == "-":
        offset = -offset
    return datetime(int(year), MONTHS[mon], int(day), int(hh), int(mm), int(ss), tzinfo=timezone(offset))


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp (``Z`` means UTC). Timestamps without an offset are rejected."""
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp has no timezone: {value!r}")
    return dt


def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)


def floor_minute(dt: datetime) -> datetime:
    """Truncate ``dt`` to the start of its minute, in UTC."""
    return to_utc(dt).replace(second=0, microsecond=0)
