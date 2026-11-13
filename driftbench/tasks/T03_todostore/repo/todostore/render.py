"""Plain-text rendering of todo lists."""
from __future__ import annotations

from typing import Sequence

from .models import Todo


def render_line(todo: Todo) -> str:
    """One line per todo: ``[x]  12  Title  (!)  #tag``."""
    mark = "x" if todo.done else " "
    line = f"[{mark}] {todo.id:>3}  {todo.title}"
    if todo.priority == 1:
        line += "  (!)"
    if todo.tags:
        line += "  " + " ".join(f"#{tag}" for tag in todo.tags)
    return line


def render_table(todos: Sequence[Todo]) -> str:
    if not todos:
        return "(no todos)"
    return "\n".join(render_line(todo) for todo in todos)


def summary(todos: Sequence[Todo]) -> str:
    done = sum(1 for todo in todos if todo.done)
    return f"{len(todos)} todos, {done} done"
