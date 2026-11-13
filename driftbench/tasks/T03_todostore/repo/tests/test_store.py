import pytest

from todostore import TodoStore


def test_add_assigns_sequential_ids(store):
    assert [todo.id for todo in store] == [1, 2, 3]
    assert store.add("Call mum").id == 4


def test_add_normalises_tags():
    todo = TodoStore().add("  Plan trip ", tags=["Travel", "Summer Plans"])
    assert todo.title == "Plan trip"
    assert todo.tags == ["travel", "summer-plans"]


def test_complete_and_pending(store):
    store.complete(2)
    assert [todo.id for todo in store.pending()] == [1, 3]


def test_remove_and_unknown_id(store):
    store.remove(1)
    assert len(store) == 2
    with pytest.raises(KeyError):
        store.get(1)


def test_with_tag(store):
    assert [todo.title for todo in store.with_tag("HOME")] == ["Pay rent", "Buy milk"]


def test_by_priority(store):
    assert [todo.priority for todo in store.by_priority()] == [1, 2, 3]


def test_invalid_priority_rejected():
    with pytest.raises(ValueError):
        TodoStore().add("Nope", priority=5)
