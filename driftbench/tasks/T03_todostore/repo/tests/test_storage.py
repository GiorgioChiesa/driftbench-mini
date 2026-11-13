import json

from todostore import TodoStore, storage


def test_roundtrip_keeps_every_field(store, saved_path):
    store.complete(3)
    store.save(saved_path)
    loaded = TodoStore.load(saved_path)
    assert [t.to_dict() for t in loaded] == [t.to_dict() for t in store]


def test_file_is_versioned(saved_path):
    data = json.loads(saved_path.read_text())
    assert data["version"] == storage.SCHEMA_VERSION
    assert len(data["todos"]) == 3


def test_save_leaves_no_temporary_file(saved_path):
    assert sorted(p.name for p in saved_path.parent.iterdir()) == ["todos.json"]


def test_version1_bare_list_is_migrated(tmp_path):
    path = tmp_path / "old.json"
    path.write_text(json.dumps([{"id": 7, "title": "Legacy", "done": True, "tags": ["old"]}]))
    (todo,) = TodoStore.load(path)
    assert (todo.id, todo.done, todo.priority, todo.tags) == (7, True, 2, ["old"])


def test_ids_continue_after_load(saved_path):
    assert TodoStore.load(saved_path).add("Next").id == 4
