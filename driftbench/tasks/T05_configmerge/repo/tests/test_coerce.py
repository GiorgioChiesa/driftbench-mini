import pytest

from appconfig.coerce import coerce, to_bool, to_int, to_list


@pytest.mark.parametrize("raw", ["1", "true", "Yes", " on "])
def test_truthy(raw):
    assert coerce("bool", raw) is True


@pytest.mark.parametrize("raw", ["0", "false", "NO", "off"])
def test_falsy(raw):
    assert coerce("bool", raw) is False


def test_bool_rejects_garbage():
    with pytest.raises(ValueError):
        to_bool("maybe")


def test_int():
    assert to_int(" 42 ") == 42
    with pytest.raises(ValueError):
        to_int("4.2")
    with pytest.raises(ValueError):
        to_int(True)


def test_list():
    assert to_list("a, b,,c ") == ["a", "b", "c"]
    assert coerce("list", "") == []


def test_unknown_type():
    with pytest.raises(ValueError):
        coerce("date", "2024-01-01")
