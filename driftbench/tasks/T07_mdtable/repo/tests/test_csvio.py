from mdtable.csvio import coerce, parse_csv, read_csv


def test_coerce():
    assert coerce(" 42 ") == 42
    assert coerce("-3.5") == -3.5
    assert coerce(".5") == 0.5
    assert coerce("") is None
    assert coerce("TRUE") is True
    assert coerce("kiwi") == "kiwi"


def test_parse_csv():
    headers, rows = parse_csv("name, qty\napple,3\nkiwi,\n")
    assert headers == ["name", "qty"]
    assert rows == [["apple", 3], ["kiwi", None]]


def test_parse_csv_raw():
    _, rows = parse_csv("a\n01\n", coerce_types=False)
    assert rows == [["01"]]


def test_read_csv(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("x,y\n1,2\n", encoding="utf-8")
    assert read_csv(p) == (["x", "y"], [[1, 2]])
