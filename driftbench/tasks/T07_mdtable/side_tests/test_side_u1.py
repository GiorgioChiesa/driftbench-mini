from mdtable.csvio import parse_csv


def test_u1_blank_lines_are_skipped():
    headers, rows = parse_csv("a,b\n1,2\n\n3,4\n\n")
    assert headers == ["a", "b"]
    assert rows == [[1, 2], [3, 4]]
