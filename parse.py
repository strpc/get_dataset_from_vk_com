import aiohttp
from bs4 import BeautifulSoup as BS

import asyncio
import logging
import csv
from time import time
import re


# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - '
#                     '%(levelname)s - %(message)s')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
           'accept': '*/*'
           }


class User:
    active = True
    status = '' # closed/opened/hidden/deleted
    id_number = int()
    full_name = list()
    description = dict()
    link_profile = str()
    profile_html = str()
    link_album = str()
    html_album = str()
    late_avatar = str()
    late_avatar_jpg = str()
    prelate_avatar = str()
    prelate_avatar_jpg = str()

    def __init__(self, id_number):
        self.id_number = id_number
        self.link_profile = f'https://vk.com/id{id_number}'
        self.active = True

    def __str__(self):
        return f'Class user with id_number: {self.id_number}'

    def __repr__(self):
        return f'Class user with id_number: {self.id_number}'


async def get_html_main(session: aiohttp.client.ClientSession, user: User):
    async with session.get(url=user.link_profile, headers=headers) as response:
        url = str(response.url)
        if re.match(r'^https:\/\/vk\.com\/\Z', url) != None:
            # print('error page')
            user.active = False
        else:
            user.profile_html = await response.text()
            

def parse_main_page(user: User):
    if user.profile_html and user.active:
        soup = BS(user.profile_html, 'lxml')
    else:
        return
    try: #FIXME:
        deleted = soup.find('div', {'class': 'message_page_body'})
        if deleted:
            user.status = 'deleted'
            user.active = False
            print(user.status, user.link_profile)
    except:
        # print('произошла ошибка при попытке поиска текста "Страница "'
                                            # '"удалена либо ещё не создана."')
        pass
   
    try:
        closed = soup.find('div', {'class': 'profile_closed_wall_dummy_title'})
        if closed:
            user.status = 'closed'
            img = soup.find('img', {'class': 'page_avatar_img'})
            user.late_avatar_jpg = img.get('src')
            user.full_name = img.get('alt')
            # NOTE: доделать дополнение всей информации в user.description
            print(f'Закрытая страница {user.link_profile} {user.late_avatar_jpg}, {user.full_name}')
    except:
        pass
        # print('Произошла ошибка. Эта страница не скрыта')
    
    try:
        hidden = soup.find('div', {'class': 'page_current_info'}).text
        if hidden == 'Страница скрыта':
            user.status = 'hidden'
            user.full_name = soup.find('h1', {'class': 'page_name'}).text
            print(f'Скрытая страница {user.link_profile}, {user.full_name}')
    except:
        # print('Произошла ошибка при опознании скрытой страницы')
        pass
    
    try:
        # div = soup.find('div', {'class': 'page_top'})
        opened = soup.find('a', {'id': 'profile_photo_link'})
        if opened:
            user.status = 'opened'
            user.link_album = f'https://vk.com/album{user.id_number}_0?rev=1'
            user.full_name = soup.find('h1', {'class': 'page_name'}).text
            # NOTE: доделать пополнение всей оставшейся информации в словарь user.description
            print(user.status, user.full_name)
    except:
        pass


async def get_album_page(session: aiohttp.client.ClientSession, user: User):
    '''ЗАПРОСЫ НА СТРАНИЦУ'''
    async with session.get(url=user.link_album, headers=headers) as response:
        user.html_album = await response.text()


def get_link_avatar(user: User):
    # print(user.id_number)
    soup = BS(user.html_album, 'lxml')
    try:
        divs = soup.find_all('div', {'class': 'photos_row'})
        user.late_avatar = f"https://vk.com{divs[0].find('a').get('href')}"
        print(f'Добавлена ссылка на последнюю аватарку - {user.late_avatar}')
    except:
        pass
    #     print('Ошибка при получении ссылки на последнюю аватарку')
    #     print(user.link_album)
    try:
        divs = soup.find_all('div', {'class': 'photos_row'})
        user.prelate_avatar = f"https://vk.com{divs[1].find('a').get('href')}"
        print(f'Добавлена ссылка на последнюю аватарку - {user.prelate_avatar}')
    except:
        pass
    #     print('Ошибка при получении ссылки на предпоследнюю аватарку')
    # print(*link)
    
    
async def get_full_avatar(session: aiohttp.client.ClientSession, user: User):
    if user.late_avatar:
        async with session.get(url=user.late_avatar, headers=headers) as response:
            user.late_avatar = await response.text()
        with open('ava.html', 'w', encoding='utf-8') as f:
            f.write(user.late_avatar)
    if user.prelate_avatar:
        async with session.get(url=user.prelate_avatar, headers=headers) as response:
            user.prelate_avatar = await response.text()
    # print(user.late_avatar)
        

def get_jpg_link(user: User):
    if user.late_avatar:
        late = BS(user.late_avatar, 'lxml')
        div = late.find('div', {'class': 'pv_photo'})
        user.late_avatar_jpg = div.find('img').get('src')
        print(user.late_avatar_jpg)
    if user.prelate_avatar:
        prelate = BS(user.prelate_avatar, 'lxml')
        div = prelate.find('div', {'class': 'pv_photo'})
        user.prelate_avatar_jpg = div.find('img').get('src')
        print(user.prelate_avatar_jpg)


async def run_app(user: User):
    tasks = []
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(get_html_main(session=session, user=user))
        tasks.append(task)
        await asyncio.gather(*tasks)
    parse_main_page(user)
    
    
    if user.link_album:
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(get_album_page(session=session,
                                                        user=user)
                                        )
            tasks.append(task)
            await asyncio.gather(*tasks)
    get_link_avatar(user=user)
    
    
    if user.html_album:
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(get_full_avatar(session=session,
                                                        user=user)
                                        )
            tasks.append(task)
            await asyncio.gather(*tasks)
    # get_jpg_link(user=user)
    


if __name__ == '__main__':
    start_time = time()
    users = []
    for i in range(1, 11):
        users.append(User(id_number=i))
        asyncio.run(run_app(User(id_number=i)))
    # asyncio.run(run_app(User(id_number=1)))
    
        
    # for i in users:
    #     print(i.link_album, i.late_avatar)
    print(f"Passed {round(time() - start_time, 2)} sec")
