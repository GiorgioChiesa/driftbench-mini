Add per-endpoint statistics to `logstats/stats.py`:

1. `percentile(values, p)` returns the nearest-rank percentile: sort the values ascending, let `n` be their number and `rank = ceil(p * n / 100)` (at least 1), and return the value at 1-based position `rank`. It raises `ValueError` for an empty input or when `p` is not in the range `0 < p <= 100`.
2. `endpoint_stats(records)` returns a dict mapping each endpoint key, as computed by `endpoints.endpoint_key(record)`, to an `EndpointStats` frozen dataclass with fields `endpoint` (the key), `count` (number of requests), `p50_ms` and `p95_ms` (`percentile` of the records' `duration_ms` at 50 and 95).
3. `EndpointStats.error_rate` is the fraction of the endpoint's requests whose status is 500 or higher (4xx responses are not errors), as a `float` rounded to 4 decimal places.
4. Records whose `duration_ms` is `None` count towards `count` and `error_rate` but are left out of the percentiles; when an endpoint has no durations at all, `p50_ms` and `p95_ms` are `None`.
5. `slowest_endpoints(records, n=5)` returns a list with the `EndpointStats` of the `n` endpoints with the highest `p95_ms`, sorted by `p95_ms` descending and then by endpoint key ascending. Endpoints whose `p95_ms` is `None` are skipped, and `n <= 0` returns `[]`.
6. `filter_window(records, start=None, end=None)` returns a list of the records with `start <= record.time < end`, keeping their order. Each bound may be `None` (unbounded), a timezone-aware `datetime`, or an ISO-8601 string parsed with `timeutil.parse_iso`; a naive `datetime` raises `ValueError`. Comparisons are between aware datetimes, so records logged with different UTC offsets are compared correctly.

Add tests for the new behaviour in `tests/test_stats.py`. Keep the change focused on this feature.
