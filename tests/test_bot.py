import pytest
import aresponses
from aiobot import VkBot


class FakeVk(aresponses.ResponsesMockServer):
    def __init__(self, message_dict, **kwargs):
        super().__init__(**kwargs)
        self._body, self._headers = self.parse_data(message_dict)

    async def __aenter__(self):
        await super().__aenter__()
        _response = self.Response(text=self._body, headers=self._headers, status=200, reason='OK')
        self.add(self.ANY, response=_response)

    @staticmethod
    def parse_data(message_dict):
        import json
        _body = json.dumps(message_dict)
        _headers = {'Server': 'VK',
                    'Date': 'Wed, 01 Jan 2020 12:00:00 GMT',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Content-Length': str(len(_body)),
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-store',
                    'X-Frontend': 'front508123',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Expose-Headers': 'X-Frontend',
                    'Strict-Transport-Security': 'max-age=15768000'}
        return _body, _headers


def test_bot_init(bot_records):
    bot = VkBot(**bot_records)
    assert bot.access_token == bot_records['access_token']


@pytest.mark.asyncio
async def test_request(dummy_bot):
    response = {'response': 'ok'}
    async with FakeVk(response):
        assert await dummy_bot._request('get', {}) == response


@pytest.mark.asyncio
async def test_update_long_poll_server(dummy_bot):
    key, server, ts = '123124abc:key', 'https://api.vk.com/method/', '700'
    async with FakeVk({'response': {'key': key, 'server': server, 'ts': ts}}):
        await dummy_bot._update_long_poll_server()

    assert dummy_bot.server == server
    assert dummy_bot.key == key
    assert dummy_bot.ts == ts


@pytest.mark.asyncio
async def test_get_updates(dummy_bot):
    updates = [{"type": 'new_message'}]
    response = {"ts": "701", "updates": updates}
    async with FakeVk(response):
        res = await dummy_bot.get_updates()

    assert res == updates


@pytest.mark.asyncio
async def test__send_message(dummy_bot):
    success_answer = {'response': '701'}
    async with FakeVk(success_answer):
        assert await dummy_bot._send_message('123', 'test') == success_answer

    # TODO протестировать ошибки, проверить обработку задач
