from aiobot import State


def test_context_var():
    test_var = State()
    State.set_current(test_var)
    assert test_var == State.get_current()