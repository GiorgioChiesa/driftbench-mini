from inventory import Item


def test_u4_item_str():
    assert str(Item("B-200", "Hex bolt M6", "Acme", on_hand=500)) == "B-200 Hex bolt M6 (500 on hand)"
