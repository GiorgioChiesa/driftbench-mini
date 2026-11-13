from todostore.models import Todo
from todostore.render import render_line, render_table, summary


def test_render_line_pending_with_tags():
    todo = Todo(3, "Buy milk", tags=["home", "errands"])
    assert render_line(todo) == "[ ]   3  Buy milk  #home #errands"


def test_render_line_done_high_priority():
    todo = Todo(12, "Pay rent", done=True, priority=1)
    assert render_line(todo) == "[x]  12  Pay rent  (!)"


def test_render_table_empty():
    assert render_table([]) == "(no todos)"


def test_summary(store):
    store.complete(1)
    assert summary(store.all()) == "3 todos, 1 done"
