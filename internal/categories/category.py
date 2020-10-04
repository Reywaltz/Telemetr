from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Category:
    """Класс пользователя"""
    name: str

    def to_json(self):
        """Метод представления объекта в JSON"""
        return {"name": self.name}


class Storage(ABC):
    """Абстрактный класс категорий"""
    @abstractmethod
    def create(self, category: Category):
        """Метод создания новой категории

        :param user: Новая категория
        :type user: Category
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Category]:
        pass
