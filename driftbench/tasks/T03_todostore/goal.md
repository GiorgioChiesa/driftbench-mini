Add due dates to the todo library, mainly in `todostore/store.py`:

1. `Todo` gets an optional `due` field (a `datetime.date` or `None`, default `None`), and `TodoStore.add` accepts a keyword argument `due` (default `None`).
2. Add `parse_due(text)` to `todostore/store.py`. It accepts `YYYY-MM-DD` and `DD/MM/YYYY` (surrounding whitespace is ignored) and returns a `date`. Anything else, including impossible dates such as `2024-02-30`, raises `InvalidDueDate`, a new exception in `todostore/store.py` that subclasses `ValueError`.
3. `TodoStore.add(..., due=...)` also accepts a string, which is parsed with `parse_due`.
4. Add `TodoStore.overdue(today)`, which returns the pending todos whose due date is strictly before `today`, sorted by due date ascending (ties broken by id). Completed todos and todos without a due date are never overdue.
5. Add `TodoStore.set_due(todo_id, due)`, which sets the due date (a `date` or a string, as in `add`) or clears it when `due` is `None`. An unknown id raises `KeyError`.
6. Due dates survive `save`/`load` (stored as `YYYY-MM-DD`). Files written without a `due` key still load, with `due` set to `None`.

Add tests for the new behaviour in `tests/test_store.py`. Keep the change focused on this feature.
