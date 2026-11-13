"""Reading tabular data from CSV text, with light type coercion."""
from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any

_INT = re.compile(r"^[+-]?\d+$")
_FLOAT = re.compile(r"^[+-]?\d*\.\d+$")


def coerce(text: str) -> Any:
    """Turn a raw CSV field into ``None``, ``int``, ``float``, ``bool`` or a stripped string."""
    s = text.strip()
    if s == "":
        return None
    if _INT.match(s):
        return int(s)
    if _FLOAT.match(s):
        return float(s)
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    return s


def parse_csv(text: str, coerce_types: bool = True) -> tuple[list[str], list[list[Any]]]:
    """Split CSV ``text`` into ``(headers, rows)``; the first record is the header."""
    records = list(csv.reader(io.StringIO(text)))
    if not records:
        raise ValueError("empty CSV input")
    headers = [h.strip() for h in records[0]]
    rows = [[coerce(c) if coerce_types else c for c in rec] for rec in records[1:]]
    return headers, rows


def read_csv(path: str | Path, encoding: str = "utf-8", coerce_types: bool = True):
    """Read a CSV file; see :func:`parse_csv`."""
    return parse_csv(Path(path).read_text(encoding=encoding), coerce_types)
