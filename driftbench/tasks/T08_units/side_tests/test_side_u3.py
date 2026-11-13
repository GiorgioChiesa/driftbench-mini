from units.rounding import format_sig


def test_u3_format_sig_keeps_trailing_zeros():
    assert format_sig(2.0, 3) == "2.00"
    assert format_sig(123456, 2) == "120000"
    assert format_sig(0.0012345, 3) == "0.00123"
