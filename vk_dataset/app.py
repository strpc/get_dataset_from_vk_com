import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vk_dataset.requests.requests import Client
from vk_dataset.models import User
from vk_dataset.service import Manager, Grabber
from vk_dataset.utils import setup_logger


async def main():
    # for i in range(20):
    user = User(3)
    manager = Manager(http_client=Client(), user=user, grabber=Grabber())
    await asyncio.gather(manager.grab())


if __name__ == '__main__':
    setup_logger()
    asyncio.run(main())
