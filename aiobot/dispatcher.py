import asyncio
from typing import List
import logging

from .bot import VkBot
from .objects import Update
from .handler import Handler
from .utils import ContextInstanceMixin


logger = logging.getLogger(__name__)


class Dispatcher(ContextInstanceMixin):
    def __init__(self, bot: VkBot):
        self.bot = bot
        self.handlers: List[Handler] = []
        self.tasks: List[asyncio.Task] = []
        self._closed = False

    def add_handler(self, handler: Handler) -> None:
        self.handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        self.handlers.remove(handler)

    async def _process_update(self, update: Update):
        for handler in self.handlers:
            # TODO mb unite 'handle' and 'check' into one function?
            if handler.check_update(update):
                handler.handle_update(update, self.bot)
                break

    def close(self):
        self._closed = True

    async def start(self, update_queue: asyncio.Queue):
        while not self._closed:
            try:
                update_dict = await update_queue.get()
                update = Update.from_dict(update_dict)
                task = asyncio.create_task(self._process_update(update))
                self.tasks.append(task)

            except Exception as error:
                logger.error(f'Unexpected error: {error or "unknown error"}')

    # TODO сделать состояния как отдельные роутеры из aiogram, композитные фильтры для обработчиков
