from logstats import report


def test_format_bytes():
    assert report.format_bytes(512) == "512 B"
    assert report.format_bytes(1536) == "1.5 KB"
    assert report.format_bytes(3 * 1024 ** 2) == "3.0 MB"


def test_format_ms():
    assert report.format_ms(None) == "-"
    assert report.format_ms(42) == "42.0 ms"
    assert report.format_ms(1250) == "1.25 s"


def test_render_table():
    out = report.render_table(["name", "n"], [("alpha", 1), ("b", 22)])
    assert out.splitlines() == ["name  | n", "------+---", "alpha | 1", "b     | 22"]


def test_summary_text(records):
    text = report.summary_text(records)
    assert text.startswith("Requests: 4\nTransferred: 2.4 KB")
    assert "203.0.113.7  | 2" in text
