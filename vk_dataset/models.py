from enum import Enum


class StateUser(Enum):
    opened = "opened"
    closed = "closed"
    hidden = 'hidden'
    deleted = 'deleted'


class User:
    def __init__(self, id_: int):
        self.id_ = id_
        self.state = StateUser.opened
        self.profile_url = f'https://vk.com/id{id_}'

        self.full_name = None
        self.description = None
        self.profile_html = None
        self.link_album = None
        self.html_album = None
        self.late_avatar = None
        self.late_avatar_jpg = None
        self.prelate_avatar = None
        self.prelate_avatar_jpg = None
