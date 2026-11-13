import pytest

from units.dimensions import AREA, DIMENSIONLESS, LENGTH, TIME, VELOCITY, Dimension


def test_velocity():
    assert VELOCITY == Dimension(length=1, time=-1)
    assert VELOCITY.exponent("time") == -1


def test_algebra():
    assert AREA / LENGTH == LENGTH
    assert VELOCITY * TIME == LENGTH
    assert LENGTH / LENGTH == DIMENSIONLESS
    assert DIMENSIONLESS.is_dimensionless


def test_hash_and_repr():
    assert len({LENGTH, Dimension(length=1), TIME}) == 2
    assert repr(VELOCITY) == "Dimension(length=1, time=-1)"


def test_unknown_base():
    with pytest.raises(ValueError):
        Dimension(luminosity=1)
