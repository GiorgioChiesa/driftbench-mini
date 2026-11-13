from units.rounding import ceil_to_step, floor_to_step


def test_u1_floor_and_ceil_to_step():
    assert floor_to_step(7.9, 5) == 5
    assert ceil_to_step(7.1, 5) == 10
    assert ceil_to_step(10, 5) == 10
