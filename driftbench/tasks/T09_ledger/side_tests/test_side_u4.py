from pathlib import Path


def test_u4_readme_data_model():
    text = Path("README.md").read_text()
    assert "## Data model" in text
    assert "cents" in text.split("## Data model", 1)[1]
