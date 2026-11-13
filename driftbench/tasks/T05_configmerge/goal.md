Add layered configuration loading to `appconfig/loader.py`:

1. Add `load_config(schema, path=None, environ=None)`, which returns a dict with exactly the schema's keys (`"section.name"`). `path=None` means no INI file is read, and `environ=None` means no environment variables are read (`os.environ` is never consulted implicitly).
2. Layer precedence is: schema defaults < values from the INI file at `path` (read with the existing `ini` module) < environment variables.
3. Environment variables are read with `envsource.read_env` and the `APP_` prefix (`APP_DB__PORT` overrides `db.port`). Environment variables that do not match a schema key are ignored.
4. Every value, whatever layer it comes from, is coerced to its field's type (`str`, `int`, `float`, `bool`, `list`) with `coerce.coerce`. A default of `None` stays `None`.
5. A value that cannot be coerced raises `ConfigValueError`, a new exception in `loader.py` that subclasses `ValueError`. It has the attributes `key`, `value` (the raw, uncoerced value) and `source` (`"default"`, `"file"` or `"env"`).
6. A key in the INI file that is not declared in the schema raises `UnknownConfigKey`, a new exception in `loader.py` that subclasses `KeyError`, with the offending name in its `key` attribute.

Add tests for the new behaviour in `tests/test_loader.py`. Keep the change focused on this feature.
