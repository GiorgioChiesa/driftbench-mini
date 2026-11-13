import pytest

from graphkit.pq import MinQueue


def test_pops_in_priority_order():
    q = MinQueue()
    for item, prio in [("c", 3), ("a", 1), ("b", 2)]:
        q.push(item, prio)
    assert [q.pop() for _ in range(3)] == [("a", 1), ("b", 2), ("c", 3)]
    assert len(q) == 0


def test_ties_pop_in_insertion_order():
    q = MinQueue()
    q.push("x", 1)
    q.push("y", 1)
    assert q.pop()[0] == "x"


def test_push_keeps_lower_priority():
    q = MinQueue()
    q.push("a", 1)
    q.push("a", 5)
    assert q.priority("a") == 1
    assert "a" in q


def test_pop_empty():
    with pytest.raises(KeyError):
        MinQueue().pop()
