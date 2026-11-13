import pytest


def make_schema():
    from appconfig.schema import Field

    return {
        "server.host": Field("str", "127.0.0.1"),
        "server.port": Field("int", "8000"),
        "server.debug": Field("bool", False),
        "server.ratio": Field("float", 0.5),
        "db.url": Field("str", None, secret=True),
        "db.pool": Field("int", 5),
        "app.tags": Field("list", "a,b"),
    }


def write_ini(tmp_path, text):
    path = tmp_path / "app.ini"
    path.write_text(text, encoding="utf-8")
    return path


def test_r1_defaults_only(monkeypatch):
    from appconfig.loader import load_config

    monkeypatch.setenv("APP_SERVER__PORT", "1234")
    config = load_config(make_schema())
    assert set(config) == set(make_schema())
    assert config["server.port"] == 8000
    assert config["db.url"] is None


def test_r2_precedence(tmp_path):
    from appconfig.loader import load_config

    path = write_ini(tmp_path, "[server]\nport = 9000\nhost = file.example\n\n[db]\npool = 10\n")
    env = {"APP_SERVER__PORT": "9100"}
    config = load_config(make_schema(), path=path, environ=env)
    assert config["server.port"] == 9100          # env beats file
    assert config["server.host"] == "file.example"  # file beats default
    assert config["db.pool"] == 10
    assert config["server.ratio"] == 0.5           # default
    assert load_config(make_schema(), path=path)["server.port"] == 9000


def test_r3_env_prefix_and_ignored(tmp_path):
    from appconfig.loader import load_config

    env = {
        "APP_DB__URL": "postgres://db/app",
        "app_server__host": "lower.example",
        "SERVER__PORT": "1",
        "APP_NOPE__THING": "x",
        "HOME": "/home/me",
    }
    config = load_config(make_schema(), environ=env)
    assert config["db.url"] == "postgres://db/app"
    assert config["server.host"] == "lower.example"
    assert config["server.port"] == 8000
    assert "nope.thing" not in config


def test_r4_coercion_every_layer(tmp_path):
    from appconfig.loader import load_config

    path = write_ini(tmp_path, "[server]\nratio = 0.75\n\n[app]\ntags = x, y ,z\n")
    env = {"APP_SERVER__DEBUG": "false", "APP_DB__POOL": " 12 "}
    config = load_config(make_schema(), path=path, environ=env)
    assert config["server.debug"] is False
    assert config["db.pool"] == 12
    assert config["server.ratio"] == 0.75
    assert config["app.tags"] == ["x", "y", "z"]
    assert load_config(make_schema(), environ={"APP_SERVER__DEBUG": "on"})["server.debug"] is True
    assert load_config(make_schema())["app.tags"] == ["a", "b"]


def test_r5_config_value_error(tmp_path):
    from appconfig.loader import ConfigValueError, load_config
    from appconfig.schema import Field

    assert issubclass(ConfigValueError, ValueError)
    with pytest.raises(ConfigValueError) as info:
        load_config(make_schema(), environ={"APP_DB__POOL": "lots"})
    assert (info.value.key, info.value.value, info.value.source) == ("db.pool", "lots", "env")

    path = write_ini(tmp_path, "[server]\ndebug = maybe\n")
    with pytest.raises(ConfigValueError) as info:
        load_config(make_schema(), path=path)
    assert (info.value.key, info.value.value, info.value.source) == ("server.debug", "maybe", "file")

    with pytest.raises(ConfigValueError) as info:
        load_config({"server.port": Field("int", "eighty")})
    assert (info.value.key, info.value.source) == ("server.port", "default")


def test_r6_unknown_file_key(tmp_path):
    from appconfig.loader import UnknownConfigKey, load_config

    assert issubclass(UnknownConfigKey, KeyError)
    path = write_ini(tmp_path, "[server]\nport = 1\ncolour = blue\n")
    with pytest.raises(UnknownConfigKey) as info:
        load_config(make_schema(), path=path)
    assert info.value.key == "server.colour"
