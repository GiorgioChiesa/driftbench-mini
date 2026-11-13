import pytest

from microweb import App, Request


@pytest.fixture
def app():
    app = App()

    @app.route("/")
    def index(request):
        return "home"

    @app.route("/health")
    def health(request):
        return {"status": "ok"}

    @app.route("/echo", methods=["POST"])
    def echo(request):
        return request.text

    @app.route("/hello/<name>")
    def hello(request, name):
        return f"hello {name}"

    return app


@pytest.fixture
def call(app):
    def _call(method, target, **kwargs):
        return app.handle(Request(method, target, **kwargs))
    return _call
