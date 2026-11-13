"""Configuration overrides from environment variables.

``APP_DB__PORT=5433`` overrides ``db.port``: the prefix is stripped and a double
underscore separates the section from the key.
"""
from __future__ import annotations

from typing import Mapping

DEFAULT_PREFIX = "APP_"
SECTION_SEPARATOR = "__"


def env_key(name: str, prefix: str = DEFAULT_PREFIX) -> str | None:
    """Translate an environment variable name into a ``section.key`` name, or ``None``."""
    if not name.upper().startswith(prefix.upper()):
        return None
    rest = name[len(prefix):]
    section, sep, key = rest.partition(SECTION_SEPARATOR)
    if not sep or not section or not key:
        return None
    return f"{section.lower()}.{key.lower()}"


def read_env(environ: Mapping[str, str], prefix: str = DEFAULT_PREFIX) -> dict[str, str]:
    """All prefixed variables of ``environ`` as ``{"section.key": raw value}``."""
    found: dict[str, str] = {}
    for name in sorted(environ):
        key = env_key(name, prefix)
        if key is not None:
            found[key] = environ[name]
    return found
