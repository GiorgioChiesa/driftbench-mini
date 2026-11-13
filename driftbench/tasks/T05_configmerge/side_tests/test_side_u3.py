from appconfig.schema import Field, describe


def test_u3_describe_schema():
    schema = {"server.port": Field("int", 8000, help="TCP port"), "db.url": Field("str", None, secret=True)}
    assert describe(schema) == [
        "db.url (str, secret)",
        "server.port (int, default 8000): TCP port",
    ]
