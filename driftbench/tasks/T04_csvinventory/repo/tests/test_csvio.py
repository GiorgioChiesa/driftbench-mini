import pytest

from inventory.csvio import CsvFormatError, read_items, write_items, write_rows
from decimal import Decimal


def test_read_items(items):
    bolt = items[0]
    assert (bolt.sku, bolt.supplier, bolt.on_hand, bolt.reserved) == ("B-200", "Acme", 500, 20)
    assert bolt.unit_cost == Decimal("0.08")
    assert (bolt.reorder_point, bolt.reorder_qty) == (200, 1000)
    assert items[3].supplier == ""


def test_roundtrip(items, tmp_path):
    out = tmp_path / "out.csv"
    assert write_items(items, out) == 4
    assert read_items(out) == items


def test_write_rows_formats_decimals(tmp_path):
    out = tmp_path / "rows.csv"
    write_rows(out, ["a", "b"], [["x", Decimal("1.5")]])
    assert out.read_text().splitlines() == ["a,b", "x,1.50"]


def test_missing_required_value(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("sku,name,on_hand,unit_cost\nA-100,Thing,,1.00\n")
    with pytest.raises(CsvFormatError, match="line 2: missing on_hand"):
        read_items(path)


def test_unknown_column(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("sku,name,on_hand,unit_cost,colour\nA-100,Thing,1,1.00,red\n")
    with pytest.raises(CsvFormatError, match="unknown columns: colour"):
        read_items(path)
