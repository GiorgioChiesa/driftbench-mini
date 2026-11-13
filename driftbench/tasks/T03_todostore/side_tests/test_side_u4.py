from pathlib import Path


def test_u4_readme_usage():
    text = Path("README.md").read_text()
    assert "## Usage" in text and "TodoStore" in text.split("## Usage", 1)[1]
