from todostore import TodoStore, storage


def test_u3_missing_file_loads_empty(tmp_path):
    missing = tmp_path / "missing.json"
    assert storage.load(missing) == []
    assert len(TodoStore.load(missing)) == 0
