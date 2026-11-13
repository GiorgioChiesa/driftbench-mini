import pytest


@pytest.fixture
def fruit():
    return ["Fruit", "Qty"], [["apple", 3], ["banana", 12], ["kiwi", None]]
