from pathlib import Path


def test_u4_readme_csv_section():
    text = Path("README.md").read_text()
    assert "## CSV input" in text
    assert "read_csv" in text.split("## CSV input", 1)[1]
