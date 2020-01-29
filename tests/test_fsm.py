import pytest
from aiobot import State, FsmHandler, Handler, Update, VkBot


class PseudoHandler:
    def __init__(self, check=False, handle='None'):
        self.check = check
        self.handle = handle

    def check_update(self, update: Update) -> bool:
        return self.check

    def handle_update(self, update: Update, bot: VkBot):
        return self.handle


@pytest.fixture()
def dummy_state():
    return State(handlers=[PseudoHandler(), PseudoHandler(check=True, handle=State(PseudoHandler(), name='test')),
                           PseudoHandler()], name='dummy')


@pytest.fixture(scope='module')
def dummy_fsm(dummy_state):
    return FsmHandler(entry_points=dummy_state, fallbacks=dummy_state)


@pytest.fixture(scope='module')
def dummy_user(raw_new_message_update):
    return raw_new_message_update['object']['message']['peer_id']


def test_states(dummy_state, raw_new_message_update):
    # TODO State it's subclass of Handler???
    test_state = dummy_state
    assert test_state.check_update(raw_new_message_update)


def test_states_eq():
    assert State(name='test') == State(PseudoHandler(), name='test')


def test_fsm_default(dummy_fsm, dummy_user, dummy_state):
    fsm = dummy_fsm
    assert fsm.get_state(dummy_user) == dummy_state


def test_state_response(dummy_fsm, new_message_update, dummy_user, dummy_bot):
    fsm = dummy_fsm
    assert fsm.check_update(new_message_update)
    test_state = State(PseudoHandler(), name='test')
    assert fsm.handle_update(new_message_update, dummy_bot) == test_state
    assert fsm.get_state(dummy_user) == test_state


def test_end_state(dummy_fsm):
    assert dummy_fsm.EndState == dummy_fsm.EntryState


def test_fallbacks(dummy_state, dummy_bot, new_message_update):
    fsm = FsmHandler(entry_points=State(PseudoHandler()), fallbacks=dummy_state)
    assert fsm.handle_update(new_message_update, dummy_bot) == State(name='test')
