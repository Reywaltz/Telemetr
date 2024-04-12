from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo

from flask import request
from pyrogram import Client
from pyrogram.errors import BadRequest

timezone = ZoneInfo('Europe/Moscow')


def auth_required(fn):
    """Метод декоратор для проверки авторизации пользователя
    :return: Продолжение / прерывание обращения к API
    """
    @wraps(fn)
    def wrapper(self, **kwargs):
        if request.headers.get('Authorization') is None:
            return {"error": "no auth"}, 401

        request_token = request.headers.get('Authorization').split(' ')[-1]

        auth_code = self.user_storage.get_user_by_authcode(request_token)
        if auth_code is None:
            return {"error": "no auth"}, 401

        if auth_code.valid_to > datetime.now(timezone):
            return fn(self, **kwargs)
        else:
            return {"error": "no auth"}, 401

    return wrapper


def admin_auth_required(fn):
    """Метод декоратор для проверки авторизации пользователя
    :return: Продолжение / прерывание обращения к API
    """
    @wraps(fn)
    def wrapper(self, **kwargs):
        if request.headers.get('Authorization') is None:
            print("1111")
            return {"error": "no auth"}, 401

        access_token = request.headers.get('Authorization').split(' ')[-1]
        print(access_token)

        auth_code = self.admin_storage.get_admin_by_token(access_token)
        if auth_code is None:
            return {"error": "no auth"}, 401

        if auth_code.valid_to > datetime.now(timezone):
            return fn(self, **kwargs)
        else:
            return {"error": "no auth"}, 401

    return wrapper


def join_to_channel(teleg_client: Client, channel_login: str):
    """Метод подписки телеграм клиента на канал.
    При первом запуске необходимо войти в учётную запись Telegram

    :param channel_login:
        Юзернейм канала
        :type channel_login: str
    """
    try:
        with teleg_client:
            result = teleg_client.join_chat(channel_login)
        if result is not None and result.type == "channel":
            return result
        else:
            return None
    except BadRequest:
        return None


def leave_channel(teleg_client: Client, channel_login: str):
    """Метод отписки от телеграм канала

    :param teleg_client:
        Телеграм клиент
        :type teleg_client: Client
    :param channel_login:
        Логин канала
        :type channel_login: str
    """
    with teleg_client:
        teleg_client.leave_chat(channel_login, delete=True)
