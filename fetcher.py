import toml
from pyrogram import Client
from apps.Fetcher import fetcher
from internal.postgres import channel, postgres
from pkg.log import filelogger

cfg = toml.load("cfg.toml")
api_id = cfg.get("client").get("api_id")
api_hash = cfg.get("client").get("api_hash")


client = Client('Telemetr', api_id, api_hash)


def configDB(cfg):
    cfgDB = postgres.Config(
        database=cfg.get("databases").get("database"),
        user=cfg.get("databases").get("user"),
        password=cfg.get("databases").get("password"),
        host=cfg.get("databases").get("host"),
        port=cfg.get("databases").get("port")
    )
    return cfgDB


logger = filelogger.new_logger("file_log")

cfgDB = configDB(cfg)

db = postgres.new(cfg=cfgDB, logger=logger)
channel_storage = channel.new_storage(db)

fetcher = fetcher.Fetcher(logger, client, channel_storage)

if __name__ == "__main__":
    fetcher.fetch()
