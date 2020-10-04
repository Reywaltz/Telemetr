from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Channel:
    """Класс канала"""
    id: int
    username: str
    name: str
    tg_link: str
    category: str
    sub_count: int
    avg_coverage: int
    er: int
    cpm: int
    post_price: int

    def to_json(self):
        """Метод представления объекта в JSON"""
        return {"id": self.id,
                "username": self.username,
                "name": self.name,
                "tg_link": self.tg_link,
                "category": self.category,
                "sub_count": self.sub_count,
                "avg_coverage": self.avg_coverage,
                "er": self.er,
                "cpm": self.cpm,
                "post_price": self.post_price
                }


class Storage(ABC):
    """Абстрактный класс пользователя"""
    @abstractmethod
    def create(self, channel: Channel):
        """Метод вставки нового канала

        :param channel: объект канала
        :type Channel: класс канала
        """
        pass

    @abstractmethod
    def get_channel_by_id(self, id: int) -> Channel:
        """Метод поиска канала по его ID в базе данных

        :param id: ID канала
        :type id: int
        :return: канал
        :rtype: Channel
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Channel]:
        """Метод получения всех каналов из бд

        :return: Список каналов
        :rtype: List[Channel]
        """
        pass
