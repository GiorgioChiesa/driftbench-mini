"""Human-readable dumps of a configuration, with secrets masked."""
from __future__ import annotations

from typing import Any, Mapping

from .schema import Schema, secret_keys

MASK = "***"


def redact(config: Mapping[str, Any], schema: Schema) -> dict[str, Any]:
    """Copy of ``config`` where non-empty values of secret fields are replaced by ``***``."""
    secret = secret_keys(schema)
    return {key: (MASK if key in secret and value not in (None, "") else value) for key, value in config.items()}


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(part) for part in value)
    if value is None:
        return ""
    return str(value)


def render(config: Mapping[str, Any]) -> str:
    """``key = value`` lines, sorted by key."""
    return "\n".join(f"{key} = {format_value(config[key])}" for key in sorted(config))
