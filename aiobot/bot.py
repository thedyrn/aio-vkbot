import random
import asyncio
from aiohttp import ClientSession
from typing import List
import time
from collections import deque
import logging

from .constants import API_URL
from .exceptions import VkError, NoneSessionError

logger = logging.getLogger(__name__)


class VkBot:
    def __init__(self, group_id: str, access_token: str, v: str) -> None:
        self.group_id = group_id
        self.access_token = access_token
        self.api_version = v
        self.session = None
        self.tasks = deque([])

        self.key, self.server, self.ts = None, None, None

    def set_session(self, session: ClientSession) -> None:
        self.session = session
        logger.info('Set the session')

    async def manage_tasks(self):
        # TODO следить за закрытием всех задач
        while True:
            await asyncio.sleep(0.1)
            if len(self.tasks) == 0:
                continue

            task: asyncio.Task = self.tasks.popleft()
            # TODO может стоит сделать 'await task_name' ?
            # TODO сделать обработку задач по готовности, в asyncio есть что-то подобное

            if task.done():
                try:
                    result = task.result()
                    if 'error_code' in result:
                        # if result.get('error_code', None) is not None:
                        # TODO добавить дебаг режим, без которого ошибки просто пишутся в лог
                        raise VkError(result['error_code'],
                                      result.get('error_message', None),
                                      result.get('request_params', None))
                        # TODO сделать ошибки поточнее
                except asyncio.CancelledError:
                    pass
                except asyncio.InvalidStateError:
                    # Not yet
                    self.tasks.append(task)
                # Обрабатывать больше ошибок?
            else:
                self.tasks.append(task)

    def send_message(self,
                     peer_id: str,
                     message: str,
                     user_id: str = None,
                     domain: str = None,
                     chat_id: str = None,
                     user_ids: List[str] = None,
                     lat: float = None,
                     lon: float = None,
                     attachment: str = None,
                     reply_to: str = None,
                     forward_messages: List[str] = None,
                     sticker_id: str = None,
                     payload: str = None,
                     keyboard: dict = None,
                     dont_parse_links: bool = None,
                     disable_mentions: bool = None,
                     intent: str = None):
        send_msg_task = asyncio.create_task(
            self._send_message(peer_id, message, user_id, domain, chat_id, user_ids, lat, lon,
                               attachment, reply_to, forward_messages, sticker_id, payload,
                               keyboard, dont_parse_links, disable_mentions, intent))
        self.tasks.append(send_msg_task)

    def get_users_sync(self, users: list):
        # TODO не работает
        get_users_task = asyncio.create_task(self._get_users(users))
        while True:
            if get_users_task.done():
                return get_users_task.result()
            else:
                time.sleep(0.05)

    async def _send_message(self,
                            peer_id: str,
                            message: str,
                            user_id: str = None,
                            domain: str = None,
                            chat_id: str = None,
                            user_ids: List[str] = None,
                            lat: float = None,
                            lon: float = None,
                            attachment: str = None,
                            reply_to: str = None,
                            forward_messages: List[str] = None,
                            sticker_id: str = None,
                            payload: str = None,
                            keyboard: str = None,
                            dont_parse_links: bool = None,
                            disable_mentions: bool = None,
                            intent: str = None) -> dict:
        # TODO kwargs?!
        params = {
            'user_id': user_id, 'peer_id': peer_id, 'domain': domain, 'chat_id': chat_id, 'user_ids': user_ids,
            'message': message, 'lat': lat, 'lon': lon, 'attachment': attachment, 'reply_to': reply_to,
            'forward_messages': forward_messages, 'sticker_id': sticker_id,
            'payload': payload, 'keyboard': keyboard, 'dont_parse_links': dont_parse_links,
            'disable_mentions': disable_mentions, 'intent': intent,
            'random_id': str(random.randint(0, 10 ** 6)),
            'group_id': self.group_id, 'access_token': self.access_token, 'v': self.api_version
        }
        params = {key: value for key, value in params.items() if value is not None}
        result = await self._request('messages.send', params)
        # if (result.get('response', None) is None or
        #         result.get('message_id', None) is None):
        if 'response' in result or 'message_id' in result:
            # TODO найти как переделать боле лаконично
            # Нельзя верить документации вк
            return result
        else:
            pass
        # TODO проверка доставки сообщения
        # TODO проверка на ошибки и доставку, (?) random_id сделать получше

    async def _update_long_poll_server(self):
        params = {'group_id': self.group_id, 'access_token': self.access_token, 'v': self.api_version}
        resp = await self._request('groups.getLongPollServer', params)
        self.key, self.server, self.ts = resp['response'].values()

    async def get_updates(self, wait: int = 25) -> list:
        logger.info('VkBot._get_updates() - Check updates')
        if self.server is None or self.key is None:
            await self._update_long_poll_server()
            # TODO локальных переменных не хватит? get_updates(self, key, server, ts, session)

        params = {'act': 'a_check', 'key': self.key, 'ts': self.ts, 'wait': wait}
        res = await self._request(url=self.server, params=params, method='')
        if 'failed' in res:
            if res['failed'] == 1:
                self.ts = res['ts']
                return await self.get_updates()
            elif res['failed'] == 2 or res['failed'] == 3:
                await self._update_long_poll_server()
                return await self.get_updates()
        else:
            self.ts, updates = res.values()
            return updates

    async def _get_users(self, user_ids: list, fields: list = None, name_case: str = None):
        params = {'user_ids': ','.join(user_ids),
                  'group_id': self.group_id,
                  'access_token': self.access_token,
                  'v': self.api_version}
        if fields is not None:
            params['fields'] = ','.join(fields)
        if name_case is not None:
            params['name_case'] = name_case
        result = await self._request('users.get', params)
        return result

    async def _request(self, method: str, params: dict, url: str = API_URL) -> dict:
        if self.session is None:
            raise NoneSessionError('Bot session not set! Use bot.set_session()')

        logger.debug(f'requested: {method=}, {params=} {url=}')
        async with self.session.get(url + method, params=params) as response:
            response.raise_for_status()
            return await response.json()