from datetime import datetime, timedelta
from functools import wraps
from flask import request
from pyrogram import Client
from pyrogram.errors import BadRequest
import pytz

timezone = pytz.timezone('Europe/Moscow')


# TODO ПЕРЕПИСАТЬ ПОД АВТОРИЗАЦИЮ В ТЕЛЕГРАММЕ
def auth_required(fn):
    """Метод декоратор для проверки авторизации пользователя
    :return: Продолжение / прерывание обращения к API
    """
    @wraps(fn)
    def wrapper(self, **kwargs):
        if request.headers.get('Authorization') is None:
            return {"error": "no auth"}, 401

        request_token = request.headers.get('Authorization').split(' ')[-1]

        db_token = self.user_storage.get_uuid(request_token)
        if db_token is None:
            return {"error": "no auth"}, 401

        if db_token.created_at + timedelta(hours=12) > datetime.now(timezone):
            return fn(self, **kwargs)
        else:
            return {"error": "no auth"}, 401

    return wrapper


def join_to_channel(teleg_client: Client, channel_login: str):
    """Метод подписки телеграм клиента на канал.
    При первом запуске необходимо войти в учётную запись Telegram

    :param channel_login: Юзернейм канала
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
    with teleg_client:
        teleg_client.leave_chat(channel_login, delete=True)
