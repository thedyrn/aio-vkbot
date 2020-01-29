import pytest
import asyncio

from aiobot import Update, VkBot


@pytest.fixture(scope='session')
def raw_new_message_update():
    message_new = {'type': 'message_new',
                   'object': {
                       'message': {'date': 1577062062, 'from_id': 38895814,
                                   'id': 465, 'out': 0,
                                   'peer_id': 38895814, 'text': 'Test',
                                   'conversation_message_id': 465, 'fwd_messages': [],
                                   'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False},
                       'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link'],
                                       'keyboard': True,
                                       'lang_id': 0}
                   },
                   'group_id': 20350423,
                   'event_id': '549e36ec9c50fa7a28af9cbe4a2441f06688dd24'}
    return message_new


@pytest.fixture(scope='session')
def new_message_update(raw_new_message_update):
    return Update.from_dict(raw_new_message_update)


@pytest.fixture(scope='session')
def dummy_bot():
    return VkBot('123', '2141:abc', '5.103')


@pytest.fixture(scope='session')
@pytest.mark.asyncio
async def empty_update_queue() -> asyncio.Queue:
    queue = asyncio.Queue()
    return queue
