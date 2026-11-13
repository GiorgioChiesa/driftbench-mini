import pytest

from appconfig.schema import Field, secret_keys, sections, validate_schema


def test_field_rejects_unknown_type():
    with pytest.raises(ValueError):
        Field("datetime")


def test_validate_schema_key_format(schema):
    validate_schema(schema)
    with pytest.raises(ValueError):
        validate_schema({"Port": Field("int")})


def test_sections_and_secrets(schema):
    assert sections(schema) == ["app", "db", "server"]
    assert secret_keys(schema) == {"db.url"}
