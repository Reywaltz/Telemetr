from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Category:
    """Класс пользователя"""
    name: str

    def to_json(self) -> dict:
        """Метод представления объекта в JSON"""
        return {"name": self.name}


class Storage(ABC):
    """Абстрактный класс категорий"""
    @abstractmethod
    def insert(self, category: Category):
        """Метод создания новой категории

        :param user: Новая категория
        :type user: Category
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Category]:
        """Метод получения всех категорий"""
        pass
