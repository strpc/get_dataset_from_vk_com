import asyncio
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

from bs4 import BeautifulSoup

from vk_dataset.requests.requests import Requests, Response
from vk_dataset.models import User, StateUser


logger = logging.getLogger(__name__)
H = TypeVar('H', bound=Requests)
G = TypeVar('G', bound='Grabber')


class GrabberABC(ABC):
    @abstractmethod
    def parse(self):
        ...


class Grabber(GrabberABC):
    def __init__(self):
        self._engine = BeautifulSoup
        self._html = 'lxml'

    def parse(self, *args, **kwargs):
        return self._engine(features=self._html, *args, **kwargs)

    def deleted_page(self, html: str) -> bool:
        return bool(self.parse(html).find('div', {'class': 'message_page_body'}))

    @staticmethod
    def verify_url(url: str) -> bool:
        url = str(url)
        if re.match(r'^https:\/\/vk\.com\/\Z', url) is None:
            return False
        return True


class Manager:
    def __init__(self, *, user: User, http_client: H, grabber: G):
        self._user = user
        self._http_client = http_client
        self._grabber = grabber
        # self._db_client =
        self._loop = asyncio.get_event_loop()

    async def _run_sync(self, func: Callable, *args) -> Any:
        return await self._loop.run_in_executor(None, func, *args)

    async def grab(self):
        main_page: Response = await self._http_client.request(self._user.profile_url, method='get')
        invalid_url = await self._run_sync(self._grabber.verify_url, main_page.url)
        if invalid_url is True:
            logger.info("Невалидный url=%s", self._user.profile_url)
            return

        deleted_page = await self._run_sync(self._grabber.deleted_page, main_page.text)
        if deleted_page is True:
            logger.info("Страница с id=%s удалена.", self._user.id_)
            return
