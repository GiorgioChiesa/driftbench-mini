"""Configuration loading."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .ini import read_ini
from .schema import Schema, validate_schema


def defaults(schema: Schema) -> dict[str, Any]:
    """The schema's default value for every key."""
    validate_schema(schema)
    return {key: field.default for key, field in schema.items()}


def load_file(path) -> dict[str, str]:
    """Raw ``section.key`` strings from an INI file (no merging, no coercion)."""
    return read_ini(Path(path))
