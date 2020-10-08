import pytz
import datetime
from dataclasses import dataclass
from typing import List, Union

from internal.channels import channel
from pkg.log import logger
from pyrogram import Client
from pyrogram.types import Message, Dialog

timezone = pytz.timezone("Europe/Moscow")

DAYS = 7


@dataclass
class Fetcher:
    """Класс парсер данных из каналов"""
    logger: logger.Logger
    client: Client
    channel_storage: channel.Storage

    async def get_stats(self) -> List[channel.Channel]:
        """Метод получения списка каналов с данными

        :return: Список объектов каналов
        :rtype: List[Channel]
        """
        channel_list = []
        async with self.client:
            for dialog in await self.client.get_dialogs():
                if dialog.chat.type == "channel" and dialog.chat.username is not None: # noqa
                    try:
                        dialog.chat.username
                        messages = await self.get_channel_messages(dialog.chat.id, DAYS) # noqa

                        views = self.count_channel_views(messages)

                        avg_views = self.count_avg_views(views)

                        er = self.count_er(avg_views,
                                           dialog.chat.members_count)

                        res_dict = self.stats_to_channel(dialog,
                                                         avg_views,
                                                         views,
                                                         er)
                        channel_list.append(transponse_channel(res_dict))
                    except AttributeError:
                        self.logger.info(f"Канал {dialog.chat.title} не публичный") # noqa
        return channel_list

    async def update_db_data(self):
        """Метод вставки данных по каналам в БД"""
        channel_list = await self.get_stats()
        for _channel in channel_list:
            self.channel_storage.update_data_from_fetcher(_channel)

    async def get_channel_messages(self,
                                   channel_id: int,
                                   days: int) -> List[Message]:
        """Метод получения сообщений из канала

        :param channel_id: ID чата
        :type channel_id: int
        :param days: Период в днях с которого нужно получить сообщения
        :type days: int
        :return: Список сообщений из канала
        :rtype: List[Message]
        """
        messages_list = []
        offset = 0

        messages = await self.client.get_history(channel_id)

        self.logger.info("Получены 100 сообщений")
        messages_list = messages

        while datetime.datetime.fromtimestamp(messages[-1].date, timezone) >= datetime.datetime.now(timezone) - datetime.timedelta(days=days): # noqa
            offset += 100
            messages = await self.client.get_history(channel_id, offset=offset)
            self.logger.info("Получены дополнительные 100 сообщений")
            messages_list.extend(messages)

        return messages_list

    def count_channel_views(self, messages: List[Message]) -> List[Union[int, int]]: # noqa
        """Метод подсчёта общего числа просмотров канала

        :param messages: Список полученных сообщений за период
        :type messages: List[Message]
        :return: Список просмотров и кол-во сообщений за период
        :rtype: List[int, int]
        """
        views_list = []
        message_count = 0
        for message in messages:
            if (message.views is not None) and (datetime.datetime.fromtimestamp(message.date) >= datetime.datetime.utcnow() - datetime.timedelta(days=DAYS)): # noqa
                views_list.append(message.views)
                message_count += 1
        views = [sum(views_list), message_count]
        return views

    def count_avg_views(self, views: List[Union[int, int]]) -> int:
        """Метод подсчёта среднего охвата

        :param views: Список просмотров и кол-ва сообщений за период
        :type views: List[int, int]
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

    def stats_to_channel(self, dialog: Dialog,
                         avg_views: int,
                         views_list: List[Union[int, int]],
                         er: int) -> dict:
        """Метод конвертации данных в объект

        :param dialog: Объект диалога
        :type dialog: Dialog
        :param avg_views: Средний охват
        :type avg_views: int
        :param views_list: Список просмотров и число сообщений
        :type views_list: List[Union[int, int]]
        :param er: Показатель вовлечённости
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
                "tg_link": dialog.chat.username
                }
        return data

    def fetch(self):
        """Точка инициализации фетчера"""
        self.client.run(self.update_db_data())


def transponse_channel(data: dict):
    """Функция преобразовния словаря в объект

    :param data: Словарь с данными
    :type data: dict
    :return: Объект канала
    :rtype: Channel
    """
    return channel.Channel(
        id=0,
        username=0,
        name=data["channel_name"],
        tg_link=data["tg_link"],
        category="",
        sub_count=data["mem_count"],
        avg_coverage=data["avg_views"],
        er=data["er"],
        cpm=0,
        post_price=0
    )
