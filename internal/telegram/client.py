from dataclasses import dataclass
from pyrogram import Client
from pyrogram.errors import BadRequest


@dataclass
class TelegramClient:
    client: Client

    def join_to_channel(self, channel_login: str):
        """Метод подписки телеграм клиента на канал.
        При первом запуске необходимо войти в учётную запись Telegram

        :param channel_login: Юзернейм канала
        :type channel_login: str
        """
        try:
            with self.client:
                result = self.client.join_chat(channel_login)
            if result is not None and result.type == "channel":
                return result
            else:
                return None
        except BadRequest:
            return None

    def leave_channel(self, channel_login: str):
        with self.client:
            self.client.leave_chat(channel_login, delete=True)
