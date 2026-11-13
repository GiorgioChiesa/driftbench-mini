from mdtable.csvio import parse_csv, to_csv


def test_u3_to_csv_roundtrip():
    text = to_csv(["name", "qty"], [["apple, red", 3], ["kiwi", None]])
    assert text.splitlines() == ["name,qty", '"apple, red",3', "kiwi,"]
    assert parse_csv(text) == (["name", "qty"], [["apple, red", 3], ["kiwi", None]])
