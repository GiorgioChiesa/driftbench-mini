"""In-memory todo collection with JSON persistence."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Iterable, Iterator

from . import storage
from .models import Todo
from .tags import normalize_tags
from .timeutil import parse_iso_date

_EU_DATE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


class InvalidDueDate(ValueError):
    """Raised when a due date cannot be parsed."""


def parse_due(text: str) -> date:
    """Parse ``YYYY-MM-DD`` or ``DD/MM/YYYY`` (surrounding whitespace is ignored)."""
    raw = text.strip()
    try:
        match = _EU_DATE.match(raw)
        if match:
            day, month, year = (int(group) for group in match.groups())
            return date(year, month, day)
        return parse_iso_date(raw)
    except ValueError:
        raise InvalidDueDate(f"invalid due date: {text!r}") from None


def _coerce_due(value: date | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return parse_due(value)
    raise TypeError(f"due must be a date, a string or None, not {type(value).__name__}")


class TodoStore:
    """Holds todos keyed by id and hands out new ids sequentially."""

    def __init__(self, todos: Iterable[Todo] = ()) -> None:
        self._todos: dict[int, Todo] = {todo.id: todo for todo in todos}
        self._next_id = max(self._todos, default=0) + 1

    def __len__(self) -> int:
        return len(self._todos)

    def __iter__(self) -> Iterator[Todo]:
        return iter(self.all())

    def add(self, title: str, *, priority: int = 2, tags: Iterable[str] = (),
            created: date | None = None, due: date | str | None = None) -> Todo:
        todo = Todo(id=self._next_id, title=title.strip(), priority=priority,
                    tags=normalize_tags(tags), created=created, due=_coerce_due(due))
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo:
        try:
            return self._todos[todo_id]
        except KeyError:
            raise KeyError(f"no todo with id {todo_id}") from None

    def complete(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        todo.done = True
        return todo

    def remove(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        del self._todos[todo_id]
        return todo

    def all(self) -> list[Todo]:
        return [self._todos[key] for key in sorted(self._todos)]

    def pending(self) -> list[Todo]:
        return [todo for todo in self.all() if not todo.done]

    def with_tag(self, tag: str) -> list[Todo]:
        wanted = normalize_tags([tag])[0]
        return [todo for todo in self.all() if wanted in todo.tags]

    def by_priority(self) -> list[Todo]:
        """Pending todos, most urgent first (ties keep id order)."""
        return sorted(self.pending(), key=lambda todo: todo.priority)

    def set_due(self, todo_id: int, due: date | str | None) -> Todo:
        """Set (or clear, with ``None``) the due date of a todo."""
        todo = self.get(todo_id)
        todo.due = _coerce_due(due)
        return todo

    def overdue(self, today: date) -> list[Todo]:
        """Pending todos due strictly before ``today``, earliest first (ties by id)."""
        late = [todo for todo in self.pending() if todo.due is not None and todo.due < today]
        return sorted(late, key=lambda todo: (todo.due, todo.id))

    def save(self, path) -> None:
        storage.save([todo.to_dict() for todo in self.all()], path)

    @classmethod
    def load(cls, path) -> "TodoStore":
        return cls(Todo.from_dict(raw) for raw in storage.load(path))
