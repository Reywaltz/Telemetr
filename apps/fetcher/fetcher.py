import datetime
from dataclasses import dataclass

from internal.channels import channel
from internal.telegram.client import TelegramClient
from pkg.log import logger
from pyrogram.types import Dialog, Message
from pyrogram.errors.exceptions import ChannelPrivate
from zoneinfo import ZoneInfo

tz = ZoneInfo("Europe/Moscow")

DAYS = 14
channel_img_folder = "channel_img/"


@dataclass
class Fetcher:
    """Класс парсер данных из каналов"""
    logger: logger.Logger
    tg_client: TelegramClient
    channel_storage: channel.Storage

    async def get_stats(self) -> list[channel.Channel]:
        """Метод получения списка каналов с данными

        :return: Список объектов каналов
        :rtype: list[Channel]
        """
        channel_list = []
        async with self.tg_client.client:
            dialogs = await self.tg_client.client.get_dialogs()
            for dialog in dialogs:
                if dialog.chat.type == "channel" and dialog.chat.title == "Gmusic": # noqa
                    invite_link = await self.get_chat_info(dialog.chat.id)
                    try:
                        try:
                            print(dialog.chat.title + f" {dialog.chat.id}")
                            photo_id = dialog.chat.photo.small_file_id
                            file_name = f"{channel_img_folder + photo_id}.png"
                            await self.tg_client.client.download_media(message=photo_id, # noqa
                                                                       file_name=file_name) # noqa
                            self.logger.info(f"Аватар канала {dialog.chat.title} загружен. Файл: {file_name}") # noqa

                        except AttributeError:
                            file_name = ""

                        if dialog.chat.username is None:
                            self.logger.info(f"Канал: {dialog.chat.title}")
                        else:
                            self.logger.info(f"Канал: {dialog.chat.username}")


                        messages = await self.get_channel_messages(dialog.chat.id, DAYS) # noqa

                        views = self.count_channel_views(messages)

                        avg_views = self.count_avg_views(views)

                        er = self.count_er(avg_views,
                                           dialog.chat.members_count)

                        res_dict = self.stats_to_channel(dialog,
                                                         invite_link,
                                                         avg_views,
                                                         views,
                                                         er,
                                                         file_name)
                        channel_list.append(transponse_channel(res_dict))
                    except ChannelPrivate:
                        self.logger.info(f"Канал {dialog.chat.title} не публичный") # noqa
        channel_list = self.count_cpm(channel_list)
        return channel_list

    async def get_chat_info(self, dialog_id: int):
        _chat = await self.tg_client.client.get_chat(dialog_id)
        try:
            if _chat.invite_link is None:
                return _chat.username
            return _chat.invite_link
        except Exception as e:
            print(e)

    async def update_db_data(self):
        """Метод вставки данных по каналам в БД"""
        channel_list = await self.get_stats()
        for _channel in channel_list:
            self.channel_storage.update_data_from_fetcher(_channel)
        self.logger.info("Работа фетчера окончена. Инициализация через 30 минут") # noqa

    async def get_channel_messages(self,
                                   channel_id: int,
                                   days: int) -> list[Message]:
        """Метод получения сообщений из канала

        :param channel_id: ID чата
        :type channel_id: int
        :param days: Период в днях с которого нужно получить сообщения
        :type days: int
        :return: Список сообщений из канала
        :rtype: list[Message]
        """
        messages_list = []
        offset = 0

        messages = await self.tg_client.client.get_history(channel_id)

        self.logger.info("Получены 100 сообщений")
        messages_list = messages

        while (messages != []) and (datetime.datetime.fromtimestamp(messages[-1].date, tz) >= datetime.datetime.now(tz) - datetime.timedelta(days=days)): # noqa
            offset += 100
            messages = await self.tg_client.client.get_history(channel_id,
                                                               offset=offset)
            self.logger.info("Получены дополнительные 100 сообщений")
            messages_list.extend(messages)

        return messages_list

    def count_channel_views(self, messages: list[Message]) -> list[int, int]: # noqa
        """Метод подсчёта общего числа просмотров канала

        :param messages: Список полученных сообщений за период
        :type messages: list[Message]
        :return: Список просмотров и кол-во сообщений за период
        :rtype: list[int, int]
        """
        views_list = []
        message_count = 0
        cur_date = datetime.datetime.now(tz)
        delta_date = cur_date - datetime.timedelta(days=DAYS)
        for message in messages:
            message_stamp = datetime.datetime.fromtimestamp(message.date, tz)
            # if (message.views is not None) and (datetime.datetime.fromtimestamp(message.date, tz) >= datetime.datetime.now(tz) - datetime.timedelta(days=DAYS)): # noqa
            if (message.views is not None) and (message_stamp >= delta_date):
                views_list.append(message.views)
                message_count += 1
        views = [sum(views_list), message_count]
        return views

    def count_avg_views(self, views: list[int, int]) -> int:
        """Метод подсчёта среднего охвата

        :param views: Список просмотров и кол-ва сообщений за период
        :type views: list[int, int]
        :return: Значение среднего охвата
        :rtype: int
        """
        try:
            avg_views = views[0] / views[1]
            return avg_views
        except ZeroDivisionError:
            # TODO забор прошлых данных
            return 0

    def count_er(self, avg_views: int, participants: int) -> int:
        """Метод подсчёта показателя вовлечённости (ER)

        :param avg_views: Средний охват
        :type avg_views: int
        :param participants: Число участников
        :type participants: int
        :return: Показатель ER
        :rtype: int
        """
        try:
            er = avg_views / participants
            return er * 100
        except ZeroDivisionError:
            self.logger.info("Новые сообщения не обнаружены")
            # TODO забор прошлых данных
            er = 0
            return er

    def count_cpm(self, channel_list: list) -> list:
        """Метод подсчёта cpm по каналу

        :param channel_list: Список каналов по которым собрана статистика
        :type channel_list: list
        :return: Список с обновлёным полем cpm
        :rtype: list
        """
        for current_channel in channel_list:
            _channel = self.channel_storage.get_channel_by_teleg_id(current_channel.tg_id) # noqa
            print(current_channel, _channel)
            if _channel == []:
                pass
            else:
                try:
                    current_channel.cpm = (_channel.post_price / current_channel.avg_coverage) * 1000 # noqa
                except ZeroDivisionError:
                    current_channel.cpm = 0
        return channel_list

    def stats_to_channel(self, dialog: Dialog,
                         invite_link: str,
                         avg_views: int,
                         views_list: list[int, int],
                         er: int,
                         photo_path: str) -> dict:
        """Метод конвертации данных в объект

        :param dialog:
            Объект диалога
            :type dialog: Dialog
        :param avg_views:
            Средний охват
            :type avg_views: int
        :param views_list:
            Список просмотров и число сообщений
            :type views_list: list[int, int]
        :param er:
            Показатель вовлечённости
            :type er: int
        :return: Словарь с данными о канале
        :rtype: dict
        """
        data = {"channel_name": dialog.chat.title,
                "mem_count": dialog.chat.members_count,
                "count": views_list[0],
                "avg_views": round(avg_views),
                "er": round(er, 1),
                "channel_id": dialog.chat.id,
                "tg_link": invite_link,
                "tg_id": str(dialog.chat.id),
                "photo_path": photo_path
                }
        return data

    def fetch(self):
        """Точка инициализации фетчера"""
        self.logger.info("Началась работа фетчера")
        self.tg_client.client.run(self.update_db_data())


def transponse_channel(data: dict):
    """Функция преобразовния словаря в объект

    :param data:
        Словарь с данными
        :type data: dict
    :return: Объект канала
    :rtype: Channel
    """
    return channel.Channel(
        id=0,
        username=0,
        name=data["channel_name"],
        tg_link=data["tg_link"],
        tg_id=data["tg_id"],
        category="",
        sub_count=data["mem_count"],
        avg_coverage=data["avg_views"],
        er=data["er"],
        cpm=0,
        post_price=0,
        photo_path=data['photo_path']
    )
