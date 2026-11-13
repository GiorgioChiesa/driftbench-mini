import pytest

from todostore.models import Todo
from todostore.tags import normalize_tag, normalize_tags, parse_tags, tag_counts


def test_normalize_tag():
    assert normalize_tag("  Home Office ") == "home-office"


def test_normalize_tag_rejects_symbols():
    with pytest.raises(ValueError):
        normalize_tag("a/b")


def test_parse_tags_skips_empty_parts():
    assert parse_tags("work, ,Errands,") == ["work", "errands"]


def test_normalize_tags_keeps_order():
    assert normalize_tags(["b", "A"]) == ["b", "a"]


def test_tag_counts():
    todos = [Todo(1, "a", tags=["x", "y"]), Todo(2, "b", tags=["y"]), Todo(3, "c", tags=["w"])]
    assert list(tag_counts(todos).items()) == [("y", 2), ("w", 1), ("x", 1)]
