import asyncio
import aiohttp
import logging

from . import VkBot, Dispatcher

logger = logging.getLogger(__name__)


class Updater:
    def __init__(self, group_id, access_token, v):
        self.bot = VkBot(group_id, access_token, v)
        self.dispatcher = Dispatcher(self.bot)
        self.tasks = []

        self._polling = False
        self._closed = False

    async def _start_polling(self):
        async with aiohttp.ClientSession() as session:
            self.bot.set_session(session)
            logger.debug('Updater - Start session.')

            while self._polling:
                updates = await self.bot.get_updates()
                for update in updates:
                    await self.update_queue.put(update)

    def close(self):
        asyncio.create_task(asyncio.shield(self._close()))

    async def _close(self):
        self._closed = True
        self._polling = False
        self.dispatcher.close()
        self.bot.close()

    async def _start(self):
        if self._closed:
            return
        self.update_queue = asyncio.Queue()
        self._polling = True

        tasks = [self._start_polling(),
                 self.dispatcher.start(self.update_queue),
                 self.bot.manage_tasks()]

        await asyncio.gather(*tasks)

    def run(self):
        logger.info('run() - Bot is running! Start polling.')
        asyncio.run(self._start())
