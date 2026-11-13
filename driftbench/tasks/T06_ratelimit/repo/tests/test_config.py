import pytest

from ratelimit import Rate, parse_rate


@pytest.mark.parametrize("spec, expected", [
    ("10/min", Rate(10, 60.0)),
    ("5/s", Rate(5, 1.0)),
    ("5/30s", Rate(5, 30.0)),
    ("100 / h", Rate(100, 3600.0)),
    ("3/1.5s", Rate(3, 1.5)),
    ("7/DAY", Rate(7, 86400.0)),
])
def test_parse_rate(spec, expected):
    assert parse_rate(spec) == expected


@pytest.mark.parametrize("spec", ["", "10", "ten/min", "10/fortnight", "0/s", "5/0s"])
def test_parse_rate_rejects(spec):
    with pytest.raises(ValueError):
        parse_rate(spec)


def test_per_second():
    assert parse_rate("120/min").per_second == 2.0
