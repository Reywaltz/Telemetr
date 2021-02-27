from dataclasses import dataclass

from pyrogram import Client


@dataclass
class TelegramClient:
    client: Client

    def join_to_channel(self, channel_login: str):
        """Метод подписки телеграм клиента на канал.
        При первом запуске необходимо войти в учётную запись Telegram

        :param channel_login:
            Юзернейм канала
            :type channel_login: str
        """
        with self.client:
            result = self.client.join_chat(channel_login)
        if result is not None and result.type == "channel":
            return result
        else:
            return None

    def leave_channel(self, channel_login: str):
        """Метод отписки от канала

        :param channel_login:
            Логин канала
            :type channel_login: str
        """
        with self.client:
            self.client.leave_chat(str(channel_login), delete=True)

    def get_chat(self, channel_login: str):
        """Метод проверки существования чата в Telegram по ссылке

        :param channel_login:
            Приглашение в телеграм канал
            :type channel_login: str
        :return: Информация о диалоге
        :rtype: Chat | None
        """
        with self.client:
            res = self.client.get_chat(channel_login)
            return res
