from pathlib import Path


def test_u4_readme_templates_section():
    text = Path("README.md").read_text()
    assert "## Templates" in text and "render(" in text
