import re
import toml

from dataclasses import dataclass
from datetime import datetime, timedelta

from internal.users import user
from pkg.log import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import CommandHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update
from zoneinfo import ZoneInfo

cfg = toml.load("cfg.toml")
tz_info = cfg.get("timezone").get("tz_info")

tz = ZoneInfo(tz_info)
url = "https://gavnishe.tk/api/v1/channel"


@dataclass
class Auth_bot:
    logger: logger.Logger
    bot: Bot
    dispatcher: Dispatcher
    user_storage: user.Storage

    def start(self, update: Update, context: CallbackContext):
        """Хэндлер для обработки сообщения при получения ботом команды /start

        :param update:
            Входящее обновления с серверов telegram
            :type update: telegram.update.Update
        :param context:
            Контекст обновления бота
            :type context: telegram.ext.callbackcontext.CallbackContext
        """
        print(context.args)
        user_firstname = update.message.chat.first_name
        keyboard = [
                [
                    InlineKeyboardButton("На сайт",
                                         url=url),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard, resize_keyboard=True)
        if context.args == []:
            context.bot.send_message(update.effective_chat.id,
                                     text="Здравствуйте. Для начала авторизации \
                                          начните на кнопку входа на сайте",
                                     reply_markup=reply_markup)
        else:
            site_code = context.args[0]
            try:
                username = update.message.chat.username
            except KeyError:
                username = ''

            """Проверка на валидность ключа по формату MD5"""
            if re.findall(r"([a-fA-F\d]{32})", site_code) == []:
                context.bot.send_message(update.effective_chat.id,
                                         text=user_firstname + ", Повторите попытку входа через сайт.", # noqa
                                         reply_markup=reply_markup)
                self.logger.info(f"Код {context.args[0]} не прошёл валидацию по регулярному выражению") # noqa 
            else:
                created_at = datetime.now(tz)
                # print(created_at)
                tel_user = user.User(id=0,
                                     username=username,
                                     telegram_id=update.message.chat.id,
                                     auth_code=site_code,
                                     created_at=created_at,
                                     valid_to=created_at + timedelta(hours=1))

                if not self.user_storage.create(tel_user):
                    self.user_storage.update_auth_key(tel_user)
                    self.logger.info(f"Обновлён ключ пользователя под id {tel_user.telegram_id}") # noqa

                context.bot.send_message(update.effective_chat.id,
                                         text="Здравствуйте, " + user_firstname + # noqa
                                              ". Возвращайтесь на сайт",
                                         reply_markup=reply_markup)

    def create_hanlders(self):
        """Метод инициализации хэндлеров бота"""

        start_handler = CommandHandler("start", self.start)
        self.dispatcher.add_handler(start_handler)


def new(logger: logger.Logger,
        bot_token: str,
        user_storage: user.Storage) -> Auth_bot:
    """Метод создания класса бота авторизации

    :param logger:
        Логгер проекта
        :type logger: logging.Logger
    :param bot_token:
        Токен бота
        :type bot_token: str
    :param user_storage:
        Хранилище БД пользователей
        :type user_storage: user.Storage
    :return: Объект класса
    :rtype: Auth_bot
    """
    bot = Bot(bot_token)
    return Auth_bot(logger=logger,
                    bot=bot,
                    dispatcher=Dispatcher(bot, None, 1),
                    user_storage=user_storage)
