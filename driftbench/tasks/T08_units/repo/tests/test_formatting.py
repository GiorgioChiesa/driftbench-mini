from units import Quantity
from units.formatting import format_quantity, humanize, si_prefix


def test_si_prefix():
    assert si_prefix(1500) == (1.5, "k")
    assert si_prefix(2_500_000) == (2.5, "M")
    assert si_prefix(12) == (12, "")


def test_humanize():
    assert humanize(1500, "m") == "1.5 km"
    assert humanize(3.2e9, "B") == "3.2 GB"
    assert humanize(123456, "g", precision=2) == "1.2e+02 kg"


def test_format_quantity():
    assert format_quantity(Quantity(3.14159, "m")) == "3.14 m"
    assert format_quantity(Quantity(2, "s"), decimals=0) == "2 s"
