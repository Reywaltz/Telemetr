import logging
from dataclasses import dataclass

import toml
from internal.users import user
from telegram.bot import Bot
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import Dispatcher

cfg = toml.load("cfg.toml")
bot_token = cfg.get("auth_bot").get("token")


@dataclass
class Auth_bot:
    logger: logging.Logger
    bot: Bot
    dispatcher: Dispatcher
    user_storage: user.Storage

    def start(self, update, context):
        print(context.args)
        if context.args == []:
            context.bot.send_message(update.effective_chat.id, text="Hello")
        else:
            tel_user = user.User(update.message.chat.id,
                                 update.message.chat.username)

            self.user_storage.create(tel_user)

            # photo = context.bot.get_user_profile_photos(update.message.chat.id)
            # file = context.bot.get_file(photo['photos'][0][-1]['file_id'])
            # file.download()
            context.bot.send_message(update.effective_chat.id, text="Nice one")

    def create_hanlders(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)


def new(logger: logging.Logger,
        bot_token: str,
        user_storage: user.Storage) -> Auth_bot:
    bot = Bot(bot_token)
    return Auth_bot(logger=logging.Logger,
                    bot=bot,
                    dispatcher=Dispatcher(bot, None, 1),
                    user_storage=user_storage)
