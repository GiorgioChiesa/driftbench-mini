# logstats

Small toolkit for web-server access logs: parse Combined Log Format lines (with nginx's trailing
`$request_time`), group requests by endpoint, compute summary statistics and print plain-text reports.

```python
from logstats.parser import parse_file
from logstats import report

records = parse_file("access.log")
print(report.summary_text(records))
```

Run the tests with `python -m pytest`.
