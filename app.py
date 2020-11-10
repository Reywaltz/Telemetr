import toml
from flask import Flask
from flask_cors import CORS
from pyrogram import Client

from apps.auth_bot import bot
from apps.telemetr.api import handlers
from internal.postgres import category, channel, postgres, user
from internal.telegram.client import TelegramClient
from pkg.log import filelogger

cfg = toml.load("cfg.toml")
app_name = cfg.get("client").get("app_name")
api_id = cfg.get("client").get("api_id")
api_hash = cfg.get("client").get("api_hash")
bot_token = cfg.get("auth_bot").get("token")


_client = Client(app_name, api_id, api_hash)

client = TelegramClient(_client)


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

app = Flask(__name__,
            instance_relative_config=cfg.get("secret_key").get("secret_key"))


CORS(app)

cfgDB = configDB(cfg)

db = postgres.new(cfg=cfgDB, logger=logger)
user_storage = user.new_storage(db)
channel_storage = channel.new_storage(db)
category_storage = category.new_storage(db)

auth_bot = bot.new(logger, bot_token, user_storage)
auth_bot.create_hanlders()

handlers = handlers.new_handler(logger, app,
                                client,
                                user_storage,
                                channel_storage,
                                category_storage,
                                auth_bot)

handlers.create_routes()

if __name__ == "__main__":
    auth_bot.bot.delete_webhook()
    auth_bot.bot.set_webhook(f'https://gavnishe.tk/api/v1/{bot_token}')
    app.run(debug=cfg.get("run").get("debug"),
            port=cfg.get("run").get("port"))
