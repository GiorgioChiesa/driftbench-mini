from appconfig.ini import parse_ini


def test_u2_inline_comments_are_stripped():
    text = "[db]\nhost = db.local ; primary\nport = 5432  # default port\n"
    assert parse_ini(text) == {"db.host": "db.local", "db.port": "5432"}
