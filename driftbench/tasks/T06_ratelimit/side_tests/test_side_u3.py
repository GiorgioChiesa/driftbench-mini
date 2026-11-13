from ratelimit.config import Rate, format_rate, parse_rate


def test_u3_format_rate():
    assert format_rate(Rate(10, 60.0)) == "10/60s"
    assert format_rate(Rate(3, 1.5)) == "3/1.5s"
    assert parse_rate(format_rate(Rate(7, 30.0))) == Rate(7, 30.0)
