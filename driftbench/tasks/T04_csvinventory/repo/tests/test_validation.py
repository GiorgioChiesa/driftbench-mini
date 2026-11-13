import pytest

from inventory import Item
from inventory.validation import InvalidSku, find_duplicates, item_problems, validate_sku


def test_validate_sku():
    assert validate_sku("AB-1234") == "AB-1234"
    with pytest.raises(InvalidSku):
        validate_sku("AB1234")


def test_clean_item_has_no_problems(items):
    assert [item_problems(item) for item in items] == [[], [], [], []]


def test_item_problems():
    item = Item("bad", "Thing", on_hand=1, reserved=3, unit_cost="-1", reorder_qty=10)
    assert item_problems(item) == [
        "invalid SKU: 'bad'", "negative unit cost", "reserved exceeds on hand",
        "reorder_qty set without reorder_point"]


def test_find_duplicates():
    items = [Item("A-100", "a"), Item("B-200", "b"), Item("A-100", "c")]
    assert find_duplicates(items) == ["A-100"]
