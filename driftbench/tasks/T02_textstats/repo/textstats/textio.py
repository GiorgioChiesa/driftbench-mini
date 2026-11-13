"""Reading text files."""


def read_text(path, encoding: str = "utf-8") -> str:
    with open(path, encoding=encoding) as fh:
        return fh.read()
