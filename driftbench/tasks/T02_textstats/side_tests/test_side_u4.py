from textstats.counter import unique_words


def test_u4_min_length():
    assert unique_words("a bb ccc bb", min_length=2) == ["bb", "ccc"]
    assert unique_words("a bb") == ["a", "bb"]
