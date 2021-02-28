import time

import toml
from pyrogram import Client

from app import db_logger
from apps.fetcher import fetcher
from internal.postgres import channel, postgres
from internal.telegram.client import TelegramClient
from pkg.log import filelogger

cfg = toml.load("cfg.toml")
app_name = cfg.get("client").get("app_name")
api_id = cfg.get("client").get("api_id")
api_hash = cfg.get("client").get("api_hash")


def configDB(cfg):
    cfgDB = postgres.Config(
        database=cfg.get("databases").get("database"),
        user=cfg.get("databases").get("user"),
        password=cfg.get("databases").get("password"),
        host=cfg.get("databases").get("host"),
        port=cfg.get("databases").get("port")
    )
    return cfgDB


logger = filelogger.new_logger("fetcher")

cfgDB = configDB(cfg)

_client = Client(app_name, api_id, api_hash)

client = TelegramClient(_client)

db = postgres.new(cfg=cfgDB, logger=logger)
channel_storage = channel.new_storage(db=db, logger=db_logger)

fetcher = fetcher.Fetcher(logger, client, channel_storage)

if __name__ == "__main__":
    while True:
        fetcher.fetch()
        time.sleep(60 * 30)
