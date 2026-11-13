from todostore.models import Todo
from todostore.render import summary


def test_u1_summary_singular():
    assert summary([Todo(1, "only one")]) == "1 todo, 0 done"
    assert summary([Todo(1, "a"), Todo(2, "b", done=True)]) == "2 todos, 1 done"
