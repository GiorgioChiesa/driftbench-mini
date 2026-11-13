import pytest

from appconfig.ini import IniError, parse_ini, read_ini


def test_parse_ini_flattens_sections():
    text = "[Server]\nHost = example.org\nport=80\n\n[db]\nurl = sqlite://\n"
    assert parse_ini(text) == {"server.host": "example.org", "server.port": "80", "db.url": "sqlite://"}


def test_values_are_raw():
    assert parse_ini("[a]\npath = %(home)s/x\n") == {"a.path": "%(home)s/x"}


def test_duplicate_key_is_an_error():
    with pytest.raises(IniError):
        parse_ini("[a]\nx = 1\nx = 2\n")


def test_read_ini(ini_file):
    assert read_ini(ini_file)["server.port"] == "9000"
