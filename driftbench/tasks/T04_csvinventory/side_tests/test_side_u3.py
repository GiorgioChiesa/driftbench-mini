from inventory.csvio import read_items


def test_u3_comment_lines_are_ignored(tmp_path):
    path = tmp_path / "c.csv"
    path.write_text(
        "# exported from the ERP\n"
        "sku,name,on_hand,unit_cost\n"
        "A-100,Anchor,3,0.10\n"
        "# discontinued below\n"
        "B-200,Bolt,4,0.20\n",
        encoding="utf-8",
    )
    assert [item.sku for item in read_items(path)] == ["A-100", "B-200"]
