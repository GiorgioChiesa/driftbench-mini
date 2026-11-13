from microweb import urls


def test_normalize_path():
    assert urls.normalize_path("") == "/"
    assert urls.normalize_path("//a///b/") == "/a/b"
    assert urls.normalize_path("/a/b?x=1#top") == "/a/b"


def test_split_path_decodes_segments():
    assert urls.split_path("/") == []
    assert urls.split_path("/docs/read%20me") == ["docs", "read me"]


def test_quote_segment():
    assert urls.quote_segment("read me") == "read%20me"
    assert urls.quote_segment(42) == "42"


def test_build_query():
    assert urls.build_query({}) == ""
    assert urls.build_query({"q": "a b"}) == "q=a+b"


def test_join_path():
    assert urls.join_path("api", "/v1/", "users") == "/api/v1/users"
