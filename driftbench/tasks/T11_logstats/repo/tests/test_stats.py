from datetime import datetime, timezone

from logstats import stats


def test_count_by_status(records):
    assert stats.count_by_status(records) == {200: 1, 304: 1, 404: 1, 500: 1}


def test_status_classes(records):
    assert stats.status_classes(records) == {"2xx": 1, "3xx": 1, "4xx": 1, "5xx": 1}


def test_top_ips(records):
    assert stats.top_ips(records, n=2) == [("203.0.113.7", 2), ("192.0.2.33", 1)]


def test_total_bytes(records):
    assert stats.total_bytes(records) == 2326 + 87 + 12


def test_requests_per_minute(records):
    per_minute = stats.requests_per_minute(records)
    assert list(per_minute.values()) == [2, 1, 1]
    assert next(iter(per_minute)) == datetime(2023, 10, 10, 13, 55, tzinfo=timezone.utc)
