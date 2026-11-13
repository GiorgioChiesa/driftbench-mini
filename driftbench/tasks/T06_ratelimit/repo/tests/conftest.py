import pytest

from ratelimit import ManualClock


@pytest.fixture
def clock():
    return ManualClock(start=1_000.0)
