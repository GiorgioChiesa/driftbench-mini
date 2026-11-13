from ratelimit import backoff


def test_u1_delays_max_total():
    assert list(backoff.delays(10, max_total=3.0)) == [0.5, 1.0]
    assert list(backoff.delays(3, backoff.constant, delay=1.0, max_total=10.0)) == [1.0, 1.0, 1.0]
