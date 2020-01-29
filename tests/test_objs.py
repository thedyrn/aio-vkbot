from aiobot import Message, Update, VkEventType
import pytest


@pytest.fixture
def msg_obj(raw_new_message_update):
    message = raw_new_message_update['object']['message']
    msg_obj = Message(date=message['date'], from_id=message['from_id'], msg_id=message['id'],
                      peer_id=message['peer_id'], text=message['text'],
                      attachments=message['attachments'], fwd_messages=message['fwd_messages'],
                      important=message['important'])
    return msg_obj


def test_message_from_dict(raw_new_message_update, msg_obj):
    msg_from_dict = Message.from_dict(raw_new_message_update['object']['message'])
    assert msg_from_dict == msg_obj


def test_update_from_dict(raw_new_message_update, msg_obj):
    upd = Update.from_dict(raw_new_message_update)
    assert upd.message == msg_obj
    assert upd.type == VkEventType.MESSAGE_NEW
    assert isinstance(upd, Update)
