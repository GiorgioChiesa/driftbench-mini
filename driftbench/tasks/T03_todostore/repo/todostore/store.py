"""In-memory todo collection with JSON persistence."""
from __future__ import annotations

from datetime import date
from typing import Iterable, Iterator

from . import storage
from .models import Todo
from .tags import normalize_tags


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
            created: date | None = None) -> Todo:
        todo = Todo(id=self._next_id, title=title.strip(), priority=priority,
                    tags=normalize_tags(tags), created=created)
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

    def save(self, path) -> None:
        storage.save([todo.to_dict() for todo in self.all()], path)

    @classmethod
    def load(cls, path) -> "TodoStore":
        return cls(Todo.from_dict(raw) for raw in storage.load(path))
