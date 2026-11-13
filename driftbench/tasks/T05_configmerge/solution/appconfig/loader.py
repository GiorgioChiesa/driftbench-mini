"""Configuration loading."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .coerce import coerce
from .envsource import read_env
from .ini import read_ini
from .schema import Schema, validate_schema


class ConfigValueError(ValueError):
    """A configuration value cannot be converted to its field type."""

    def __init__(self, key: str, value: Any, source: str, reason: str = "") -> None:
        self.key = key
        self.value = value
        self.source = source
        message = f"{key}: invalid value {value!r} from {source}"
        super().__init__(f"{message} ({reason})" if reason else message)


class UnknownConfigKey(KeyError):
    """The configuration file sets a key the schema does not declare."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


def defaults(schema: Schema) -> dict[str, Any]:
    """The schema's default value for every key."""
    validate_schema(schema)
    return {key: field.default for key, field in schema.items()}


def load_file(path) -> dict[str, str]:
    """Raw ``section.key`` strings from an INI file (no merging, no coercion)."""
    return read_ini(Path(path))


def load_config(schema: Schema, path=None, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Merge defaults < INI file < ``APP_`` environment variables and coerce every value."""
    layers: dict[str, tuple[Any, str]] = {key: (value, "default") for key, value in defaults(schema).items()}
    if path is not None:
        for key, value in load_file(path).items():
            if key not in schema:
                raise UnknownConfigKey(key)
            layers[key] = (value, "file")
    if environ is not None:
        for key, value in read_env(environ).items():
            if key in schema:
                layers[key] = (value, "env")
    config: dict[str, Any] = {}
    for key, (value, source) in layers.items():
        if value is None:
            config[key] = None
            continue
        try:
            config[key] = coerce(schema[key].type, value)
        except ValueError as exc:
            raise ConfigValueError(key, value, source, str(exc)) from None
    return config
