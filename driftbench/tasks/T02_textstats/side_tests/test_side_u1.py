import io
from textstats import cli


def test_u1_sentence_count(tmp_path):
    p = tmp_path / "s.txt"
    p.write_text("One cat. Two dogs! Three?", encoding="utf-8")
    out = io.StringIO()
    cli.main([str(p), "--readability"], out=out)
    assert "sentences\t3" in out.getvalue().splitlines()
