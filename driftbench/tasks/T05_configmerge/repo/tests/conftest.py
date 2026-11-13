import pytest

from appconfig.schema import Field


@pytest.fixture
def schema():
    return {
        "server.host": Field("str", "127.0.0.1"),
        "server.port": Field("int", 8000),
        "server.debug": Field("bool", False),
        "db.url": Field("str", "sqlite:///app.db", secret=True),
        "db.pool": Field("int", 5),
        "app.tags": Field("list", ""),
    }


@pytest.fixture
def ini_file(tmp_path):
    path = tmp_path / "app.ini"
    path.write_text(
        "[server]\nport = 9000\ndebug = yes\n\n[db]\nurl = postgres://app:s3cret@db/app\n",
        encoding="utf-8",
    )
    return path
