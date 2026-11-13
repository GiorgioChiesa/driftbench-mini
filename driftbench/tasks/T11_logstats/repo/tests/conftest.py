import pytest

from logstats.parser import parse_lines

# A short excerpt of a real access log. The fourth line was truncated by a crashed worker and
# is expected to be skipped by the default (lenient) parser.
SAMPLE_LOG = """
203.0.113.7 - alice [10/Oct/2023:13:55:36 +0000] "GET /api/users/42?full=1 HTTP/1.1" 200 2326 "https://example.com/" "Mozilla/5.0" 0.042
203.0.113.7 - alice [10/Oct/2023:13:55:40 +0000] "GET /static/app.js HTTP/1.1" 304 - "https://example.com/" "Mozilla/5.0" 0.001
198.51.100.2 - - [10/Oct/2023:13:56:02 +0000] "POST /api/orders HTTP/1.1" 500 87 "-" "curl/8.4.0" 1.250
198.51.100.2 - - [10/Oct/2023:13:56:0
192.0.2.33 - - [10/Oct/2023:13:57:10 +0000] "GET /api/users/7 HTTP/1.1" 404 12 "-" "python-requests/2.31" -
"""


@pytest.fixture
def records():
    return parse_lines(SAMPLE_LOG.splitlines())
