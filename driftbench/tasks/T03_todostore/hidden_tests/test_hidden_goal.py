import json
from datetime import date

import pytest


def test_r1_due_field_and_add_keyword():
    from todostore import TodoStore
    from todostore.models import Todo

    assert Todo(1, "x").due is None
    store = TodoStore()
    todo = store.add("File taxes", due=date(2024, 4, 30))
    assert todo.due == date(2024, 4, 30)
    assert store.add("No deadline").due is None


def test_r2_parse_due():
    from todostore.store import InvalidDueDate, parse_due

    assert parse_due("2024-03-05") == date(2024, 3, 5)
    assert parse_due(" 05/03/2024 ") == date(2024, 3, 5)
    assert parse_due("7/11/2024") == date(2024, 11, 7)
    assert issubclass(InvalidDueDate, ValueError)
    for bad in ["2024-02-30", "31/13/2024", "tomorrow", "", "2024/03/05"]:
        with pytest.raises(InvalidDueDate):
            parse_due(bad)


def test_r3_add_accepts_strings():
    from todostore import TodoStore
    from todostore.store import InvalidDueDate

    store = TodoStore()
    assert store.add("a", due="2024-05-01").due == date(2024, 5, 1)
    assert store.add("b", due="01/05/2024").due == date(2024, 5, 1)
    with pytest.raises(InvalidDueDate):
        store.add("c", due="next week")


def test_r4_overdue_sorted_and_filtered():
    from todostore import TodoStore

    store = TodoStore()
    a = store.add("a", due=date(2024, 3, 10))
    b = store.add("b", due=date(2024, 3, 1))
    store.add("c", due=date(2024, 3, 15))
    store.add("d")
    e = store.add("e", due=date(2024, 2, 1))
    f = store.add("f", due=date(2024, 3, 1))
    store.complete(e.id)
    assert [t.id for t in store.overdue(date(2024, 3, 15))] == [b.id, f.id, a.id]
    assert store.overdue(date(2024, 1, 1)) == []


def test_r5_set_due():
    from todostore import TodoStore

    store = TodoStore()
    todo = store.add("x")
    store.set_due(todo.id, date(2024, 6, 1))
    assert store.get(todo.id).due == date(2024, 6, 1)
    store.set_due(todo.id, "15/06/2024")
    assert store.get(todo.id).due == date(2024, 6, 15)
    store.set_due(todo.id, None)
    assert store.get(todo.id).due is None
    with pytest.raises(KeyError):
        store.set_due(999, date(2024, 1, 1))


def test_r6_due_persists(tmp_path):
    from todostore import TodoStore

    store = TodoStore()
    store.add("x", due=date(2024, 3, 5), priority=1)
    store.add("y")
    path = tmp_path / "todos.json"
    store.save(path)
    raw = json.loads(path.read_text())
    assert raw["todos"][0]["due"] == "2024-03-05"
    loaded = TodoStore.load(path)
    assert [t.due for t in loaded] == [date(2024, 3, 5), None]

    legacy = tmp_path / "legacy.json"
    legacy.write_text(json.dumps({"version": 2, "todos": [
        {"id": 1, "title": "Old", "done": False, "priority": 2, "tags": [], "created": None}]}))
    (old,) = TodoStore.load(legacy)
    assert old.due is None and old.title == "Old"
