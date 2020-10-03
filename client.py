import datetime
import pprint
from dataclasses import dataclass
import pytz
import toml
from pyrogram import Client

# from pkg.log import logger
from Telemetr_app.internal.channels import channel

timezone = pytz.timezone("Europe/Moscow")
cfg = toml.load('cfg.toml')
api_id = cfg.get("client").get("api_id")
api_hash = cfg.get("client").get("api_hash")


client = Client('Telemetr', api_id, api_hash)


@dataclass
class Fetcher:
    # logger: logger.Logger
    client: Client
    channel_storage: channel.Storage

    async def get_stats(self):
        data = []
        async with client:
            for dialog in await client.get_dialogs():
                if dialog.chat.type == "channel":
                    print(f"Processing {dialog.chat.title}")
                    # self.logger.info(f"Обработка канала {dialog.chat.title}")

                    messages = await self.get_channel_messages(dialog.chat.id, 7)
                    views = self.count_channel_views(messages)

                    er = self.count_er(views, dialog.chat.members_count)
                    res = self.stats_to_json(data, dialog, views, er)

        pprint.pprint(res)

    async def get_channel_messages(self, channel_id, days):
        lst = []
        offset = 0
        messages = await client.get_history(channel_id)
        # self.logger.info("Получены 100 сообщений")
        lst = messages
        while datetime.datetime.fromtimestamp(messages[-1].date, timezone) >= datetime.datetime.now(timezone) - datetime.timedelta(days=days):
            offset += 100
            messages = await client.get_history(channel_id, offset=offset)
            # self.logger.info("Получены дополнительные 100 сообщений")
            lst.extend(messages)
        return lst

    def count_channel_views(self, messages):
        views_list = []
        message_count = 0
        for message in messages:
            if (message.views is not None) and (datetime.datetime.fromtimestamp(message.date) >= datetime.datetime.utcnow() - datetime.timedelta(days=7)):
                views_list.append(message.views)
                message_count += 1
        views = [sum(views_list), message_count]
        return views

    def count_er(self, views, participants):
        try:
            avg_views = views[0] / views[1]
            er = avg_views / participants
            return er * 100
        except ZeroDivisionError:
            # self.logger.info("Новых сообщения не обнаружены")
            er = 0
            return er

    def stats_to_json(self, data, dialog, views_list, er):
        data.append({"name": dialog.chat.title,
                     "mem_count": dialog.chat.members_count,
                     "count": views_list[0],
                     "er": round(er, 1)
                     })
        return data

    def fetch(self):
        self.client.run(self.get_stats())
