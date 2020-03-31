import aiohttp
from bs4 import BeautifulSoup as BS

import asyncio
import json
import logging
import csv
from time import time
import os
import re

from config import IMAGES_DIR, LOGS_DIR


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
        pass
   
    try:
        closed = soup.find('div', {'class': 'profile_closed_wall_dummy_title'})
        if closed:
            user.status = 'closed'
            img = soup.find('img', {'class': 'page_avatar_img'})
            user.late_avatar_jpg = img.get('src').split('?')[0]
            user.full_name = img.get('alt')
            # TODO: доделать дополнение всей информации в user.description
            print(f'Закрытая страница {user.link_profile} {user.late_avatar_jpg}, {user.full_name}')
    except:
        pass
    
    try:
        hidden = soup.find('div', {'class': 'page_current_info'}).text
        if hidden == 'Страница скрыта':
            user.status = 'hidden'
            user.full_name = soup.find('h1', {'class': 'page_name'}).text
            print(f'Скрытая страница {user.link_profile}, {user.full_name}')
    except:
        pass
    
    try:
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
    soup = BS(user.html_album, 'lxml')
    try:
        divs = soup.find_all('div', {'class': 'photos_row'})
        raw = divs[0].find('a').get('href')
        user.late_avatar = raw.split('/photo')[-1].split('?')[0]
        # print(f'Добавлена ссылка на последнюю аватарку - {user.late_avatar}')
    except:
        pass

    try:
        divs = soup.find_all('div', {'class': 'photos_row'})
        raw = divs[1].find('a').get('href')
        user.prelate_avatar = raw.split('/photo')[-1].split('?')[0]
        # print(f'Добавлена ссылка на предпоследнюю аватарку - {user.prelate_avatar}')
    except:
        pass
    
    
async def get_link_jpg(session: aiohttp.client.ClientSession, user: User):
    params = {'act': 'show',
              'al': 1,
              'list': '', # album1_0
              'module': 'photos',
              'photo': ''} # 1_456264771
    url = 'https://vk.com/al_photos.php'
    
    if user.late_avatar:
        uid_album = user.link_album.split('/')[-1].split('?')[0]
        params['list'] = uid_album
        params['photo'] = user.late_avatar

        async with session.get(url=url, headers=headers, params=params) as response:
            answer = await response.read()
        data = str(answer, encoding='utf-8', errors='ignore')[4:].strip()
        # with open('txt.json', 'w', encoding='utf-8') as f:
        #     f.write(data)
        js = json.loads(data)
        
        for i in js['payload'][1][3]:
            if i['id'] == user.late_avatar: 
                if i.get('z_src'):
                    user.late_avatar_jpg = i.get('z_src')
                    break
                elif i.get('y_src'):
                    user.late_avatar_jpg = i.get('y_src')
                    break
                elif i.get('x_src'):
                    user.late_avatar_jpg = i.get('x_src')
                    break

    # await asyncio.sleep(0.5)
    if user.prelate_avatar:
        params['photo'] = user.prelate_avatar
        async with session.get(url=url, headers=headers, params=params) as response:
            answer = await response.read()
        data = str(answer, encoding='utf-8', errors='ignore')[4:].strip()
        with open('txt.json', 'w', encoding='utf-8') as f:
            f.write(data)
        js = json.loads(data)
        
        for i in js['payload'][1][3]:
            if i['id'] == user.prelate_avatar: 
                if i.get('z_src'):
                    user.prelate_avatar_jpg = i.get('z_src')
                    break
                elif i.get('y_src'):
                    user.prelate_avatar_jpg = i.get('y_src')
                    break
                elif i.get('x_src'):
                    user.prelate_avatar_jpg = i.get('x_src')
                    break
    print(user.late_avatar_jpg, user.prelate_avatar_jpg)
        

async def download_jpg(session: aiohttp.client.ClientSession, user: User):
    if user.late_avatar_jpg:
        async with session.get(url=user.late_avatar_jpg, headers=headers) as response:
            jpg = await response.read()
        with open(os.path.join(os.getcwd(), IMAGES_DIR, user.late_avatar_jpg.split('/')[-1]), mode='wb') as file:
            file.write(jpg)

    if user.prelate_avatar:
        async with session.get(url=user.prelate_avatar_jpg, headers=headers) as response:
            jpg = await response.read()
        with open(os.path.join(os.getcwd(), IMAGES_DIR, user.prelate_avatar_jpg.split('/')[-1]), mode='wb') as file:
            file.write(jpg)
        


async def run_app(user: User):
    tasks = []
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(get_html_main(session=session, 
                                                 user=user))
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
            task = asyncio.create_task(get_link_jpg(session=session,
                                                       user=user)
                                        )
            tasks.append(task)
            await asyncio.gather(*tasks)
    
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(download_jpg(session=session,
                                           user=user)
                                    )
        tasks.append(task)
        await asyncio.gather(*tasks)
    
    


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
