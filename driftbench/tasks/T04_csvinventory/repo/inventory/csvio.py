"""CSV import/export for inventory items."""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from typing import Iterable, Sequence

from .models import Item

COLUMNS = ("sku", "name", "supplier", "on_hand", "reserved", "unit_cost", "reorder_point", "reorder_qty")
REQUIRED = ("sku", "name", "on_hand", "unit_cost")


class CsvFormatError(ValueError):
    """Raised when an inventory CSV cannot be parsed."""


def _row_to_item(row: dict, line: int) -> Item:
    missing = [column for column in REQUIRED if not (row.get(column) or "").strip()]
    if missing:
        raise CsvFormatError(f"line {line}: missing {', '.join(missing)}")
    try:
        return Item(
            sku=row["sku"],
            name=row["name"].strip(),
            supplier=row.get("supplier") or "",
            on_hand=int(row["on_hand"]),
            reserved=int(row.get("reserved") or 0),
            unit_cost=Decimal(row["unit_cost"].strip()),
            reorder_point=int(row.get("reorder_point") or 0),
            reorder_qty=int(row.get("reorder_qty") or 0),
        )
    except (ValueError, InvalidOperation) as exc:
        raise CsvFormatError(f"line {line}: {exc}") from None


def read_items(path) -> list[Item]:
    """Load every item from an inventory CSV (header row required)."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        unknown = set(reader.fieldnames or ()) - set(COLUMNS)
        if unknown:
            raise CsvFormatError(f"unknown columns: {', '.join(sorted(unknown))}")
        return [_row_to_item(row, number) for number, row in enumerate(reader, start=2)]


def _cell(value) -> str:
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return str(value)


def write_rows(path, header: Sequence[str], rows: Iterable[Sequence]) -> int:
    """Write ``header`` and ``rows`` as CSV; returns the number of data rows written."""
    count = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for row in rows:
            writer.writerow([_cell(value) for value in row])
            count += 1
    return count


def write_items(items: Iterable[Item], path) -> int:
    """Export items with the standard column layout."""
    return write_rows(path, COLUMNS, ([getattr(item, column) for column in COLUMNS] for item in items))
