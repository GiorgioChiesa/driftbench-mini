import pytest

from microweb.http import NotFound
from microweb.routing import Router


def home(request):
    return "home"


def show(request, slug):
    return slug


def test_static_route_matches():
    router = Router()
    router.add_route("/about", home)
    match = router.match("GET", "/about")
    assert match.handler is home
    assert match.params == {}


def test_trailing_slash_and_query_are_ignored():
    router = Router()
    router.add_route("/about/", home)
    assert router.match("GET", "/about?x=1").handler is home


def test_untyped_parameter_is_captured():
    router = Router()
    router.add_route("/posts/<slug>", show)
    assert router.match("get", "/posts/hello-world").params == {"slug": "hello-world"}


def test_unknown_path_raises_not_found():
    router = Router()
    router.add_route("/about", home)
    with pytest.raises(NotFound):
        router.match("GET", "/contact")


def test_router_len_and_iter():
    router = Router()
    router.add_route("/a", home)
    router.add_route("/b", home, methods=["POST"])
    assert len(router) == 2
    assert [r.pattern for r in router] == ["/a", "/b"]
