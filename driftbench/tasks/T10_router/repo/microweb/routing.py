"""URL routing: map (method, path) pairs to handlers."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .http import NotFound
from .urls import normalize_path, split_path

_PARAM = re.compile(r"^<([A-Za-z_][A-Za-z0-9_]*)>$")


@dataclass
class Route:
    pattern: str
    handler: Callable
    methods: frozenset
    name: str | None = None
    segments: list = field(default_factory=list)

    def match_path(self, parts: list[str]) -> dict | None:
        """Return the captured parameters if `parts` matches this route, else None."""
        if len(parts) != len(self.segments):
            return None
        params = {}
        for (kind, value), part in zip(self.segments, parts):
            if kind == "static":
                if part != value:
                    return None
            else:
                params[value] = part
        return params


@dataclass
class Match:
    route: Route
    params: dict

    @property
    def handler(self) -> Callable:
        return self.route.handler


class Router:
    """An ordered collection of routes. Patterns look like ``/users/<name>``."""

    def __init__(self):
        self.routes: list[Route] = []

    def add_route(self, pattern: str, handler: Callable, methods=("GET",), name: str | None = None) -> Route:
        segments = []
        for seg in split_path(pattern):
            m = _PARAM.match(seg)
            segments.append(("param", m.group(1)) if m else ("static", seg))
        route = Route(normalize_path(pattern), handler, frozenset(m.upper() for m in methods), name, segments)
        self.routes.append(route)
        return route

    def match(self, method: str, path: str) -> Match:
        method = method.upper()
        parts = split_path(path)
        for route in self.routes:
            if method not in route.methods:
                continue
            params = route.match_path(parts)
            if params is not None:
                return Match(route, params)
        raise NotFound(f"no route for {method} {normalize_path(path)}")

    def __iter__(self):
        return iter(self.routes)

    def __len__(self) -> int:
        return len(self.routes)
