import aiohttp
from bs4 import BeautifulSoup as BS

import asyncio
import logging
import csv
from time import time
import re


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                    '%(levelname)s - %(message)s')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
           'accept': '*/*'
           }


class User:
    active = True
    id_number = int()
    link_profile = str()
    profile_html = str()
    link_album = str()
    html_album = str()
    full_name = list()
    late_avatar = str()
    prelate_avatar = str()

    def __init__(self, id_number):
        self.id_number = id_number
        self.link_profile = f'https://vk.com/id{id_number}'
        self.link_album = f'https://vk.com/album{id_number}_0?rev=1'
        self.active = True

    def __str__(self):
        return f'Class user with id_number: {self.id_number}'

    def __repr__(self):
        return f'Class user with id_number: {self.id_number}'


async def get_html_main(session: aiohttp.client.ClientSession, user: User):
    async with session.get(url=user.link_profile, headers=headers) as response:
        url = str(response.url)
        if re.match(r'^https:\/\/vk\.com\/\Z', url) != None:
            print('error page')
            user.active = False
        else:
            user.profile_html = await response.text()
            

def parse_main_page(user: User):
    if user.profile_html:
        soup = BS(user.profile_html, 'lxml')
    else:
        return
    try: #FIXME:
        div = soup.find('div', {'class': 'message_page_body'})
        # deleted = div('div', {'class': 'message_page_body'}).text
        print(div)
    except:
        pass

async def get_album_page(session: aiohttp.client.ClientSession, user: User):
    '''ЗАПРОСЫ НА СТРАНИЦУ'''
    if user.link_album == False:
        return
    async with session.get(url=user.link_album, headers=headers) as response:
        url = str(response.url)
        if re.match(r'^https:\/\/vk\.com\/\Z', url) != None:
            print('error page')
            user.link_profile = False
            user.link_album = False
            user.html_album = False
            user.full_name = False
            user.late_avatar = False
            user.prelate_avatar = False
        else:
            user.html_album = await response.text()


def get_link_avatar(user: User):
    if user.active:
        print(user.id_number)
        soup = BS(user.html_album, 'lxml')
        divs = soup.find_all('div', {'class': 'photos_row'})
        user.late_avatar = f"https://vk.com{divs[0].find('a').get('href')}"
        print(f'Добавлена ссылка на последнюю аватарку - {user.late_avatar}')
    # except:
    #     # pass
    #     print('Ошибка при получении ссылки на последнюю аватарку')
    #     print(user.link_album)
    # try:
        divs = soup.find_all('div', {'class': 'photos_row'})
        user.prelate_avatar = f"https://vk.com{divs[1].find('a').get('href')}"
        print(f'Добавлена ссылка на последнюю аватарку - {user.prelate_avatar}')
    # except:
    #     print('Ошибка при получении ссылки на предпоследнюю аватарку')
    # print(*link)
    
    
async def get_full_avatar(session: aiohttp.client.ClientSession, user: User):
    async with session.get(url=user.late_avatar, headers=headers) as response:
        user.late_avatar = await response.text()
    async with session.get(url=user.prelate_avatar, headers=headers) as response:
        user.prelate_avatar = await response.text()
    print('hello world')
        


# def get_jpg_link(user: User):
#     soup = BS(user.late_avatar, 'lxml')
    


async def run_app(user: User):
    tasks = []
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(get_html_main(session=session, user=user))
        tasks.append(task)
        await asyncio.gather(*tasks)
        
    parse_main_page(user)
    
    # async with aiohttp.ClientSession() as session:
    #     task = asyncio.create_task(get_album_page(session=session,
    #                                                 user=user)
    #                                 )
    #     tasks.append(task)
    #     await asyncio.gather(*tasks)
    # get_link_avatar(user)
    


if __name__ == '__main__':
    start_time = time()
    users = []
    for i in range(1, 10):
        users.append(User(id_number=i))
        asyncio.run(run_app(User(id_number=i)))
    # asyncio.run(run_app(User(id_number=1)))
    
        
    # for i in users:
    #     print(i.link_album, i.late_avatar)
    print(f"Passed {round(time() - start_time, 2)} sec")
