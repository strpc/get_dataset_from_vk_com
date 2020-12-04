# pylint: disable=too-few-public-methods, missing-module-docstring
from abc import ABC, abstractmethod
from typing import Dict, Union

from httpx import AsyncClient, Response


DEFAULT_USERAGENT = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 '
                  '(KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
}
GET = AsyncClient.get
POST = AsyncClient.post


class Requests(ABC):
    @abstractmethod
    async def request(self, url: str, *, method: str = 'get', **kwargs):
        ...


class Client(Requests):
    def __init__(self):
        self._client = AsyncClient

    @staticmethod
    def _check_useragent(kwargs) -> Dict:
        if (kwargs.get('headers') is not None
                and isinstance(kwargs['headers'], dict) is True
                and kwargs['headers'].get('user-agent') is None):
            kwargs['headers'].update(DEFAULT_USERAGENT)
        elif kwargs.get('headers') is None:
            kwargs['headers'] = DEFAULT_USERAGENT
        return kwargs

    async def request(self, url: str, *, method: str = 'get', **kwargs) -> Response:
        async with self._client() as client:
            kwargs = self._check_useragent(kwargs)
            method_client: Union[GET, POST] = getattr(client, method)
            return await method_client(url, **kwargs)
