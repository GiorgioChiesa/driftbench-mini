from logstats import report


def test_u2_binary_units():
    assert report.format_bytes(1536) == "1.5 KiB"
    assert report.format_bytes(3 * 1024 ** 2) == "3.0 MiB"
    assert report.format_bytes(512) == "512 B"
