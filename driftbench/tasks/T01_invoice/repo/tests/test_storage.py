from invoice import storage


def test_roundtrip(sample, tmp_path):
    path = tmp_path / "inv.json"
    storage.save(sample, path)
    loaded = storage.load(path)
    assert storage.to_dict(loaded) == storage.to_dict(sample)
