from logstats.parser import parse_line


def _line(agent):
    return f'10.0.0.1 - - [01/Jan/2024:00:00:00 +0000] "GET / HTTP/1.1" 200 5 "-" "{agent}" 0.001'


def test_u3_is_bot():
    assert parse_line(_line("Mozilla/5.0 (compatible; Googlebot/2.1)")).is_bot
    assert parse_line(_line("Baiduspider/2.0")).is_bot
    assert not parse_line(_line("Mozilla/5.0 (X11; Linux x86_64)")).is_bot
