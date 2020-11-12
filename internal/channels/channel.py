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
    photo_path: str

    def to_json(self) -> dict:
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
                "post_price": self.post_price,
                "photo_path": self.photo_path
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
                min_subcribers: int = 0,
                max_subscribers: int = 9999999999,
                min_views: int = 0,
                max_views: int = 9999999999,
                min_er: int = 0,
                max_er: int = 9999999999,
                min_cost: int = 0,
                max_cost: int = 9999999999,
                tg_link: str = "%%",
                name: str = "%%",
                limit: int = 15,
                offset: int = 0) -> list[Channel]:
        """Метод получения списка каналов из БД с параметрами фильтрации

        :param min_subcribers:
            Минимальное число подписчиков на канале, defaults: 0
            :type min_subcribers: int, optional
        :param max_subscribers:
            Максимальное число подписчиков на канале, default: 9999999999
            :type max_subscribers: int, optional
        :param min_views:
            Минимальное число просмотров на канале, default: 0
            :type min_views: int, optional
        :param max_views:
            Максимальное число просмотров на канале, default: 9999999999
            :type max_views: int, optional
        :param min_er:
            Минимальное параметр ER на канале, default: 0
            :type min_er: int, optional
        :param max_er:
            Максимальный параметр ER на канале, default: 9999999999
            :type max_er: int, optional
        :param min_cost:
            Минимальное значение стоймости просмотора на канале, default: 0
            :type min_cost: int, optional
        :param max_cost:
            Максимальное значение стоймости просмотора на канале,
            default: 9999999999
            :type max_cost: int, optional
        :param tg_link:
            Ссылка на телеграмм канал без @, defaults to "%%"
            :type tg_link: str, optional
        :param name:
            Имя канала, defaults to "%%"
            :type name: str, optional
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

        :param id:
            ID канала
            :type id: int
        """
        pass
