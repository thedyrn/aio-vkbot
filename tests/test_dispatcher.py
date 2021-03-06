import pytest
import asyncio
from unittest.mock import Mock

from aiobot import Dispatcher, MessageHandler


@pytest.fixture
@pytest.mark.asyncio
async def queue_with_event(raw_new_message_update):
    queue = asyncio.Queue()
    await queue.put(raw_new_message_update)
    return queue


@pytest.mark.asyncio
async def test_dispatcher(queue_with_event):
    mocked_callback = Mock()
    mocked_bot = Mock()
    dp = Dispatcher(mocked_bot)
    h = MessageHandler(mocked_callback)
    dp.add_handler(h)
    task = asyncio.create_task(dp.start(queue_with_event))
    await asyncio.sleep(0.5)  # дать времени диспетчеру отработать
    assert mocked_callback.called
    task.cancel()


@pytest.mark.asyncio
async def test_dispatcher_close(queue_with_event):
    done_cb_called = False

    def done_callback(done_task):
        nonlocal done_cb_called
        print(f' Close Dispatcher: {done_task.__repr__()[1:14]}...')
        done_cb_called = True

    mocked_bot = Mock()
    dp = Dispatcher(mocked_bot)
    task = asyncio.create_task(dp.start(queue_with_event))
    task.add_done_callback(done_callback)
    dp.close()
    assert dp._closed
    await asyncio.sleep(0.5)
    assert done_cb_called
