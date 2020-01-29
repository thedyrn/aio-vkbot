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
def dummy_user(new_message_update):
    return new_message_update['object']['message']['peer_id']


def test_states(dummy_state, new_message_update):
    # TODO State it's subclass of Handler???
    test_state = dummy_state
    assert test_state.check_update(new_message_update)


def test_states_eq():
    assert State(name='test') == State(PseudoHandler(), name='test')


def test_fsm_default(dummy_fsm, dummy_user, dummy_state):
    fsm = dummy_fsm
    assert fsm.conversations.get(dummy_user) == dummy_state


def test_state_response(dummy_fsm, new_message_update, dummy_user):
    fsm = dummy_fsm
    update = Update.from_dict(new_message_update)
    assert fsm.check_update(update)
    test_state = State(PseudoHandler(), name='test')
    assert fsm.handle_update(update, VkBot('123', '2141:abc', '5.103')) == test_state
    assert fsm.conversations.get(dummy_user) == test_state


def test_end_state(dummy_fsm):
    assert dummy_fsm.EndState == dummy_fsm.EntryState
