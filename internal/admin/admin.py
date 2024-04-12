from abc import ABC, abstractmethod
from dataclasses import dataclass

from datetime import datetime


@dataclass
class Admin:
    """Класс админа"""
    id: int
    username: str
    password: str
    access_token: str
    created_at: datetime
    valid_to: datetime

    def to_json(self) -> dict:
        """Метод представления объекта в JSON"""
        return {"id": self.id,
                "username": self.username,
                "password": self.password,
                "access_token": self.access_token,
                "created_at": self.created_at,
                "valid_to": self.valid_to
                }


class Storage(ABC):
    """Абстрактный класс администратора"""

    @abstractmethod
    def get_admin_by_token(self, access_token: str) -> list[Admin]:
        """Метод получения администратора по токену"""
        pass

    @abstractmethod
    def get_admin(self, username: str) -> Admin:
        """Метод получения администратора по юзернейму"""
        pass

    @abstractmethod
    def update_token(self, admin: Admin) -> bool:
        pass
