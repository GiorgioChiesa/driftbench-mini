"""The application object: route registration and request dispatch."""
from __future__ import annotations

import json
from typing import Callable

from .http import HTTPError, Request, Response
from .routing import Router


class App:
    def __init__(self):
        self.router = Router()
        self.before_hooks: list[Callable] = []

    def route(self, pattern: str, methods=("GET",), name: str | None = None):
        """Decorator registering ``func`` for ``pattern``; the route name defaults to the function name."""
        def decorator(func: Callable) -> Callable:
            self.router.add_route(pattern, func, methods, name or func.__name__)
            return func
        return decorator

    def before_request(self, func: Callable) -> Callable:
        """Register a hook run before every handler; returning a value short-circuits the request."""
        self.before_hooks.append(func)
        return func

    def handle(self, request: Request) -> Response:
        try:
            match = self.router.match(request.method, request.path)
            request.params = dict(match.params)
            for hook in self.before_hooks:
                early = hook(request)
                if early is not None:
                    return self._coerce(early)
            return self._coerce(match.handler(request, **match.params))
        except HTTPError as exc:
            response = Response(exc.detail, exc.status)
            response.headers.update(exc.headers)
            return response

    @staticmethod
    def _coerce(result) -> Response:
        if isinstance(result, Response):
            return result
        if isinstance(result, tuple):
            body, status = result
            return Response(body, status)
        if isinstance(result, (dict, list)):
            return Response(json.dumps(result), content_type="application/json")
        return Response(str(result))
