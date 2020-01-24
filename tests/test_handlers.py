import pytest
from unittest.mock import Mock
from aiobot import Handler, MessageHandler, CommandHandler, VkEventType, Update


@pytest.fixture
def update_from_dict(new_message_update):
    return Update.from_dict(new_message_update)


def test_handler(update_from_dict):
    mocked_callback = Mock()
    h = Handler(mocked_callback, VkEventType.MESSAGE_NEW)
    assert h.check_update(update_from_dict)
    h.handle_update(update_from_dict, Mock())
    assert mocked_callback.called


def test_message_handler(update_from_dict):
    mocked_callback = Mock()
    h = MessageHandler(mocked_callback)
    assert h.check_update(update_from_dict)
    h.handle_update(update_from_dict, Mock())
    assert mocked_callback.called

    # TODO CommandHandler добавить
