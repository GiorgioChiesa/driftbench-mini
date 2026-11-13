# ratelimit

Small building blocks for throttling and scheduling: an injectable clock, rate specs such as
`"10/min"`, a fixed-window limiter, retry back-off strategies and a tiny delayed-job scheduler.

Everything that depends on time takes a `clock` argument, so tests use `ManualClock` instead of
sleeping. Run the tests with `python -m pytest`.
