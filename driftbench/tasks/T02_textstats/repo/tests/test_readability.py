from textstats.readability import count_sentences, syllables


def test_count_sentences():
    assert count_sentences("One. Two! Three?") == 3


def test_syllables():
    assert syllables("cat") == 1
    assert syllables("table") == 1 or syllables("table") == 2
