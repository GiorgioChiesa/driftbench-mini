"""Render rows as a GitHub-flavoured Markdown table."""
from __future__ import annotations

from typing import Any, Iterable, Sequence

from .textutil import display_width, pad

MIN_WIDTH = 3


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _line(cells: Sequence[str], widths: Sequence[int]) -> str:
    return "| " + " | ".join(pad(c, w) for c, w in zip(cells, widths)) + " |"


def render_table(headers: Sequence[Any], rows: Iterable[Sequence[Any]]) -> str:
    """Render ``headers`` and ``rows`` as a Markdown table.

    Short rows are padded with empty cells; a row with more cells than headers is an error.
    Every column is at least ``MIN_WIDTH`` display columns wide.
    """
    header = [_text(h) for h in headers]
    if not header:
        raise ValueError("a table needs at least one column")
    body = []
    for row in rows:
        cells = [_text(v) for v in row]
        if len(cells) > len(header):
            raise ValueError(f"row has {len(cells)} cells, expected at most {len(header)}")
        body.append(cells + [""] * (len(header) - len(cells)))
    widths = [
        max([MIN_WIDTH, display_width(h)] + [display_width(r[i]) for r in body])
        for i, h in enumerate(header)
    ]
    lines = [_line(header, widths), _line(["-" * w for w in widths], widths)]
    lines += [_line(r, widths) for r in body]
    return "\n".join(lines)


class Table:
    """Incrementally built table: ``Table(["a", "b"]).add_row(1, 2).render()``."""

    def __init__(self, headers: Sequence[Any]) -> None:
        self.headers = list(headers)
        self.rows: list[list[Any]] = []

    def add_row(self, *cells: Any) -> "Table":
        self.rows.append(list(cells))
        return self

    def __len__(self) -> int:
        return len(self.rows)

    def render(self) -> str:
        return render_table(self.headers, self.rows)
