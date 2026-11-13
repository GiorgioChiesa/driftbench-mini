from appconfig.redact import format_value, redact, render


def test_redact_masks_secrets(schema):
    config = {"db.url": "postgres://x", "server.port": 9000}
    assert redact(config, schema) == {"db.url": "***", "server.port": 9000}


def test_redact_keeps_empty_secrets(schema):
    assert redact({"db.url": ""}, schema) == {"db.url": ""}


def test_format_value():
    assert format_value(True) == "true"
    assert format_value(["a", "b"]) == "a, b"
    assert format_value(None) == ""


def test_render_sorted():
    assert render({"b.x": 1, "a.y": False}) == "a.y = false\nb.x = 1"
