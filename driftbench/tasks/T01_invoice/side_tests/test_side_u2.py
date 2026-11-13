import json
from decimal import Decimal
from invoice import Invoice, LineItem, storage


def _keys_sorted(pairs):
    keys = [k for k, _ in pairs]
    assert keys == sorted(keys), keys
    return dict(pairs)


def test_u2_sorted_keys(tmp_path):
    inv = Invoice("S", "Cust")
    inv.add(LineItem("a", "a", 1, Decimal("1")))
    p = tmp_path / "x.json"
    storage.save(inv, p)
    # every JSON object (top level and line items) must have sorted keys; indentation is free
    json.loads(p.read_text(), object_pairs_hook=_keys_sorted)
