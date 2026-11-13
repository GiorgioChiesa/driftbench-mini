import pytest

from mdtable import Table, render_table


def test_render_basic(fruit):
    headers, rows = fruit
    assert render_table(headers, rows).splitlines() == [
        "| Fruit  | Qty |",
        "| ------ | --- |",
        "| apple  | 3   |",
        "| banana | 12  |",
        "| kiwi   |     |",
    ]


def test_short_rows_are_padded():
    out = render_table(["a", "b"], [["x"]]).splitlines()
    assert out[2] == "| x   |     |"


def test_long_row_is_an_error():
    with pytest.raises(ValueError):
        render_table(["a"], [[1, 2]])


def test_no_columns():
    with pytest.raises(ValueError):
        render_table([], [])


def test_wide_characters_are_measured():
    out = render_table(["名前"], [["ab"]]).splitlines()
    assert out == ["| 名前 |", "| ---- |", "| ab   |"]


def test_table_builder():
    t = Table(["n"]).add_row(1).add_row(2)
    assert len(t) == 2
    assert t.render().splitlines()[-1] == "| 2   |"
