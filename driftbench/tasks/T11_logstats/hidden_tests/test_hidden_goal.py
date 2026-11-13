import pytest


def line(path, status=200, rt="0.010", method="GET", when="10/Oct/2023:13:55:36 +0000"):
    return f'203.0.113.7 - - [{when}] "{method} {path} HTTP/1.1" {status} 512 "-" "curl/8.4.0" {rt}'


def recs(*lines):
    from logstats.parser import parse_line
    return [parse_line(item) for item in lines]


def test_r1_percentile_nearest_rank():
    from logstats.stats import percentile

    data = [50, 15, 40, 20, 35]
    assert percentile(data, 5) == 15
    assert percentile(data, 30) == 20
    assert percentile(data, 40) == 20
    assert percentile(data, 50) == 35
    assert percentile(data, 100) == 50
    assert percentile(list(range(1, 21)), 95) == 19
    assert percentile([7.5], 50) == 7.5
    for bad_values, bad_p in (([], 50), ([1, 2], 0), ([1, 2], 101), ([1, 2], -5)):
        with pytest.raises(ValueError):
            percentile(bad_values, bad_p)


def test_r2_endpoint_stats_keys_and_percentiles():
    from logstats.stats import endpoint_stats

    rows = recs(
        line("/api/users/42?full=1", rt="0.0125"),
        line("/api/users/7", rt="0.030"),
        line("/api/users/8/", rt="0.0205"),
        line("/reports/2024-summary", rt="0.200"),
        line("/api/users", method="POST", status=201, rt="0.050"),
    )
    out = endpoint_stats(rows)
    assert set(out) == {"GET /api/users/{id}", "GET /reports/2024-summary", "POST /api/users"}
    users = out["GET /api/users/{id}"]
    assert users.endpoint == "GET /api/users/{id}"
    assert users.count == 3
    assert users.p50_ms == 20.5
    assert users.p95_ms == 30.0
    assert out["GET /reports/2024-summary"].p50_ms == 200.0
    with pytest.raises(Exception):
        users.count = 99  # frozen dataclass


def test_r3_error_rate_counts_only_5xx():
    from logstats.stats import endpoint_stats

    rows = recs(*(line("/api/orders", status=s) for s in (200, 404, 500, 503, 200, 201)))
    st = endpoint_stats(rows)["GET /api/orders"]
    assert st.error_rate == 0.3333
    assert isinstance(st.error_rate, float)
    assert endpoint_stats(recs(line("/ok", status=404)))["GET /ok"].error_rate == 0.0


def test_r4_missing_durations():
    from logstats.stats import endpoint_stats

    rows = recs(
        line("/a", rt="-", status=502),
        line("/a", rt="0.0125"),
        line("/a", rt="-"),
        line("/b", rt="-"),
    )
    out = endpoint_stats(rows)
    a = out["GET /a"]
    assert a.count == 3
    assert a.error_rate == 0.3333
    assert a.p50_ms == 12.5 and a.p95_ms == 12.5
    b = out["GET /b"]
    assert b.count == 1 and b.p50_ms is None and b.p95_ms is None


def test_r5_slowest_endpoints():
    from logstats.stats import slowest_endpoints

    rows = recs(
        line("/a", rt="0.050"), line("/a", rt="0.0125"),
        line("/b", rt="0.080"),
        line("/c", rt="0.080"),
        line("/d", rt="-"),
        line("/e", rt="0.010"),
    )
    top = slowest_endpoints(rows, n=3)
    assert [s.endpoint for s in top] == ["GET /b", "GET /c", "GET /a"]
    assert [s.p95_ms for s in top] == [80.0, 80.0, 50.0]
    assert [s.endpoint for s in slowest_endpoints(rows, n=10)] == ["GET /b", "GET /c", "GET /a", "GET /e"]
    assert len(slowest_endpoints(rows)) == 4
    assert slowest_endpoints(rows, n=0) == []


def test_r6_filter_window():
    from datetime import datetime, timedelta, timezone

    from logstats.stats import filter_window

    rows = recs(
        line("/1", when="10/Oct/2023:13:55:00 +0200"),  # 11:55:00Z
        line("/2", when="10/Oct/2023:11:59:59 +0000"),  # 11:59:59Z
        line("/3", when="10/Oct/2023:07:00:00 -0500"),  # 12:00:00Z
        line("/4", when="10/Oct/2023:11:54:59 +0000"),  # 11:54:59Z
    )
    paths = lambda rs: [r.path for r in rs]
    assert paths(filter_window(rows, "2023-10-10T11:55:00Z", "2023-10-10T12:00:00Z")) == ["/1", "/2"]
    assert paths(filter_window(rows, start="2023-10-10T12:00:00+00:00")) == ["/3"]
    assert paths(filter_window(rows, end=datetime(2023, 10, 10, 13, 55, tzinfo=timezone(timedelta(hours=2))))) == ["/4"]
    assert paths(filter_window(rows)) == ["/1", "/2", "/3", "/4"]
    assert isinstance(filter_window(iter(rows)), list)
    with pytest.raises(ValueError):
        filter_window(rows, start=datetime(2023, 10, 10, 12, 0))
