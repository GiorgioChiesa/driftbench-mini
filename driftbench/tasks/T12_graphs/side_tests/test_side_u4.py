from pathlib import Path


def test_u4_readme_edge_list_section():
    text = Path("README.md").read_text()
    assert "## Edge-list format" in text and "parse_edge_list" in text
