"""Render rows as a GitHub-flavoured Markdown table."""
from __future__ import annotations

from typing import Any, Iterable, Sequence

from .numfmt import format_number, is_number
from .textutil import display_width, pad, truncate

MIN_WIDTH = 3


def _text(value: Any, decimals: int | None = None) -> str:
    if value is None:
        return ""
    if decimals is not None and is_number(value):
        return format_number(value, decimals)
    return str(value)


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\r\n", "\n").replace("\n", "<br>")


def _prepare(value: Any, decimals: int | None, max_width: int | None) -> str:
    text = _text(value, decimals)
    if max_width is not None:
        text = truncate(text, max_width)
    return _escape(text)


def _separator(width: int, align: str | None) -> str:
    if align == "l":
        return ":" + "-" * (width - 1)
    if align == "r":
        return "-" * (width - 1) + ":"
    if align == "c":
        return ":" + "-" * (width - 2) + ":"
    return "-" * width


def _line(cells: Sequence[str], widths: Sequence[int], aligns: Sequence[str]) -> str:
    return "| " + " | ".join(pad(c, w, a) for c, w, a in zip(cells, widths, aligns)) + " |"


def render_table(
    headers: Sequence[Any],
    rows: Iterable[Sequence[Any]],
    align: str | None = None,
    decimals: int | None = None,
    max_width: int | None = None,
) -> str:
    """Render ``headers`` and ``rows`` as a Markdown table.

    Short rows are padded with empty cells; a row with more cells than headers is an error.
    Every column is at least ``MIN_WIDTH`` display columns wide.
    """
    header = [_prepare(h, None, max_width) for h in headers]
    if not header:
        raise ValueError("a table needs at least one column")
    if align is not None and (len(align) != len(header) or set(align) - set("lrc")):
        raise ValueError(f"align must have one of 'l', 'r', 'c' per column, got {align!r}")
    aligns = list(align) if align is not None else ["l"] * len(header)
    body = []
    for row in rows:
        cells = [_prepare(v, decimals, max_width) for v in row]
        if len(cells) > len(header):
            raise ValueError(f"row has {len(cells)} cells, expected at most {len(header)}")
        body.append(cells + [""] * (len(header) - len(cells)))
    widths = [
        max([MIN_WIDTH, display_width(h)] + [display_width(r[i]) for r in body])
        for i, h in enumerate(header)
    ]
    seps = [_separator(w, align and a) for w, a in zip(widths, aligns)]
    lines = [_line(header, widths, aligns), _line(seps, widths, aligns)]
    lines += [_line(r, widths, aligns) for r in body]
    return "\n".join(lines)


class Table:
    """Incrementally built table: ``Table(["a", "b"]).add_row(1, 2).render()``."""

    def __init__(
        self,
        headers: Sequence[Any],
        align: str | None = None,
        decimals: int | None = None,
        max_width: int | None = None,
    ) -> None:
        self.headers = list(headers)
        self.align = align
        self.decimals = decimals
        self.max_width = max_width
        self.rows: list[list[Any]] = []

    def add_row(self, *cells: Any) -> "Table":
        self.rows.append(list(cells))
        return self

    def __len__(self) -> int:
        return len(self.rows)

    def render(self) -> str:
        return render_table(
            self.headers, self.rows, align=self.align, decimals=self.decimals, max_width=self.max_width
        )
