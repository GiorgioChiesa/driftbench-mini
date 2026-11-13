from appconfig.envsource import env_key, read_env


def test_env_key():
    assert env_key("APP_DB__PORT") == "db.port"
    assert env_key("app_server__debug") == "server.debug"


def test_env_key_ignores_foreign_names():
    assert env_key("HOME") is None
    assert env_key("APP_PORT") is None
    assert env_key("APP___X") is None


def test_read_env_custom_prefix():
    environ = {"SVC_DB__URL": "x", "APP_DB__URL": "y", "PATH": "/bin"}
    assert read_env(environ, prefix="SVC_") == {"db.url": "x"}
    assert read_env(environ) == {"db.url": "y"}
