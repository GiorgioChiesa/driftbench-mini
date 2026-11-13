from appconfig import loader


def test_defaults(schema):
    assert loader.defaults(schema)["server.port"] == 8000
    assert set(loader.defaults(schema)) == set(schema)


def test_load_file_returns_raw_strings(ini_file):
    assert loader.load_file(ini_file) == {
        "server.port": "9000", "server.debug": "yes", "db.url": "postgres://app:s3cret@db/app"}
