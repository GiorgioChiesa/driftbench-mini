import pytest


def h_a(request, **kw):
    return "a"


def h_b(request, **kw):
    return "b"


def h_c(request, **kw):
    return "c"


def h_d(request, **kw):
    return "d"


def test_r1_typed_parameters():
    from microweb.http import NotFound
    from microweb.routing import Router

    r = Router()
    r.add_route("/users/<int:id>", h_a)
    r.add_route("/tags/<tag>", h_b)
    r.add_route("/files/<path:p>", h_c)
    r.add_route("/posts/<str:slug>/edit", h_d)
    m = r.match("GET", "/users/42")
    assert m.handler is h_a
    assert m.params == {"id": 42} and type(m.params["id"]) is int
    assert r.match("GET", "/tags/c++").params == {"tag": "c++"}
    assert r.match("GET", "/tags/a%20b").params == {"tag": "a b"}
    assert r.match("GET", "/files/docs/2024/Report.pdf").params == {"p": "docs/2024/Report.pdf"}
    assert r.match("GET", "/posts/hello/edit").params == {"slug": "hello"}
    for bad in ("/users/abc", "/users/-1", "/users/4.2", "/files"):
        with pytest.raises(NotFound):
            r.match("GET", bad)


def test_r2_invalid_patterns():
    from microweb.routing import Router, RouteError

    assert issubclass(RouteError, ValueError)
    for pattern in ("/a/<float:x>", "/a/<path:p>/b", "/a/<x>/<int:x>"):
        with pytest.raises(RouteError):
            Router().add_route(pattern, h_a)


def test_r3_precedence():
    from microweb.routing import Router

    r = Router()
    r.add_route("/u/<path:rest>", h_d)
    r.add_route("/u/<name>", h_c)
    r.add_route("/u/<int:id>", h_b)
    r.add_route("/u/me", h_a)
    assert r.match("GET", "/u/me").handler is h_a
    assert r.match("GET", "/u/7").handler is h_b
    assert r.match("GET", "/u/bob").handler is h_c
    assert r.match("GET", "/u/a/b").handler is h_d


def test_r4_method_not_allowed_vs_not_found():
    from microweb.http import MethodNotAllowed, NotFound
    from microweb.routing import Router

    r = Router()
    r.add_route("/items", h_a, methods=["get"])
    r.add_route("/items", h_b, methods=["POST"])
    r.add_route("/items/<int:id>", h_c, methods=["PUT"])
    assert r.match("head", "/items").handler is h_a
    assert r.match("post", "/items").handler is h_b
    with pytest.raises(MethodNotAllowed) as info:
        r.match("DELETE", "/items")
    assert info.value.status == 405
    assert tuple(info.value.allowed) == ("GET", "HEAD", "POST")
    with pytest.raises(MethodNotAllowed) as info:
        r.match("GET", "/items/3")
    assert tuple(info.value.allowed) == ("PUT",)
    with pytest.raises(NotFound):
        r.match("GET", "/nothing")


def test_r5_url_for():
    from microweb.routing import BuildError, Router

    assert issubclass(BuildError, LookupError)
    r = Router()
    r.add_route("/users/<int:id>", h_a, name="user")
    r.add_route("/tags/<tag>", h_a, name="tag")
    r.add_route("/files/<path:p>", h_a, name="file")
    r.add_route("/search", h_a, name="search")
    assert r.url_for("user", id=42) == "/users/42"
    assert r.url_for("user", id="7") == "/users/7"
    assert r.url_for("tag", tag="a b/c") == "/tags/a%20b%2Fc"
    assert r.url_for("file", p="docs/my file.txt") == "/files/docs/my%20file.txt"
    assert r.url_for("search", q="x y", page=2, lang="it") == "/search?lang=it&page=2&q=x+y"
    assert r.url_for("user", id=5, tab="info") == "/users/5?tab=info"
    with pytest.raises(BuildError):
        r.url_for("nope")
    with pytest.raises(BuildError):
        r.url_for("user")
    with pytest.raises(BuildError):
        r.url_for("user", id="abc")
    with pytest.raises(BuildError):
        r.url_for("user", id=-3)


def test_r6_conflicts():
    from microweb.routing import RouteConflict, RouteError, Router

    assert issubclass(RouteConflict, RouteError)
    r = Router()
    r.add_route("/users/<int:id>", h_a, name="user")
    with pytest.raises(RouteConflict):
        r.add_route("/users/<int:uid>", h_b)
    with pytest.raises(RouteConflict):
        r.add_route("/users/<int:x>/", h_b, methods=["put", "get"])
    r.add_route("/users/<int:id>", h_b, methods=["DELETE"])
    r.add_route("/users/<name>", h_c)
    with pytest.raises(RouteConflict):
        r.add_route("/users/<str:other>", h_c)
    with pytest.raises(RouteConflict):
        r.add_route("/elsewhere", h_d, name="user")
    assert len(r) == 3
