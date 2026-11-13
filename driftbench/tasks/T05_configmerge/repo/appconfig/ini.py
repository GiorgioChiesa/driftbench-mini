"""INI file reading, flattened to ``section.key`` names."""
from __future__ import annotations

import configparser
from pathlib import Path


class IniError(ValueError):
    """Raised when an INI document cannot be parsed."""


def parse_ini(text: str, source: str = "<string>") -> dict[str, str]:
    """Parse INI text into ``{"section.key": "raw value"}`` (keys lower-cased)."""
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read_string(text, source=source)
    except configparser.Error as exc:
        raise IniError(str(exc)) from None
    flat: dict[str, str] = {}
    for section in parser.sections():
        for key, value in parser.items(section, raw=True):
            flat[f"{section.lower()}.{key}"] = value
    return flat


def read_ini(path) -> dict[str, str]:
    path = Path(path)
    return parse_ini(path.read_text(encoding="utf-8"), source=str(path))
