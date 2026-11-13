from logstats.endpoints import endpoint_key, is_static_asset, path_template


def test_path_template_replaces_ids():
    assert path_template("/api/users/42?full=1") == "/api/users/{id}"
    assert path_template("/api/users/7/") == "/api/users/{id}"
    assert path_template("/orders/0b7c9a62-1f3e-4c55-9a51-6f1f0d2b9e10/items") == "/orders/{id}/items"
    assert path_template("/") == "/"


def test_endpoint_key(records):
    assert endpoint_key(records[0]) == "GET /api/users/{id}"
    assert endpoint_key(records[2]) == "POST /api/orders"


def test_is_static_asset():
    assert is_static_asset("/static/app.js?v=3")
    assert not is_static_asset("/api/users")
