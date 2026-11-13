"""logstats: parse web-server access logs and summarise them."""
from .parser import LogRecord, ParseError, parse_file, parse_line, parse_lines

__version__ = "0.2.3"
__all__ = ["LogRecord", "ParseError", "parse_file", "parse_line", "parse_lines"]
