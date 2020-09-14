from dataclasses import dataclass
from Telemetr_app.internal.channels import channel
from Telemetr_app.internal.postgres import postgres


@dataclass
class ChannelStorage(channel.Storage):

    db: postgres.DB

    get_channels_query = "SELECT * FROM channels ORDER BY id"

    get_channel_by_id_query = "SELECT * FROM channels WHERE id = %s"

    def get_all(self):
        cursor = self.db.session.cursor()
        cursor.execute(self.get_channels_query)
        row = cursor.fetchall()
        ch_list = scan_channels(row)

        return ch_list

    def create(self, channel):
        pass

    def get_channel_by_id(self, id):
        cursor = self.db.session.cursor()
        cursor.execute(self.get_channel_by_id_query, (id, ))
        row = cursor.fetchone()
        if row is not None:
            return scan_channel(row)
        else:
            return None


def scan_channel(data):
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


def scan_channels(data):
    """Функция преобразовния SQL ответа в список объектов Channels

    :param data: SQL ответ из базы
    :type data: List[tupple]
    :return: Список каналов
    :rtype: Channel[channel.Channel]
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
    :rtype: user.User
    """
    return ChannelStorage(db=db)
