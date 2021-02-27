from dataclasses import dataclass

from internal.channels import channel
from internal.postgres import postgres
from psycopg2 import IntegrityError

insert_channel_fields = "owner, name, " + \
                        "tg_link, tg_id, category, sub_count, " + \
                        "avg_coverage, er, cpm, post_price, photo_path"

select_all_channel_fields = "id, " + insert_channel_fields


default_limit = 5
default_offset = 0

er_range = "(er between %s and %s)"
avg_coverage_range = "(avg_coverage between %s and %s)"
cpm_range = "(cpm between %s and %s)"
sub_count_range = "(sub_count between %s and %s)"
post_price_range = "(post_price between %s and %s)"
tg_link_search = "(tg_link ILIKE %s)"
tg_name_search = "(name ILIKE %s)"
category_search = "(category ILIKE %s)"
limit_value = "%s"
offset_value = "%s"


@dataclass
class ChannelStorage(channel.Storage):
    """Реализация абстрактного класса Storage канала"""

    db: postgres.DB

    get_channels_query = f"SELECT {select_all_channel_fields} FROM channels \
                          WHERE {sub_count_range} AND \
                          {avg_coverage_range} AND \
                          {er_range} AND \
                          {post_price_range} AND \
                          {tg_link_search} AND \
                          {tg_name_search} AND \
                          {category_search} \
                          ORDER BY id \
                          LIMIT {limit_value} \
                          OFFSET {offset_value}"

    get_rows_query = f"SELECT COUNT(*) FROM channels \
                      WHERE {sub_count_range} AND \
                      {avg_coverage_range} AND \
                      {er_range} AND \
                      {post_price_range} AND \
                      {tg_link_search} AND \
                      {tg_name_search} AND \
                      {category_search}"

    get_channel_by_id_query = f"SELECT {select_all_channel_fields} \
                               FROM channels WHERE id = %s"

    get_channels_in_range_query = f"SELECT {select_all_channel_fields} \
                                    FROM channels WHERE id IN %s ORDER BY id"

    update_channel_fields_query = "UPDATE channels SET sub_count=%s, \
                                   avg_coverage=%s, er=%s, photo_path=%s, \
                                   tg_link=%s, cpm=%s \
                                   WHERE tg_id=%s RETURNING id"

    update_post_price_query = "UPDATE channels SET post_price=%s \
                              WHERE id = %s RETURNING ID"

    insert_channel_query = "INSERT INTO channels (" + insert_channel_fields + " ) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" # noqa

    get_user_channels_query = f"SELECT {select_all_channel_fields} FROM channels \
                              WHERE owner = %s"

    delete_channel_query = "DELETE FROM channels WHERE id=%s RETURNING ID"

    get_channel_by_teleg_id_query = f"SELECT {select_all_channel_fields} \
                                     FROM channels WHERE tg_id = %s"

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
                category="%%",
                limit=default_limit,
                offset=default_offset) -> list[channel.Channel]:
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
                                                 category,
                                                 limit,
                                                 offset))
        row = cursor.fetchall()
        ch_list = scan_channels(row)

        cursor.execute(self.get_rows_query, (min_subcribers,
                                             max_subscribers,
                                             min_views,
                                             max_views,
                                             min_er,
                                             max_er,
                                             min_cost,
                                             max_cost,
                                             tg_link,
                                             name,
                                             category,
                                             ))

        total = cursor.fetchone()[0]
        # print(total)

        return ch_list, total

    def insert(self, channel: channel.Channel) -> bool:
        """Метод добавления канала в БД

        :param channel:
            Объект канала
            :type channel: Channel
        :return: Результат вставки в БД
        :rtype: bool
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(self.insert_channel_query, (channel.username,
                                                       channel.name,
                                                       channel.tg_link,
                                                       channel.tg_id,
                                                       channel.category,
                                                       channel.sub_count,
                                                       channel.avg_coverage,
                                                       channel.er,
                                                       channel.cpm,
                                                       channel.post_price,
                                                       channel.photo_path))
            self.db.session.commit()
            return True
        except IntegrityError:
            self.db.session.rollback()
            return False

    def get_channel_by_id(self, id: int) -> channel.Channel:
        """Метод получения пользователя в базе данных

        :param id:
            ID канала в БД
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

        :param channel:
            Объект канала
            :type channel: Channel
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(
                self.update_channel_fields_query, (channel.sub_count,
                                                   channel.avg_coverage,
                                                   channel.er,
                                                   channel.photo_path,
                                                   channel.tg_link,
                                                   channel.cpm,
                                                   channel.tg_id,
                                                   ))

            self.db.session.commit()

        except Exception as e:
            print(e)
            self.db.session.rollback()

    def update_post_price(self, channel: channel.Channel):
        """Метод обновления цены данных за пост

        :param channel:
            Объект канала
            :type channel: Channel
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(self.update_post_price_query, (channel.post_price,
                                                          channel.id,))
            data = cursor.fetchone()
            if data is None:
                return False
            else:
                self.db.session.commit()
                return True
        except Exception:
            self.db.session.rollback()
            return False

    def get_channels_to_doc(self, id_data: tuple) -> list[channel.Channel]:
        """Метод получения каналов, необходимых для добавления в EXEL файл

        :param
            id_data: ID каналов, которые нужно выгрузить
            :type id_data: tuple
        :return:
            Каналы из БД
            :rtype: list[channel.Channel]
        """
        cursor = self.db.session.cursor()
        try:
            cursor.execute(self.get_channels_in_range_query, (id_data, ))
        except Exception:
            self.db.session.rollback()
            return None
        row = cursor.fetchall()
        if row is not None:
            return scan_channels(row)
        else:
            return None

    def delete(self, id: int) -> bool:
        """Метод удаления канала

        :param
            id: ID канала
            :type id: int
        :return:
            Результат операции
            :rtype: bool
        """
        cursor = self.db.session.cursor()
        try:
            cursor.execute(self.delete_channel_query, (id, ))
            data = cursor.fetchone()
            if data == []:
                return False
            else:
                self.db.session.commit()
                return True
        except Exception:
            self.db.session.rollback()
            return False

    def get_user_channels(self, user_id: int):
        """Получения списка каналов пользователя

        :param id:
            ID пользователя
            :type id: int
        :return: Список каналов
        :rtype: List[Channel]
        """
        cursor = self.db.session.cursor()
        try:
            cursor.execute(self.get_user_channels_query, (user_id, ))
        except Exception:
            self.db.session.rollback()
            return False
        data = cursor.fetchall()
        if data == []:
            return None
        else:
            return scan_channels(data)

    def get_channel_by_teleg_id(self, teleg_id: str):
        """Получение канала по Telegram ID в базе данных

        :param teleg_id:
            ID телеграмма
            :type teleg_id: str
        :return: Объект Telegrma канала
        :rtype: channel.Channel
        """
        cursor = self.db.session.cursor()
        try:
            cursor.execute(self.get_channel_by_teleg_id_query, (teleg_id, ))
            data = cursor.fetchone()
            if data is not None:
                return scan_channel(data)
            else:
                return []
        except Exception:
            self.db.session.rollback()
            return False


def scan_channel(data: tuple) -> channel.Channel:
    """Преобразование SQL ответа в объект Channel

    :param data:
        SQL ответ
        :type data: tuple
    :return: Объект канала
    :rtype: Channel
    """
    return channel.Channel(
        id=data[0],
        username=data[1],
        name=data[2],
        tg_link=data[3],
        tg_id=data[4],
        category=data[5],
        sub_count=data[6],
        avg_coverage=data[7],
        er=data[8],
        cpm=data[9],
        post_price=data[10],
        photo_path=data[11]
    )


def scan_channels(data: list[tuple]) -> list[channel.Channel]:
    """Функция преобразовния SQL ответа в список объектов Channel

    :param data: SQL ответ из базы
    :type data: list[tuple]
    :return: Список каналов
    :rtype: list[Channel]
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
