import pytest

from units.registry import Registry


@pytest.fixture
def reg():
    return Registry.with_defaults()
