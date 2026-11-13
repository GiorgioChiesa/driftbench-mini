"""Plain-text rendering of log summaries."""
from __future__ import annotations

from typing import Sequence

from . import stats


def format_bytes(n: int) -> str:
    """Human-readable size: ``512 B``, ``1.5 KB``, ``3.2 MB`` (1 KB = 1024 B)."""
    value = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{int(value)} B" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def format_ms(ms: float | None) -> str:
    if ms is None:
        return "-"
    return f"{ms / 1000:.2f} s" if ms >= 1000 else f"{ms:.1f} ms"


def render_table(headers: Sequence[str], rows: Sequence[Sequence]) -> str:
    """Left-aligned columns separated by `` | `` with a dashed rule under the header."""
    widths = [max(len(str(h)), *(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
    lines = [" | ".join(str(h).ljust(w) for h, w in zip(headers, widths)).rstrip()]
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(" | ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())
    return "\n".join(lines)


def summary_text(records) -> str:
    records = list(records)
    lines = [f"Requests: {len(records)}", f"Transferred: {format_bytes(stats.total_bytes(records))}", ""]
    lines.append(render_table(["status", "count"], list(stats.count_by_status(records).items())))
    lines.append("")
    lines.append(render_table(["ip", "requests"], stats.top_ips(records)))
    return "\n".join(lines)
