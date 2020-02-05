import pytest
import asyncio
import aiohttp

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
def bot_records():
    return {'group_id': '123', 'access_token': '2141:abc', 'v': '5.103'}


@pytest.fixture(scope='module')
async def empty_update_queue() -> asyncio.Queue:
    queue = asyncio.Queue()
    return queue


@pytest.fixture(scope='session')
async def client_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(scope='module')
def dummy_bot(bot_records, client_session):
    bot = VkBot(**bot_records)
    bot.set_session(client_session)
    return bot


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
