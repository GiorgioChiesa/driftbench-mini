from textstats.textio import read_text


def test_u2_bom(tmp_path):
    p = tmp_path / "b.txt"
    p.write_bytes(b"\xef\xbb\xbfhello")
    assert read_text(p) == "hello"
