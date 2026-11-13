from datetime import datetime, timezone

import pytest

from logstats.parser import ParseError, parse_line, parse_lines

LINE = ('203.0.113.7 - alice [10/Oct/2023:13:55:36 +0000] "GET /api/users/42?full=1 HTTP/1.1" '
        '200 2326 "https://example.com/" "Mozilla/5.0" 0.042')


def test_parse_line_fields():
    r = parse_line(LINE)
    assert r.ip == "203.0.113.7"
    assert r.user == "alice"
    assert r.time == datetime(2023, 10, 10, 13, 55, 36, tzinfo=timezone.utc)
    assert (r.method, r.path, r.protocol) == ("GET", "/api/users/42?full=1", "HTTP/1.1")
    assert (r.status, r.size) == (200, 2326)
    assert r.referer == "https://example.com/"
    assert r.agent == "Mozilla/5.0"
    assert r.duration_ms == 42.0


def test_dash_fields_become_none_or_zero(records):
    r = records[-1]
    assert r.user is None and r.referer is None
    assert r.duration_ms is None
    assert records[1].size == 0


def test_plain_common_log_format():
    r = parse_line('10.0.0.1 - - [01/Jan/2024:00:00:00 +0000] "GET / HTTP/1.0" 200 5')
    assert r.agent is None and r.duration_ms is None


def test_lenient_parsing_skips_bad_lines(records):
    assert len(records) == 4


def test_strict_parsing_reports_line_number():
    with pytest.raises(ParseError) as info:
        parse_lines([LINE, "garbage"], strict=True)
    assert info.value.lineno == 2


def test_parse_line_rejects_garbage():
    with pytest.raises(ParseError):
        parse_line("hello world")
