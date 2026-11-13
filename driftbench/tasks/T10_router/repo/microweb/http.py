"""HTTP primitives: requests, responses and the error hierarchy used by the app."""
from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

STATUS_REASONS = {
    200: "OK", 201: "Created", 204: "No Content", 301: "Moved Permanently", 302: "Found",
    400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed", 500: "Internal Server Error",
}


class HTTPError(Exception):
    """An error that maps directly to an HTTP status code."""

    status = 500

    def __init__(self, detail: str = ""):
        self.detail = detail or STATUS_REASONS.get(self.status, "Error")
        super().__init__(self.detail)

    @property
    def headers(self) -> dict:
        return {}


class BadRequest(HTTPError):
    status = 400


class NotFound(HTTPError):
    status = 404


class MethodNotAllowed(HTTPError):
    """The path exists, but not for the requested method."""

    status = 405

    def __init__(self, allowed, detail: str = ""):
        super().__init__(detail)
        self.allowed = tuple(sorted({m.upper() for m in allowed}))

    @property
    def headers(self) -> dict:
        return {"Allow": ", ".join(self.allowed)}


class Request:
    """An incoming request. `params` is filled in by the app after routing."""

    def __init__(self, method: str, target: str, headers: dict | None = None, body: bytes = b""):
        self.method = method.upper()
        parts = urlsplit(target)
        self.path = parts.path or "/"
        self.query_string = parts.query
        self.headers = {k.title(): v for k, v in (headers or {}).items()}
        self.body = body
        self.params: dict = {}

    @property
    def query(self) -> dict:
        """Query parameters; the last value wins when a key is repeated."""
        return {key: values[-1] for key, values in parse_qs(self.query_string).items()}

    @property
    def text(self) -> str:
        return self.body.decode("utf-8")

    def json(self):
        return json.loads(self.body or b"null")

    def __repr__(self) -> str:
        return f"<Request {self.method} {self.path}>"


class Response:
    """An outgoing response; `body` may be text or bytes."""

    def __init__(self, body="", status: int = 200, headers: dict | None = None,
                 content_type: str = "text/plain; charset=utf-8"):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}
        self.headers.update(headers or {})

    @property
    def reason(self) -> str:
        return STATUS_REASONS.get(self.status, "Unknown")

    @property
    def status_line(self) -> str:
        return f"{self.status} {self.reason}"

    def encode(self) -> bytes:
        return self.body.encode("utf-8") if isinstance(self.body, str) else bytes(self.body)

    def __repr__(self) -> str:
        return f"<Response {self.status_line}>"
