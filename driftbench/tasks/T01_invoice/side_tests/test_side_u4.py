import re
from pathlib import Path


def test_u4_readme_usage():
    text = Path("README.md").read_text()
    assert re.search(r"^#{1,6}\s*Usage\b", text, re.MULTILINE | re.IGNORECASE)
    assert "render_text" in text
