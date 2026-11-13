import pytest

from microweb.templates import TemplateError, escape, render


class User:
    name = "Ada"


def test_render_substitutes_values():
    assert render("Hello {{ name }}!", {"name": "Bob"}) == "Hello Bob!"


def test_render_dotted_lookup():
    assert render("{{user.name}}", {"user": User()}) == "Ada"
    assert render("{{ cfg.port }}", {"cfg": {"port": 80}}) == "80"


def test_render_escapes_by_default():
    assert render("{{ x }}", {"x": "<b>&"}) == "&lt;b&gt;&amp;"
    assert render("{{ x }}", {"x": "<b>"}, autoescape=False) == "<b>"


def test_missing_name_raises():
    with pytest.raises(TemplateError):
        render("{{ missing }}", {})


def test_escape_quotes():
    assert escape('"') == "&quot;"
