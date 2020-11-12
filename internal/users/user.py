from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Класс пользователя"""
    id: int
    username: str
    telegram_id: str
    auth_code: str
    created_at: datetime
    valid_to: datetime

    def to_json(self):
        """Метод представления объекта в JSON"""
        return {"id": self.id,
                "username": self.username,
                "telegram_id": self.telegram_id,
                "auth_code": self.auth_code,
                "created_at": self.created_at,
                "valid_to": self.valid_to}


class Storage(ABC):
    """Абстрактный класс пользователя"""
    @abstractmethod
    def create(self, user: User):
        """Метод  нового юзера

        :param user:
            Новый пользователь
            :type user: User
        """
        pass

    @abstractmethod
    def get_user_by_id(self, id: int) -> User:
        """Метод поиска пользователя по его ID в базе данных

        :param id:
            ID пользователя
            :type id: int
        :return: пользователь
        :rtype: User
        """
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        """Метод получения всех пользователей в базе данных

        :return: Список пользователей
        :rtype: list[User]
        """
        pass

    @abstractmethod
    def get_user_by_authcode(self, auth_code: str) -> User:
        """Метод проверки авторизации пользователя через телеграм бота

        :param auth_code:
            Сгенерированный код с клиента
            :type auth_code: str
        :return: Пользователя с данным кодом
        :rtype: user.User
        """
        pass

    @abstractmethod
    def update_auth_key(self, user: User):
        """Метод обновления кода авторизации

        :param user:
            Объект пользователя
            :type user: user.User
        """
        pass
