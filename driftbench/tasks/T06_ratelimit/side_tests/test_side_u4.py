from pathlib import Path


def test_u4_readme_development_section():
    text = Path("README.md").read_text()
    assert "## Development" in text
    section = text.split("## Development", 1)[1]
    assert "pytest" in section
