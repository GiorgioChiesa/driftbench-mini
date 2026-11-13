"""Declarative description of the configuration keys an application accepts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .coerce import COERCERS

_KEY = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class Field:
    type: str = "str"
    default: Any = None
    secret: bool = False
    help: str = ""

    def __post_init__(self) -> None:
        if self.type not in COERCERS:
            raise ValueError(f"unknown field type: {self.type!r}")


Schema = dict[str, Field]


def validate_schema(schema: Schema) -> None:
    """Every key must look like ``section.name`` (lower case)."""
    for key, field in schema.items():
        if not _KEY.match(key):
            raise ValueError(f"invalid key {key!r}: expected 'section.name'")
        if not isinstance(field, Field):
            raise TypeError(f"{key}: expected a Field, got {type(field).__name__}")


def sections(schema: Schema) -> list[str]:
    return sorted({key.split(".", 1)[0] for key in schema})


def secret_keys(schema: Schema) -> set[str]:
    return {key for key, field in schema.items() if field.secret}
