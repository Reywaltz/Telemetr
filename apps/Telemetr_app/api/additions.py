from datetime import datetime, timedelta
from functools import wraps
from flask import request
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
