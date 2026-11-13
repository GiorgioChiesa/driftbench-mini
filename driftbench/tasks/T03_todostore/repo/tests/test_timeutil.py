from datetime import date

import pytest

from todostore.timeutil import days_between, format_date, humanize_age, parse_iso_date


def test_parse_iso_date():
    assert parse_iso_date(" 2024-03-15 ") == date(2024, 3, 15)


def test_parse_iso_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_iso_date("15/03/2024")


def test_format_date():
    assert format_date(date(2024, 1, 2)) == "2024-01-02"
    assert format_date(None) == "-"


def test_days_between():
    assert days_between(date(2024, 2, 28), date(2024, 3, 1)) == 2


def test_humanize_age():
    today = date(2024, 3, 15)
    assert humanize_age(today, today) == "today"
    assert humanize_age(date(2024, 3, 14), today) == "yesterday"
    assert humanize_age(date(2024, 3, 5), today) == "10 days ago"
