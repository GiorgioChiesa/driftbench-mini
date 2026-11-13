import pytest

from microweb.http import MethodNotAllowed, NotFound, Request, Response


def test_request_parses_target():
    req = Request("get", "/search?q=x&page=2&q=y", headers={"content-type": "text/plain"})
    assert req.method == "GET"
    assert req.path == "/search"
    assert req.query == {"q": "y", "page": "2"}
    assert req.headers["Content-Type"] == "text/plain"


def test_request_body_helpers():
    req = Request("POST", "/", body=b'{"a": 1}')
    assert req.text == '{"a": 1}'
    assert req.json() == {"a": 1}


def test_response_defaults():
    resp = Response("hi")
    assert resp.status_line == "200 OK"
    assert resp.headers["Content-Type"].startswith("text/plain")
    assert resp.encode() == b"hi"


def test_errors_carry_status():
    assert NotFound().status == 404
    assert NotFound().detail == "Not Found"
    exc = MethodNotAllowed(["post", "GET"])
    assert exc.status == 405
    assert exc.headers == {"Allow": "GET, POST"}
