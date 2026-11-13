from pathlib import Path


def test_u4_readme_supported_units():
    text = Path("README.md").read_text()
    assert "## Supported units" in text
    section = text.split("## Supported units", 1)[1]
    assert "km" in section and "lb" in section
