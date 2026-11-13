import io

from textstats import cli


def test_basic_counts(text_file):
    out = io.StringIO()
    assert cli.main([str(text_file)], out=out) == 0
    assert "words\t10" in out.getvalue().splitlines()
