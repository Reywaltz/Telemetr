import re
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo

import openpyxl
from pyrogram.errors import UserNotParticipant
import toml
from apps.auth_bot.bot import Auth_bot
from apps.telemetr.api.additions import admin_auth_required, auth_required
from flask import Flask, Response, jsonify, request, send_file
from internal.admin import admin
from internal.categories import category
from internal.channels import channel
from internal.postgres.channel import default_limit, default_offset
from internal.telegram.client import TelegramClient
from internal.users import user
from pkg.log import logger
from pyrogram.errors import BadRequest
from telegram import Update

cfg = toml.load("cfg.toml")
bot_token = cfg.get("auth_bot").get("token")
tz_info = cfg.get("timezone").get("tz_info")

channel_invite_prefix = "https://t.me/"

tz = ZoneInfo(tz_info)


@dataclass
class Handler:
    logger: logger.Logger
    app: Flask
    client: TelegramClient
    user_storage: user.Storage
    channel_storage: channel.Storage
    category_storage: category.Storage
    admin_storage: admin.Storage
    auth_bot: Auth_bot

    def create_routes(self):

        """Метод инициализации рутов"""
        self.app.add_url_rule("/api/v1/channel/<int:id>",
                              "get_channel",
                              self.get_channel,
                              methods=["GET"])

        self.app.add_url_rule("/api/v1/channel",
                              "update_channel",
                              self.update_channel,
                              methods=["PUT"])

        self.app.add_url_rule("/api/v1/channel",
                              "get_all_channels",
                              self.get_all_channels,
                              methods=["GET"])

        self.app.add_url_rule("/api/v1/channel",
                              "add_new_channel",
                              self.add_channel,
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/channel",
                              "delete_channel",
                              self.delete_channel,
                              methods=["DELETE"])

        self.app.add_url_rule("/api/v1/category",
                              "get_categories",
                              self.get_categories)

        self.app.add_url_rule("/api/v1/category",
                              "add_category",
                              self.add_category,
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/user",
                              "users_get",
                              self.get_users,
                              methods=["GET"])

        self.app.add_url_rule("/api/v1/user/<id>",
                              "get_user_by_id",
                              self.get_user_by_id,
                              methods=["GET"])

        self.app.add_url_rule("/api/v1/doc",
                              "send_channels_data",
                              self.send_channels_data,
                              methods=["GET"])

        self.app.add_url_rule(f"/api/v1/{bot_token}",
                              "webhook",
                              self.webhook,
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/auth",
                              "auth",
                              self.auth_check,
                              methods=["POST"]),

        self.app.add_url_rule("/api/v1/me",
                              "user_channel",
                              self.get_user_channels)

        self.app.add_url_rule("/api/v1/admin",
                              "get_admin",
                              self.get_admin,
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/admin/<int:id>",
                              "delete_channel_admin",
                              self.admin_delete_channel,
                              methods=["DELETE"])

    def auth_check(self) -> Response:
        """Метод проверки пользователя на авторизацию с сайта

        :return: Информация о пользователя с проверяемым ключом
        :rtype: Response
        """
        data = request.get_json(force=True)
        if data is None:
            return {"error": "empty json"}, 400
        else:
            try:
                auth_code = data['auth_code']
            except KeyError:
                return {"error": "wrong JSON format"}, 400
            cur_user = self.user_storage.get_user_by_authcode(auth_code)
            if cur_user is None:
                return {"status": "no user"}, 400
            return cur_user.to_json(), 200

    def webhook(self) -> Response:
        """Метод получения обновлений с телеграм бота

        :return: Обновления с телеграм бота
        :rtype: Response
        """
        data = Update.de_json(request.get_json(force=True),
                              bot=self.auth_bot.bot)
        print(data)
        self.auth_bot.dispatcher.process_update(data)
        return '', 200

    @auth_required
    def delete_channel(self) -> Response:
        """Метод удаления канала

        :return: JSON ответ о статусе запроса
        :rtype: Response
        """
        req = request.get_json(force=True)
        id_list = req.get("id")
        if id_list is None or id_list == []:
            return {"error": "Bad request"}, 400

        for id in id_list:
            _channel = self.channel_storage.get_channel_by_id(id)
            if _channel is None:
                self.logger.info(f"Канал ID:{id} не существует")
                if len(id_list) == 1:
                    return {"error": "not exists"}, 400
                continue

            if self.channel_storage.delete(id):
                self.logger.info(f"Удалён канал под ID {id}")
                try:
                    self.client.leave_channel(int(_channel.tg_id))
                except UserNotParticipant:
                    self.logger.info(f"Канал {_channel.name} уже был покинут клиентом") # noqa
            else:
                self.logger.error(f"Канал под ID {id} не удалён")
                return {"error": "can't remove channel"}, 500

        return {"success": "deleted"}, 200

    @auth_required
    def add_channel(self) -> Response:
        """Метод добавления канала в БД

        :return: Статус операции
        :rtype: JSON ответ
        """
        data = request.get_json(force=True)
        if data is None:
            return {"error": "empty data"}, 400
        else:

            try:
                channel_login = str(data["channel_login"])
                channel_name = data.get("channel_name", None)
                category = str(data["category"])
                post_price = int(data["post_price"])
                user_id = int(data["user_id"])

                try:
                    res = self.client.join_to_channel(channel_login)

                    if (res is None) or (res.type != "channel"):
                        raise BadRequest

                    if channel_name is None:
                        channel_name = res.title

                    tg_id = str(res.id)
                    print(res)
                    db_res = self.channel_storage.get_channel_by_teleg_id(tg_id) # noqa

                    if db_res != []:
                        return {"error": "channel already exists in db"}, 400

                    if res is not None:
                        _channel = channel.Channel(id=0,
                                                   username=user_id,
                                                   name=channel_name,
                                                   tg_link=channel_login,
                                                   tg_id=tg_id,
                                                   category=category,
                                                   sub_count=0,
                                                   avg_coverage=0,
                                                   er=0,
                                                   cpm=0,
                                                   post_price=post_price,
                                                   photo_path=""
                                                   )
                        if self.channel_storage.insert(_channel):
                            self.logger.info(f"Добавлен канал. ID: {res['id']}, логин {res['username']}") # noqa
                            return {"success": "channel added"}, 200
                        else:
                            self.client.leave_channel(int(tg_id))
                            return {"error": "inserttion error. \
                                    Channel alreay exists"}, 400

                except BadRequest:
                    return {"error":
                            "wrong channel username or dialog type"}, 400

            except KeyError:
                print("format")
                return {"error": "wrong json format"}, 400

    @auth_required
    def update_channel(self) -> Response:
        """Метод обновления данных о канале

        :return: Статус операции
        :rtype: JSON
        """
        data = request.get_json()
        if (data is None) or (data == []):
            return {"error": "wrong json format"}, 400

        for item in data:
            try:
                channel_id = int(item.get("id", -1))
                new_price = int(item.get("post_price", -1))
            except ValueError:
                channel_id = -1
                new_price = -1

            if (channel_id == -1) or ((new_price < 0) or (new_price is None)):
                if len(data) == 1:
                    return {"error": "bad request"}, 400
                continue

            _channel = channel.Channel(id=channel_id,
                                       username='',
                                       name='',
                                       tg_link='',
                                       tg_id='',
                                       category='',
                                       sub_count=0,
                                       avg_coverage=0,
                                       er=0,
                                       cpm=0,
                                       post_price=new_price,
                                       photo_path='')

            if self.channel_storage.update_post_price(_channel):
                self.logger.info(f"Канал ID:{_channel.id} обновлён")
            else:
                self.logger.info(f"Канал ID:{_channel.id} не получилось обновить") # noqa
        return {"success": "updated"}, 200

    def send_channels_data(self) -> Response:
        """Метод отправки EXEL файла пользователю

        :return: Ответ с готовым файлом
        :rtype: Response
        """

        url_params = request.args

        id_query = url_params.get("id", None)
        if id_query is None:
            return {"error": "empty data"}, 400

        id_data_sorted_set = sorted(set(id_query.split(",")))

        id_data = tuple(id_data_sorted_set)

        channels = self.channel_storage.get_channels_to_doc(id_data)

        if channels is None:
            return {"error": "channels not found"}, 400

        workbook = openpyxl.Workbook()

        with NamedTemporaryFile() as tmp:

            sheet = workbook.active

            sheet['A1'] = "Название"
            sheet['B1'] = "Ссылка"
            sheet['C1'] = "Подписчики"
            sheet['D1'] = "Средний охват"
            sheet['E1'] = "ER %"
            sheet['F1'] = "Цена, руб."
            sheet['G1'] = "CPM, руб."

            for index, item in enumerate(channels):
                sheet.append((item.name,
                             item.tg_link,
                             item.sub_count,
                             item.avg_coverage,
                             item.er,
                             item.cpm,
                             item.post_price))

                link_check = re.findall("t.me/joinchat/", item.tg_link)

                if link_check == []: # noqa
                    new_hyperlink = channel_invite_prefix + item.tg_link
                    sheet[f"B{index+2}"].hyperlink = new_hyperlink
                else:
                    sheet[f"B{index+2}"].hyperlink = item.tg_link
                sheet[f"B{index+2}"].style = 'Hyperlink'

            workbook.save(tmp.name)

            output = BytesIO(tmp.read())
        self.logger.info(f"Запрос на скачивание файла с id: {id_data_sorted_set}") # noqa
        cur_date = datetime.now().strftime("%d.%m.%Y")
        return send_file(output,
                         attachment_filename=f'{cur_date}.xlsx',
                         as_attachment=True), 200

    def get_all_channels(self) -> Response:
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: Response
        """
        url_params = request.args
        channels, total = self.channel_storage.get_all(
            url_params.get("min_subcribers", 0, type=int),
            url_params.get("max_subcribers", 9999999999, type=int),
            url_params.get("min_views", 0, type=int),
            url_params.get("max_views", 9999999999, type=int),
            url_params.get("min_er", 0, type=int),
            url_params.get("max_er", 9999999999, type=int),
            url_params.get("min_cost", 0, type=int),
            url_params.get("max_cost", 9999999999, type=int),
            url_params.get("tg_link", "%%", type=str) + "%",
            url_params.get("tg_name", "%%", type=str) + "%",
            url_params.get("category", "%%", type=str) + "%",
            url_params.get("limit", default_limit, type=int),
            url_params.get("offset", default_offset, type=int)
        )

        channel_res = []
        for item in channels:
            channel_res.append(item.to_json())

        res = {"count": len(channels),
               "total": total,
               "limit": default_limit,
               "items": channel_res}
        return res, 200

    def get_channel(self, id: int) -> Response:
        """Метод GET для информации о канале

        :param id:
            ID канала в базе
            :type id: int
        :return: Информация о канале
        :rtype: JSON
        """
        res = self.channel_storage.get_channel_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

    def get_categories(self) -> Response:
        """Метод GET для информации о категориях

        :return: Список категорий в БД
        :rtype: JSON
        """
        category_res = []
        res = self.category_storage.get_all()
        for item in res:
            category_res.append(item.to_json())

        return jsonify(category_res), 200

    def get_user_by_id(self, id: int) -> Response:
        """Метод GET для информации о пользователе

        :param id:
            ID пользователя в базе
            :type id: int
        :return: Информация о пользователе
        :rtype: JSON
        """
        res = self.user_storage.get_user_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

    def get_users(self) -> Response:
        """Метод GET для списка пользователей

        :return: Список пользователей
        :rtype: JSON
        """
        user_res = []
        res = self.user_storage.get_all()
        for item in res:
            user_res.append(item.to_json())

        return jsonify(user_res), 200

    @auth_required
    def add_category(self) -> Response:
        """POST запрос на вставку категории

        :return: Результат запроса
        :rtype: JSON
        """
        data = request.get_json()
        if data is None:
            return {"error": "empty data"}, 404
        try:
            _category = category.Category(data['category'])
            if self.category_storage.insert(_category):
                self.logger.info(f"Добавлена категория {_category.name}")
                return {"success": "new category added"}, 201
            else:
                return {"error": "category already exists"}, 400
        except KeyError:
            return {"error": "wrong json format"}, 400

    def get_user_channels(self) -> Response:
        """[summary]

        :return: [description]
        :rtype: Response
        """
        args = request.args
        auth_code = request.headers.get('Authorization', None)

        user_id = args.get("id", None, int)
        required_user = self.user_storage.get_user_by_id(user_id)

        if user_id is None or (required_user is None):
            return {"error": "no user info"}, 400
        if (auth_code is None) or (auth_code != required_user.auth_code):
            return {"error": "unauthorized access to other data"}, 401

        channel_res = []
        res = self.channel_storage.get_user_channels(user_id)
        if (res is None) or (res is False):
            return {"status": "No channels"}, 400

        for item in res:
            channel_res.append(item.to_json())
        return jsonify(channel_res), 200

    def get_admin(self) -> Response:
        data = request.get_json(force=True)
        if data is None:
            return {"error": "empty data"}, 400
        try:
            username_json = data['username']
            password_json = data['password']
        except KeyError:
            return {"error": "wrong JSON format"}, 400

        db_user = self.admin_storage.get_admin(username_json)
        if db_user is None or db_user.password != password_json:
            return {"error": "wrong user data"}, 401

        curr_time = datetime.now(tz)
        if (db_user.valid_to is None) or (curr_time > db_user.valid_to):
            db_user.access_token = self.admin_storage.update_token(db_user)
        return {"access_token": db_user.access_token}, 201

    @admin_auth_required
    def admin_delete_channel(self,  id: int) -> Response:
        _channel = self.channel_storage.get_channel_by_id(id)

        if _channel is None:
            return {"error": "not found"}, 400

        if self.channel_storage.delete(id):
            self.logger.info(f"Удалён канал под ID {id}")
            self.client.leave_channel(_channel.tg_link)
            return {"success": "channel deleted"}, 200
        else:
            return {"error": "channel was not deleted"}, 500


def new_handler(logger: logger.Logger, app: Flask, client: TelegramClient,
                user_storage: user.Storage,
                channel_storage: channel.Storage,
                category_storage: category.Storage,
                admin_storage: admin.Storage,
                auth_bot: Auth_bot) -> Handler:
    """Метод создания хэндлера

    :param logger:
        Логгер проекта
        :type logger: logger.Logger
    :param app:
        Приложение Flask
        :type app: Flask
    :param Client:
        Телеграм клиент
        :type app: TelegramClient
    :param user_storage:
        Хранилище пользователей
        :type user_storage: user.Storage
    :param channel_storage:
         Хранилище каналов
        :type channel_storage: channel.Storage
    :param category_storage:
        Хранилище категорий
        :type category_storage: category.Storage
    :param auth_bot:
        Бот авторизации
        :type category_storage: Auth_bot
    :rtype: Handler
    """
    return Handler(
        logger=logger,
        app=app,
        client=client,
        user_storage=user_storage,
        channel_storage=channel_storage,
        category_storage=category_storage,
        admin_storage=admin_storage,
        auth_bot=auth_bot
    )
