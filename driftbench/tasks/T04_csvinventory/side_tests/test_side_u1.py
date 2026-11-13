from inventory import Item, Ledger


def test_u1_history_kind_filter():
    ledger = Ledger([Item("B-200", "Bolt", on_hand=10)])
    ledger.receive("B-200", 5)
    ledger.ship("B-200", 3)
    ledger.ship("B-200", 2)
    assert [m.quantity for m in ledger.history("B-200", kind="ship")] == [3, 2]
    assert [m.kind for m in ledger.history(kind="receive")] == ["receive"]
