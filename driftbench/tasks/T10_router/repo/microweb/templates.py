"""A deliberately small template renderer: ``{{ name }}`` and ``{{ user.name }}`` substitutions."""
from __future__ import annotations

import re

_VAR = re.compile(r"\{\{\s*([A-Za-z_][\w.]*)\s*\}\}")
_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


class TemplateError(KeyError):
    """A placeholder refers to a name that is not in the context."""


def escape(value) -> str:
    """HTML-escape ``value`` (converted with ``str``)."""
    return "".join(_ESCAPES.get(ch, ch) for ch in str(value))


def _lookup(context, dotted: str):
    value = context
    for part in dotted.split("."):
        value = value[part] if isinstance(value, dict) else getattr(value, part)
    return value


def render(template: str, context: dict | None = None, autoescape: bool = True) -> str:
    """Substitute every ``{{ name }}`` placeholder with its value from ``context``."""
    context = context or {}

    def substitute(m: re.Match) -> str:
        try:
            value = _lookup(context, m.group(1))
        except (KeyError, AttributeError):
            raise TemplateError(m.group(1)) from None
        return escape(value) if autoescape else str(value)

    return _VAR.sub(substitute, template)
