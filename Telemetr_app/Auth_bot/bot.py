import toml
from telegram.ext import Updater
from telegram.ext import PrefixHandler

cfg = toml.load("config.toml")


def start(update, context):
    a = update.message.text
    print(a)
    context.bot.sendMessage(update.message.chat.id, "dsadas")


bot_token = cfg.get("bot").get("token")

updater = Updater(token=bot_token, use_context=True)

dp = updater.dispatcher

dp.add_handler(PrefixHandler('/', 'start', start))

updater.start_polling()
