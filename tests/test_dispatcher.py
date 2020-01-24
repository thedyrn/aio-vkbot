import pytest
import asyncio
from unittest.mock import Mock

from aiobot import Dispatcher, MessageHandler


@pytest.fixture
@pytest.mark.asyncio
async def queue_with_event(new_message_update):
    queue = asyncio.Queue()
    await queue.put(new_message_update)
    return queue


@pytest.mark.asyncio
async def test_dispatcher(queue_with_event):
    mocked_callback = Mock()
    mocked_bot = Mock()
    dp = Dispatcher(mocked_bot)
    h = MessageHandler(mocked_callback)
    dp.add_handler(h)
    # TODO сделать остановку диспетячера и всего отсального
    task = asyncio.create_task(dp.start(queue_with_event))
    await asyncio.sleep(0.5)  # дать времени диспетчеру отработать
    assert mocked_callback.called
    task.cancel()
