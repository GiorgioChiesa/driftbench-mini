import json

from microweb.http import Response


def test_u2_response_json_factory():
    resp = Response.json({"ok": True}, status=201)
    assert resp.status == 201
    assert resp.headers["Content-Type"] == "application/json"
    assert json.loads(resp.body) == {"ok": True}
