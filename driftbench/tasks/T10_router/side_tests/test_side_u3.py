from microweb.http import Request


def test_u3_request_cookies():
    req = Request("GET", "/", headers={"Cookie": "session=abc123; theme=dark"})
    assert req.cookies == {"session": "abc123", "theme": "dark"}
    assert Request("GET", "/").cookies == {}
