import pytest

from todostore import TodoStore


@pytest.fixture
def store():
    s = TodoStore()
    s.add("Pay rent", priority=1, tags=["home"])
    s.add("Write report", tags=["work"])
    s.add("Buy milk", priority=3, tags=["home", "errands"])
    return s


@pytest.fixture
def saved_path(store, tmp_path):
    path = tmp_path / "todos.json"
    store.save(path)
    return path
