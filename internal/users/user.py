from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class User:
    """Класс пользователя"""
    id: int
    username: str

    def to_json(self):
        """Метод представления объекта в JSON"""
        return {"id": self.id, "username": self.username}


class Storage(ABC):
    """Абстрактный класс пользователя"""
    @abstractmethod
    def create(self, user: User):
        """Метод  нового юзера

        :param user: Новый пользователь
        :type user: User
        """
        pass

    @abstractmethod
    def get_user_by_id(self, id: int) -> User:
        """Метод поиска пользователя по его ID в базе данных

        :param id: ID пользователя
        :type id: int
        :return: пользователь
        :rtype: User
        """
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass
