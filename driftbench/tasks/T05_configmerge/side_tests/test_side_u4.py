from appconfig.redact import render


def test_u4_render_quotes_values_with_spaces():
    assert render({"app.name": "my service", "app.port": 80}) == 'app.name = "my service"\napp.port = 80'
