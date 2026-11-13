from datetime import datetime, timedelta, timezone

import pytest

from logstats import timeutil


def test_parse_clf_time_utc():
    dt = timeutil.parse_clf_time("05/Mar/2024:08:01:02 +0000")
    assert dt == datetime(2024, 3, 5, 8, 1, 2, tzinfo=timezone.utc)
    assert dt.utcoffset() == timedelta(0)


def test_parse_iso():
    assert timeutil.parse_iso("2024-03-05T08:01:02Z") == datetime(2024, 3, 5, 8, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        timeutil.parse_iso("2024-03-05T08:01:02")


def test_floor_minute():
    dt = datetime(2024, 3, 5, 8, 1, 59, 123, tzinfo=timezone.utc)
    assert timeutil.floor_minute(dt) == datetime(2024, 3, 5, 8, 1, tzinfo=timezone.utc)
