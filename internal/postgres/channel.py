from dataclasses import dataclass
from typing import List

from internal.channels import channel
from internal.postgres import postgres

insert_channel_fields = "owner, name, " + \
                        "tg_link, category, sub_count, " + \
                        "avg_coverage, er, cpm, post_price"

select_all_channel_fields = "id, " + insert_channel_fields


default_limit = 15
default_offset = 0

er_range = "(er between %s and %s)"
avg_coverage_range = "(avg_coverage between %s and %s)"
cpm_range = "(cpm between %s and %s)"
sub_count_range = "(sub_count between %s and %s)"
post_price_range = "(post_price between %s and %s)"
tg_link_search = "(tg_link ILIKE %s)"
tg_name_search = "(name ILIKE %s)"
limit_value = "%s"
offset_value = "%s"


@dataclass
class ChannelStorage(channel.Storage):
    """Реализация абстрактного класса Storage канала

    :param user:
        Абстрактный класс канала
        :type user: Storage
    """
    db: postgres.DB

    get_channels_query = f"SELECT {select_all_channel_fields} FROM channels \
                          WHERE {sub_count_range} AND \
                          {avg_coverage_range} AND \
                          {er_range} AND \
                          {post_price_range} AND \
                          {tg_link_search} AND \
                          {tg_name_search} \
                          ORDER BY id \
                          LIMIT {limit_value} \
                          OFFSET {offset_value}"

    get_channel_by_id_query = f"SELECT {select_all_channel_fields} \
                               FROM channels WHERE id = %s"

    update_channel_fields_query = "UPDATE channels SET sub_count=%s, \
                                   avg_coverage=%s, er=%s \
                                   WHERE tg_link=%s RETURNING id"

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
                limit=default_limit,
                offset=default_offset) -> List[channel.Channel]:
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
        :rtype: List[Channel]
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_channels_query, (min_subcribers,
                                                 max_subscribers,
                                                 min_views,
                                                 max_views,
                                                 min_er,
                                                 max_er,
                                                 min_cost,
                                                 max_cost,
                                                 tg_link,
                                                 name,
                                                 limit,
                                                 offset))
        row = cursor.fetchall()
        ch_list = scan_channels(row)

        return ch_list

    def create(self, channel: channel.Channel):
        """Метод добавления канала в БД

        :param channel: Объект канала
        :type channel: Channel
        """
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
