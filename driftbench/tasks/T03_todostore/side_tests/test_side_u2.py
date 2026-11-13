from todostore.tags import normalize_tags


def test_u2_normalize_tags_drops_duplicates():
    assert normalize_tags(["work", "Home", "WORK", "home"]) == ["work", "home"]
