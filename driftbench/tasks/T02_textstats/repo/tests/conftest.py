import pytest


@pytest.fixture
def text_file(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("The cat sat on the mat. The dog sat too!\n", encoding="utf-8")
    return p
