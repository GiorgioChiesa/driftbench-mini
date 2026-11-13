from textstats.counter import unique_words, word_counts


def test_word_counts():
    assert word_counts("a b a")["a"] == 2


def test_unique_words():
    assert unique_words("b a b") == ["a", "b"]
