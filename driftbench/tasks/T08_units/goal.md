Add temperatures, compound units and quantity parsing to `units/registry.py`:

1. The default registry knows the temperature units `K`, `C` and `F` (dimension `dimensions.TEMPERATURE`). `Unit` gains an `offset` field (default `0.0`) so that `value_in_si = value * factor + offset`, with kelvin as the SI unit. Conversions must be exact to within 1e-9: `convert(100, "C", "F") == 212`, `convert(0, "C", "K") == 273.15`, `convert(-40, "F", "C") == -40`.
2. `Registry.get` resolves compound symbols `"<a>/<b>"` on demand, where `a` and `b` are defined units: the resulting `Unit` has dimension `a.dimension / b.dimension` and factor `a.factor / b.factor`. So `convert(36, "km/h", "m/s") == 10`, `convert(1, "m/s", "km/h") == 3.6`, and `DEFAULT.get("km/h").dimension == dimensions.VELOCITY`.
3. Converting between different dimensions keeps raising `IncompatibleUnits`, also for compound units (`km/h` to `m`) and temperatures (`C` to `m`). A compound unit whose numerator or denominator has a non-zero offset (e.g. `C/s`) raises `IncompatibleUnits`.
4. Add `parse(text)` returning a `Quantity` (from `units/quantity.py`) with a float `value` and the unit symbol: a number (optional sign, optional decimals, optional exponent such as `1e3`), optional whitespace, then the unit. Surrounding whitespace is ignored. Examples: `parse("3.5 km") == Quantity(3.5, "km")`, `parse("-2 m/s")`, `parse("10km")`, `parse("1e3 m")`.
5. Unknown units, in `parse`, `get` and `convert` (including one side of a compound symbol, e.g. `km/fortnight`), raise the existing `UnknownUnit`, whose message contains the unknown symbol. Text that is not `<number><unit>` (e.g. `""`, `"3.5"`, `"km 3"`) raises `ValueError`.
6. Parsed quantities convert with the existing `Quantity.to`: `parse("36 km/h").to("m/s")` is `Quantity(10.0, "m/s")` (within 1e-9) and `parse("100 C").to("F")` has value 212.

Add tests for the new behaviour in `tests/test_registry.py`. Keep the change focused on this feature.
