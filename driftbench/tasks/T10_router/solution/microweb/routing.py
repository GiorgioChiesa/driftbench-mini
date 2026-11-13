"""URL routing: map (method, path) pairs to handlers.

Patterns look like ``/users/<int:id>`` or ``/posts/<slug>``. Supported converters: ``str``
(default, one non-empty segment), ``int`` (ASCII digits, converted to ``int``) and ``path``
(last segment only, captures the rest of the path).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .http import MethodNotAllowed, NotFound
from .urls import build_query, normalize_path, quote_segment, split_path

_PARAM = re.compile(r"^<(?:([A-Za-z_][A-Za-z0-9_]*):)?([A-Za-z_][A-Za-z0-9_]*)>$")
_DIGITS = re.compile(r"[0-9]+")
_RANK = {"static": 0, "int": 1, "str": 2, "path": 3}


class RouteError(ValueError):
    """A route pattern is invalid."""


class RouteConflict(RouteError):
    """A route clashes with one that is already registered."""


class BuildError(LookupError):
    """``url_for`` cannot build a URL from the given arguments."""


@dataclass
class Route:
    pattern: str
    handler: Callable
    methods: frozenset
    name: str | None = None
    segments: list = field(default_factory=list)

    @property
    def signature(self) -> tuple:
        """Pattern shape used for conflict detection (parameter names do not matter)."""
        return tuple((kind, value if kind == "static" else None) for kind, value in self.segments)

    @property
    def rank(self) -> tuple:
        return tuple(_RANK[kind] for kind, _ in self.segments)

    @property
    def allowed_methods(self) -> set:
        return set(self.methods) | ({"HEAD"} if "GET" in self.methods else set())

    def allows(self, method: str) -> bool:
        return method in self.allowed_methods

    def match_path(self, parts: list[str]) -> dict | None:
        """Return the converted parameters if `parts` matches this route, else None."""
        params = {}
        for i, (kind, value) in enumerate(self.segments):
            if kind == "path":
                rest = parts[i:]
                if not rest:
                    return None
                params[value] = "/".join(rest)
                return params
            if i >= len(parts):
                return None
            part = parts[i]
            if kind == "static":
                if part != value:
                    return None
            elif kind == "int":
                if not _DIGITS.fullmatch(part):
                    return None
                params[value] = int(part)
            else:
                if not part:
                    return None
                params[value] = part
        return params if len(parts) == len(self.segments) else None

    def build(self, params: dict) -> str:
        params = dict(params)
        out = []
        for kind, value in self.segments:
            if kind == "static":
                out.append(quote_segment(value))
                continue
            if value not in params:
                raise BuildError(f"missing parameter {value!r} for route {self.name!r}")
            raw = params.pop(value)
            if kind == "int":
                valid_int = isinstance(raw, int) and not isinstance(raw, bool) and raw >= 0
                if not (valid_int or (isinstance(raw, str) and _DIGITS.fullmatch(raw))):
                    raise BuildError(f"parameter {value!r} must be a non-negative integer, got {raw!r}")
                out.append(str(raw))
            elif kind == "path":
                out.append("/".join(quote_segment(p) for p in str(raw).split("/")))
            else:
                out.append(quote_segment(raw))
        url = "/" + "/".join(out)
        if params:
            url += "?" + build_query(params)
        return url


@dataclass
class Match:
    route: Route
    params: dict

    @property
    def handler(self) -> Callable:
        return self.route.handler


def _parse(pattern: str) -> list:
    segments, seen = [], set()
    parts = split_path(pattern)
    for i, seg in enumerate(parts):
        m = _PARAM.match(seg)
        if not m:
            segments.append(("static", seg))
            continue
        conv, name = m.group(1) or "str", m.group(2)
        if conv not in ("str", "int", "path"):
            raise RouteError(f"unknown converter {conv!r} in {pattern!r}")
        if conv == "path" and i != len(parts) - 1:
            raise RouteError(f"'path' converter must be the last segment in {pattern!r}")
        if name in seen:
            raise RouteError(f"parameter {name!r} used twice in {pattern!r}")
        seen.add(name)
        segments.append((conv, name))
    return segments


class Router:
    """An ordered collection of routes."""

    def __init__(self):
        self.routes: list[Route] = []
        self._by_name: dict[str, Route] = {}

    def add_route(self, pattern: str, handler: Callable, methods=("GET",), name: str | None = None) -> Route:
        segments = _parse(pattern)
        route = Route(normalize_path(pattern), handler, frozenset(m.upper() for m in methods), name, segments)
        if name is not None and name in self._by_name:
            raise RouteConflict(f"route name {name!r} is already registered")
        for other in self.routes:
            if other.signature == route.signature and other.methods & route.methods:
                overlap = ", ".join(sorted(other.methods & route.methods))
                raise RouteConflict(f"{route.pattern!r} conflicts with {other.pattern!r} for {overlap}")
        self.routes.append(route)
        if name is not None:
            self._by_name[name] = route
        return route

    def match(self, method: str, path: str) -> Match:
        method = method.upper()
        parts = split_path(path)
        candidates = []
        for route in self.routes:
            params = route.match_path(parts)
            if params is not None:
                candidates.append((route, params))
        if not candidates:
            raise NotFound(f"no route for {method} {normalize_path(path)}")
        candidates.sort(key=lambda c: c[0].rank)
        for route, params in candidates:
            if route.allows(method):
                return Match(route, params)
        allowed = set().union(*(route.allowed_methods for route, _ in candidates))
        raise MethodNotAllowed(allowed, f"{method} not allowed for {normalize_path(path)}")

    def url_for(self, name: str, **params) -> str:
        route = self._by_name.get(name)
        if route is None:
            raise BuildError(f"no route named {name!r}")
        return route.build(params)

    def __iter__(self):
        return iter(self.routes)

    def __len__(self) -> int:
        return len(self.routes)
