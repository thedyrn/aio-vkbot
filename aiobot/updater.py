import asyncio
import aiohttp
import logging

from . import VkBot, Dispatcher

logger = logging.getLogger(__name__)


class Updater:
    def __init__(self, group_id, access_token, v):
        self.bot = VkBot(group_id, access_token, v)
        self.dispatcher = Dispatcher(self.bot)

    async def _start_polling(self):
        async with aiohttp.ClientSession() as session:
            self.bot.set_session(session)
            logger.debug('_create_session() - Create session.')

            while True:
                updates = await self.bot.get_updates()
                for update in updates:
                    await self.update_queue.put(update)

    async def _start(self):
        self.update_queue = asyncio.Queue()

        tasks = [self._start_polling(),
                 self.dispatcher.start(self.update_queue),
                 self.bot.manage_tasks()]

        await asyncio.gather(*tasks)

    def run(self):
        logger.info('run() - Bot is running! Start polling.')
        asyncio.run(self._start())
