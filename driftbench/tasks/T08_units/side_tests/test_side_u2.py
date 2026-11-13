from units.formatting import humanize


def test_u2_tera_prefix():
    assert humanize(2.5e12, "B") == "2.5 TB"
