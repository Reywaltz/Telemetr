import toml
from pyrogram import Client
import datetime
import pytz
import pprint
from pkg.log import logger
from dataclasses import dataclass

# from Telemetr_app.internal.channels import channel
# from Telemetr_app.internal.channels import channel
from Telemetr_app.internal.channels import channel

timezone = pytz.timezone("Europe/Moscow")
cfg = toml.load('cfg.toml')
now = datetime.datetime.now()
api_id = cfg.get("client").get("api_id")
api_hash = cfg.get("client").get("api_hash")


@dataclass
class Fetcher:
    logger: logger.Logger
    channel_storage: channel.Storage


client = Client('Telemetr', api_id, api_hash)


async def get_stats():
    data = []
    async with client:
        for dialog in await client.get_dialogs():
            if dialog.chat.type == "channel":
                print(f"Processing {dialog.chat.title}")
                messages = await get_channel_messages(dialog.chat.id)
                views = count_channel_views(messages)
                count_er(views, dialog.chat.members_count)
                res = stats_to_json(data, dialog, views)
    pprint.pprint(res)


async def get_channel_messages(channel_id):
    lst = []
    offset = 0
    messages = await client.get_history(channel_id)
    lst = messages
    while datetime.datetime.fromtimestamp(messages[-1].date, timezone) >= datetime.datetime.now(timezone) - datetime.timedelta(days=7):
        offset += 100
        messages = await client.get_history(channel_id, offset=offset)
        lst.extend(messages)
    return lst


def count_channel_views(messages):
    views_list = []
    for message in messages:
        if (message.views is not None) and (datetime.datetime.fromtimestamp(message.date) >= datetime.datetime.utcnow() - datetime.timedelta(days=7)):
            views_list.append(message.views)
    views = [sum(views_list), len(views_list)]
    return views


def count_er(views, participants):
    try:
        avg_views = views[0] / views[1]
        er = avg_views / participants
        return er
    except ZeroDivisionError:
        er = 0
        return er


def stats_to_json(data, dialog, views_list):
    data.append({"name": dialog.chat.title,
                 "mem_count": dialog.chat.members_count,
                 "count": views_list[0],
                 "er": views_list[1]
                 })
    return data


client.run(get_stats())
