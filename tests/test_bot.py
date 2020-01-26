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
        # TODO надо заменить на ответ от вк
        _body = '{"ok":true,"result":' + json.dumps(message_dict) + '}'
        _headers = {'Server': 'nginx/1.12.2',
                    'Date': 'Tue, 03 Apr 2018 16:59:54 GMT',
                    'Content-Type': 'application/json',
                    'Content-Length': str(len(_body)),
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Expose-Headers': 'Content-Length,Content-Type,Date,Server,Connection',
                    'Strict-Transport-Security': 'max-age=31536000; includeSubdomains'}
        return _body, _headers
