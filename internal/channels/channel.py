from abc import ABC, abstractmethod
from dataclasses import dataclass


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
    def insert(self, channel: Channel):
        """Метод вставки нового канала

        :param channel: объект канала
        :type Channel: класс канала
        """
        pass

    @abstractmethod
    def get_channel_by_id(self, id: int) -> Channel:
        """Метод поиска канала по его ID в базе данных

        :param id:
            ID канала
            :type id: int
        :return: Канал
        :rtype: Channel
        """
        pass

    @abstractmethod
    def get_all(self,
                min_subcribers=0,
                max_subscribers=9999999999,
                min_views=0,
                max_views=9999999999,
                min_er=0,
                max_er=9999999999,
                min_cost=0,
                max_cost=9999999999,
                tg_link="%%",
                name="%%",
                limit=15,
                offset=0) -> list[Channel]:
        """Метод получения всех каналов из бд

        :return: Список каналов
        :rtype: list[Channel]
        """
        pass

    @abstractmethod
    def update_data_from_fetcher(self, channel: Channel):
        """Метод обновления данных каналов из Телеграм клиента

        :param channel:
            Объект канала
            :type channel: Channel
        """
        pass

    @abstractmethod
    def update_post_price(self, channel: Channel):
        """Метод обновления цены данных за пост

        :param channel:
            Объект канала
            :type channel: Channel
        """
        pass

    @abstractmethod
    def get_channels_to_doc(self, id_data: tuple):
        """Метод получения каналов, необходимых для добавления в EXEL файл

        :param
            id_data: ID каналов, которые нужно выгрузить
            :type id_data: tuple
        """
        pass

    @abstractmethod
    def delete(self, id: int):
        """Метод удаления канала

        :param id: ID канала
        :type id: int
        """
        pass
