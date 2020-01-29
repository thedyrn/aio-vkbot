from aiobot.utils import ContextInstanceMixin


class ContextClass(ContextInstanceMixin):
    pass


def test_context_var():
    test_var = ContextClass()
    ContextClass.set_current(test_var)
    assert test_var == ContextClass.get_current()