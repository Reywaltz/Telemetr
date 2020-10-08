from dataclasses import dataclass
from typing import List

from internal.channels import channel
from internal.postgres import postgres

insert_channel_fields = "chat_id, owner, name, " + \
                             "tg_link, category, sub_count, " + \
                             "avg_coverage, er, cpm, post_price"

select_all_channel_fields = "id, " + insert_channel_fields


@dataclass
class ChannelStorage(channel.Storage):
    """Реализация абстрактного класса Storage канала

    :param user: абстрактный класс канала
    :type user: Storage
    """
    db: postgres.DB

    get_channels_query = "SELECT * FROM channels ORDER BY id"

    get_channel_by_id_query = "SELECT * FROM channels WHERE id = %s"

    update_channel_fields_query = "UPDATE channels SET sub_count=%s, \
                                   avg_coverage=%s, er=%s \
                                   WHERE tg_link=%s RETURNING id"

    def get_all(self) -> List[channel.Channel]:
        """Метод получения списка каналов из БД

        :return: Список каналов
        :rtype: List[Channel]
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_channels_query)
        row = cursor.fetchall()
        ch_list = scan_channels(row)

        return ch_list

    def create(self, channel):
        pass

    def get_channel_by_id(self, id: int) -> channel.Channel:
        """Метод получения пользователя в базе данных

        :param id: ID канала в БД
        :type id: int
        :return: Канал из БД
        :rtype: Channel
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_channel_by_id_query, (id, ))
        row = cursor.fetchone()
        if row is not None:
            return scan_channel(row)
        else:
            return None

    def update_data_from_fetcher(self, channel: channel.Channel):
        """Метод обновления данных каналов из Телеграм клиента

        :param channel: Объект канала
        :type channel: Channel
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(
                self.update_channel_fields_query, (channel.sub_count,
                                                   channel.avg_coverage,
                                                   channel.er,
                                                   channel.tg_link))

            self.db.session.commit()
        except Exception:
            self.db.session.rollback()


def scan_channel(data: tuple) -> channel.Channel:
    """Преобразование SQL ответа в объект Channel

    :param data: SQL ответ
    :type data: tuple
    :return: Объект канала
    :rtype: Channel
    """
    return channel.Channel(
        id=data[0],
        username=data[1],
        name=data[2],
        tg_link=data[3],
        category=data[4],
        sub_count=data[5],
        avg_coverage=data[6],
        er=data[7],
        cpm=data[8],
        post_price=data[9]
    )


def scan_channels(data: List[tuple]) -> List[channel.Channel]:
    """Функция преобразовния SQL ответа в список объектов Channel

    :param data: SQL ответ из базы
    :type data: List[tuple]
    :return: Список каналов
    :rtype: List[Channel]
    """
    channels = []
    for row in data:
        channel = scan_channel(row)
        channels.append(channel)

    return channels


def new_storage(db: postgres.DB) -> ChannelStorage:
    """Функция инициализации хранилища канала

    :param db: объект базы данных
    :type db: postgres.DB
    :return: объект хранилища каналов
    :rtype: User
    """
    return ChannelStorage(db=db)
