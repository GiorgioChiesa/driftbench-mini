def test_index(call):
    resp = call("GET", "/")
    assert resp.status == 200
    assert resp.body == "home"


def test_json_result(call):
    resp = call("GET", "/health")
    assert resp.headers["Content-Type"] == "application/json"
    assert resp.body == '{"status": "ok"}'


def test_path_params_are_passed_to_handler(call):
    assert call("GET", "/hello/ada").body == "hello ada"


def test_post_body(call):
    assert call("POST", "/echo", body=b"ping").body == "ping"


def test_unknown_path_is_404(call):
    resp = call("GET", "/missing")
    assert resp.status == 404
    assert resp.body == "no route for GET /missing"


def test_before_request_hook_can_short_circuit(app, call):
    @app.before_request
    def deny(request):
        if request.path == "/":
            return ("forbidden", 403)

    assert call("GET", "/").status == 403
    assert call("GET", "/hello/x").status == 200
