"""Render rows as a simple HTML ``<table>``."""
from __future__ import annotations

from html import escape
from typing import Any, Iterable, Sequence


def _cell(value: Any) -> str:
    return "" if value is None else escape(str(value), quote=False)


def render_html(headers: Sequence[Any], rows: Iterable[Sequence[Any]], caption: str | None = None) -> str:
    """Return an HTML table; cell contents are escaped, ``None`` becomes an empty cell."""
    lines = ["<table>"]
    if caption:
        lines.append(f"  <caption>{caption}</caption>")
    lines.append("  <tr>" + "".join(f"<th>{_cell(h)}</th>" for h in headers) + "</tr>")
    for row in rows:
        lines.append("  <tr>" + "".join(f"<td>{_cell(v)}</td>" for v in row) + "</tr>")
    lines.append("</table>")
    return "\n".join(lines)
