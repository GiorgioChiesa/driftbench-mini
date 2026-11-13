# appconfig

Configuration loading for our services. Keys are named `section.name` and declared in a
schema of `Field`s (type, default, secret flag). Values come from INI files (`appconfig.ini`)
and from `APP_`-prefixed environment variables (`appconfig.envsource`); `appconfig.redact`
renders a configuration with secrets masked.

Run the tests with `python -m pytest`.
