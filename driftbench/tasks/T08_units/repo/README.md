# units

A small, dependency-free unit-conversion library: dimensions as products of base quantities,
a registry of units with conversion factors, `Quantity` values, rounding helpers and
human-friendly formatting with SI prefixes.

```python
from units import Quantity, convert

convert(5, "km", "mi")          # 3.1068...
Quantity(90, "min").to("h")     # Quantity(value=1.5, unit='h')
```

Run the tests with `python -m pytest`.
