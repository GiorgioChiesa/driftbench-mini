import pytest


def test_r1_temperatures():
    from units.dimensions import TEMPERATURE
    from units.registry import DEFAULT, convert

    assert convert(100, "C", "F") == pytest.approx(212, abs=1e-9)
    assert convert(0, "C", "K") == pytest.approx(273.15, abs=1e-9)
    assert convert(-40, "F", "C") == pytest.approx(-40, abs=1e-9)
    assert convert(32, "F", "K") == pytest.approx(273.15, abs=1e-9)
    assert convert(300, "K", "C") == pytest.approx(26.85, abs=1e-9)
    assert DEFAULT.get("C").dimension == TEMPERATURE
    assert DEFAULT.get("C").offset == pytest.approx(273.15)
    assert DEFAULT.get("km").offset == 0.0


def test_r2_compound_units():
    from units.dimensions import VELOCITY
    from units.registry import DEFAULT, convert

    assert convert(36, "km/h", "m/s") == pytest.approx(10, abs=1e-9)
    assert convert(1, "m/s", "km/h") == pytest.approx(3.6, abs=1e-9)
    assert convert(60, "mi/h", "km/h") == pytest.approx(96.56064, abs=1e-9)
    unit = DEFAULT.get("km/h")
    assert unit.dimension == VELOCITY
    assert unit.factor == pytest.approx(1000 / 3600)
    assert convert(2, "g/cm", "kg/m") == pytest.approx(0.2, abs=1e-9)


def test_r3_incompatible():
    from units.registry import IncompatibleUnits, convert

    with pytest.raises(IncompatibleUnits):
        convert(1, "km/h", "m")
    with pytest.raises(IncompatibleUnits):
        convert(1, "m", "km/h")
    with pytest.raises(IncompatibleUnits):
        convert(1, "C", "m")
    with pytest.raises(IncompatibleUnits):
        convert(1, "km/h", "kg/s")
    with pytest.raises(IncompatibleUnits):
        convert(1, "C/s", "K/s")


def test_r4_parse():
    from units.quantity import Quantity
    from units.registry import parse

    assert parse("3.5 km") == Quantity(3.5, "km")
    assert parse("-2 m/s") == Quantity(-2.0, "m/s")
    assert parse("10km") == Quantity(10.0, "km")
    assert parse("1e3 m") == Quantity(1000.0, "m")
    assert parse("  20 C ") == Quantity(20.0, "C")
    assert isinstance(parse("7 s").value, float)


def test_r5_errors():
    from units.registry import DEFAULT, UnknownUnit, convert, parse

    for call in (lambda: parse("3 parsec"), lambda: DEFAULT.get("parsec"), lambda: convert(1, "parsec", "m")):
        with pytest.raises(UnknownUnit) as info:
            call()
        assert "parsec" in str(info.value)
    with pytest.raises(UnknownUnit) as info:
        convert(1, "km/fortnight", "m/s")
    assert "fortnight" in str(info.value)
    for bad in ["", "3.5", "km 3", "three km"]:
        with pytest.raises(ValueError):
            parse(bad)


def test_r6_parsed_quantities_convert():
    from units.registry import parse

    q = parse("36 km/h").to("m/s")
    assert q.unit == "m/s"
    assert q.value == pytest.approx(10.0, abs=1e-9)
    assert parse("100 C").to("F").value == pytest.approx(212, abs=1e-9)
