import pytest
from aiobot import State, FsmHandler, BaseHandler, Update, VkBot


class PseudoHandler(BaseHandler):
    def __init__(self, check=False, handle=None):
        self.check = check
        self.handle = handle

    def check_update(self, update: Update) -> bool:
        return self.check

    def handle_update(self, update: Update, bot: VkBot):
        return self.handle


@pytest.fixture(scope='module')
def dummy_state():
    return State(handlers=[PseudoHandler(), PseudoHandler(check=True, handle=State([PseudoHandler()], name='test'))],
                 name='dummy')


@pytest.fixture(scope='module')
def dummy_fsm(dummy_state):
    return FsmHandler(entry_points=dummy_state, fallbacks=dummy_state)


@pytest.fixture(scope='module')
def dummy_user(raw_new_message_update):
    return raw_new_message_update['object']['message']['peer_id']


def test_states(dummy_state, raw_new_message_update):
    # TODO State it's subclass of Handler???
    test_state = dummy_state
    test_state2 = State(name='test')
    assert test_state.name == 'dummy'
    assert test_state2.name == 'test'


def test_states_eq():
    assert State(name='test') == State([PseudoHandler()], name='test')


def test_states_hash(dummy_state):
    assert hash(State()) != hash(State())
    assert hash(dummy_state) == hash(State(name='dummy'))


def test_fsm_default(dummy_fsm, dummy_user, dummy_state):
    fsm = dummy_fsm
    assert fsm.get_state(dummy_user) == dummy_state


def test_state_response(dummy_fsm, new_message_update, dummy_user, dummy_bot):
    fsm = dummy_fsm
    assert fsm.check_update(new_message_update)
    test_state = State([PseudoHandler()], name='test')
    fsm.handle_update(new_message_update, dummy_bot)
    assert BaseHandler.get_current().handle_update(new_message_update, dummy_bot) == test_state
    assert fsm.get_state(dummy_user) == test_state


def test_fallbacks(dummy_state, dummy_bot, new_message_update, dummy_user):
    fsm = FsmHandler(entry_points=State([PseudoHandler()]), fallbacks=dummy_state)
    fsm.handle_update(new_message_update, dummy_bot)
    assert fsm.get_state(dummy_user) == State(name='test')
