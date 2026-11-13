import pytest

from mdtable.textutil import display_width, pad, truncate


def test_display_width():
    assert display_width("abc") == 3
    assert display_width("日本") == 4
    assert display_width("é") == 1


@pytest.mark.parametrize("align, expected", [("l", "ab   "), ("r", "   ab"), ("c", " ab  ")])
def test_pad(align, expected):
    assert pad("ab", 5, align) == expected


def test_pad_never_cuts():
    assert pad("abcdef", 3) == "abcdef"


def test_pad_rejects_unknown_alignment():
    with pytest.raises(ValueError):
        pad("x", 3, "j")


def test_truncate():
    assert truncate("hello world", 6) == "hello…"
    assert truncate("hello", 5) == "hello"
    assert truncate("日本語", 4) == "日…"


def test_truncate_too_narrow():
    with pytest.raises(ValueError):
        truncate("abc", 0)
