from pathlib import Path


def test_u4_readme_log_format_section():
    text = Path("README.md").read_text()
    assert "## Log format" in text and "HTTP/1.1" in text
