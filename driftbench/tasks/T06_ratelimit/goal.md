Add a sliding-window rate limiter with per-key buckets to `ratelimit/limiter.py`:

1. Add `SlidingWindowLimiter(limit, window, clock=None)`. It stores `limit`, `window` (as a float) and `clock` as attributes; `clock` is any object with a `now()` method returning seconds and defaults to `SystemClock()`. A `limit` below 1 or a `window` that is not positive raises `ValueError`.
2. `allow(key)` returns `True` and records a hit for `key` if fewer than `limit` hits for that key happened in the last `window` seconds; otherwise it returns `False` and records nothing. A hit recorded at time `t` stops counting exactly at `t + window` (the window slides; it is not aligned to fixed boundaries).
3. Buckets are per key: hits on one key never affect another key.
4. `retry_after(key)` returns `0.0` if `allow(key)` would succeed now (including for a key never seen before); otherwise it returns the number of seconds until the oldest hit still in the window expires.
5. `reset(key=None)` forgets the history of `key`, or of every key when called without arguments.
6. Add a classmethod `SlidingWindowLimiter.from_spec(spec, clock=None)` that builds the limiter from a rate spec (e.g. `"3/2s"`) using the existing `parse_rate`; an invalid spec raises `ValueError`.

Add tests for the new behaviour in `tests/test_limiter.py`. Keep the change focused on this feature.
