"""String-to-value coercion for configuration fields."""
from __future__ import annotations

from typing import Any, Callable

_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise ValueError(f"not a boolean: {value!r}")


def to_int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError(f"not an integer: {value!r}")
    if isinstance(value, int):
        return value
    return int(str(value).strip())


def to_float(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError(f"not a number: {value!r}")
    return float(str(value).strip())


def to_str(value: Any) -> str:
    return str(value)


def to_list(value: Any) -> list[str]:
    """Comma-separated text (or a list) to a list of stripped, non-empty strings."""
    parts = value if isinstance(value, (list, tuple)) else str(value).split(",")
    return [str(part).strip() for part in parts if str(part).strip()]


COERCERS: dict[str, Callable[[Any], Any]] = {
    "str": to_str,
    "int": to_int,
    "float": to_float,
    "bool": to_bool,
    "list": to_list,
}


def coerce(type_name: str, value: Any) -> Any:
    """Convert ``value`` to the field type ``type_name``; raises ``ValueError`` on bad input."""
    try:
        func = COERCERS[type_name]
    except KeyError:
        raise ValueError(f"unknown field type: {type_name!r}") from None
    return func(value)
