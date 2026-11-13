# Package imports live inside each test so that every requirement is scored on its own: e.g. a
# broken `readability.py` (cascade c1) breaks `textstats.cli` but must not zero r1-r4.
import io

import pytest


def test_r1_sorting_and_ties():
    from textstats.counter import top_words
    assert top_words("b a b c a b", 2, stopwords=set()) == [("b", 3), ("a", 2)]
    assert top_words("z y x", 3, stopwords=set()) == [("x", 1), ("y", 1), ("z", 1)]


def test_r2_default_stopwords():
    from textstats.counter import top_words
    from textstats.stopwords import DEFAULT_STOPWORDS
    assert {"the", "a", "an", "and", "of", "to", "in", "is", "it"} <= set(DEFAULT_STOPWORDS)
    assert top_words("the cat and the dog the cat", 1) == [("cat", 2)]
    assert top_words("the the cat", 1, stopwords=set()) == [("the", 2)]


def test_r3_n_positive():
    from textstats.counter import top_words
    for bad in (0, -1):
        with pytest.raises(ValueError):
            top_words("a b", bad)


def test_r4_contractions():
    from textstats.tokenize import tokenize
    assert tokenize("Don't stop, it's fine") == ["don't", "stop", "it's", "fine"]


def test_r5_cli(tmp_path):
    from textstats import cli
    p = tmp_path / "t.txt"
    p.write_text("the cat sat\nthe cat ran\nthe dog\n", encoding="utf-8")
    out = io.StringIO()
    cli.main([str(p), "--top", "2"], out=out)
    lines = out.getvalue().splitlines()
    assert "cat\t2" in lines
    assert not any(l.startswith("the\t") for l in lines)
    out = io.StringIO()
    cli.main([str(p), "--top", "1", "--keep-stopwords"], out=out)
    assert "the\t3" in out.getvalue().splitlines()
