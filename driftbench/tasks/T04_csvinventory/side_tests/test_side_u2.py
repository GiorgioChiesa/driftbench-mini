from inventory.validation import validate_sku


def test_u2_lowercase_sku_is_normalised():
    assert validate_sku("ab-1234") == "AB-1234"
    assert validate_sku(" w-110 ") == "W-110"
