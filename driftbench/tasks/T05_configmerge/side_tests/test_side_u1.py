from appconfig.redact import redact
from appconfig.schema import Field


def test_u1_redacts_password_and_token_names():
    schema = {"db.password": Field(), "api.token": Field(), "db.user": Field()}
    config = {"db.password": "hunter2", "api.token": "abc", "db.user": "app"}
    assert redact(config, schema) == {"db.password": "***", "api.token": "***", "db.user": "app"}
