from decimal import Decimal

import pytest


def test_r1_separator_alignment():
    from mdtable.table import render_table

    assert render_table(["a", "b", "c"], [[1, 2, 3]], align="lrc").splitlines()[1] == "| :-- | --: | :-: |"
    assert render_table(["Name", "Qty"], [["apple", 10]], align="cr").splitlines()[1] == "| :---: | --: |"
    assert render_table(["x"], [["y"]]).splitlines()[1] == "| --- |"
    for bad in ["lr", "lrcl", "lrx", "LRC"]:
        with pytest.raises(ValueError):
            render_table(["a", "b", "c"], [], align=bad)


def test_r2_cell_padding():
    from mdtable.table import render_table

    out = render_table(["Item", "Qty", "Note"], [["pen", 3, "ok"], ["notebook", 12, "x"]], align="lrc")
    assert out.splitlines() == [
        "| Item     | Qty | Note |",
        "| :------- | --: | :--: |",
        "| pen      |   3 |  ok  |",
        "| notebook |  12 |  x   |",
    ]
    assert render_table(["名前"], [["ab"]], align="c").splitlines() == ["| 名前 |", "| :--: |", "|  ab  |"]
    assert render_table(["a", "b"], [["x", "y"]]).splitlines()[2] == "| x   | y   |"


def test_r3_decimals():
    from mdtable.table import render_table

    rows = [[2.675], [2], [Decimal("1.005")], [True], [None], ["7"]]
    assert render_table(["v"], rows, decimals=2).splitlines()[2:] == [
        "| 2.68 |", "| 2.00 |", "| 1.01 |", "| True |", "|      |", "| 7    |",
    ]
    assert render_table(["v"], [[2.5]], decimals=0).splitlines()[2] == "| 3   |"
    assert render_table(["v"], [[2.5], [False]]).splitlines()[2:] == ["| 2.5   |", "| False |"]


def test_r4_escaping():
    from mdtable.table import render_table

    out = render_table(["a|b"], [["x|y"], ["line1\nline2"], ["p\r\nq"]]).splitlines()
    assert out == [
        "| a\\|b           |",
        "| -------------- |",
        "| x\\|y           |",
        "| line1<br>line2 |",
        "| p<br>q         |",
    ]


def test_r5_max_width():
    from mdtable.table import render_table

    rows = [["abcdefgh", 1], ["abcde", 2], ["名前名前", 3]]
    assert render_table(["Description", "n"], rows, max_width=5).splitlines() == [
        "| Desc… | n   |",
        "| ----- | --- |",
        "| abcd… | 1   |",
        "| abcde | 2   |",
        "| 名前… | 3   |",
    ]
    assert render_table(["v"], [["a|bcdef"]], max_width=4).splitlines()[2] == "| a\\|b… |"


def test_r6_table_options():
    from mdtable.table import Table

    t = Table(["n", "v"], align="lr", decimals=1, max_width=4)
    assert (t.align, t.decimals, t.max_width) == ("lr", 1, 4)
    t.add_row("abcdef", 3)
    assert t.render().splitlines() == ["| n    |   v |", "| :--- | --: |", "| abc… | 3.0 |"]
    assert Table(["n"]).add_row(2.5).render().splitlines()[2] == "| 2.5 |"
