from dataclasses import dataclass
from io import BytesIO
from tempfile import NamedTemporaryFile

import openpyxl
import toml
from apps.auth_bot.bot import Auth_bot
from apps.telemetr.api.additions import auth_required
from flask import Flask, Response, jsonify, request, send_file
from internal.categories import category
from internal.channels import channel
from internal.postgres.channel import default_limit, default_offset
from internal.telegram.client import TelegramClient
from internal.users import user
from pkg.log import logger
from telegram import Update


cfg = toml.load("cfg.toml")
bot_token = cfg.get("auth_bot").get("token")


@dataclass
class Handler:
    logger: logger.Logger
    app: Flask
    client: TelegramClient
    user_storage: user.Storage
    channel_storage: channel.Storage
    category_storage: category.Storage
    auth_bot: Auth_bot

    def create_routes(self):
        """Метод инициализации рутов"""
        self.app.add_url_rule("/api/v1/channel/<int:id>",
                              "get_channel",
                              self.get_channel,
                              methods=["GET"])

        self.app.add_url_rule("/api/v1/channel/<int:id>",
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

        self.app.add_url_rule("/api/v1/channel/<id>",
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
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/{bot_token}",
                              "webhook",
                              self.webhook,
                              methods=["POST"])

        self.app.add_url_rule("/api/v1/auth",
                              "auth",
                              self.auth_check,
                              methods=["POST"])

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
    def delete_channel(self, id: int) -> Response:
        """Метод удаления канала

        :param id:
             ID канала в базе
            :type id: int
        :return: JSON ответ о статусе запроса
        :rtype: Response
        """
        _channel = self.channel_storage.get_channel_by_id(id)

        if _channel is None:
            return {"error": "not found"}, 400

        if self.channel_storage.delete(id):
            self.logger.info(f"Удалён канал под ID {id}")
            self.client.leave_channel(_channel.tg_link)
            return {"success": "channel deleted"}, 200
        else:
            return {"error": "channel was not deleted"}, 500

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
                channel_name = str(data["channel_name"])
                category = str(data["category"])
                post_price = int(data["post_price"])
                user_id = int(data["user_id"])

                res = self.client.join_to_channel(channel_login)

                if res is None:
                    return {"error": "No channel"}, 400
                db_res = self.channel_storage.get_all(tg_link=res["username"])

                if db_res != []:
                    return {"error": "channel already exists in db"}, 400

                if res is not None:
                    _channel = channel.Channel(id=0,
                                               username=user_id,
                                               name=channel_name,
                                               tg_link=channel_login,
                                               category=category,
                                               sub_count=0,
                                               avg_coverage=0,
                                               er=0,
                                               cpm=0,
                                               post_price=post_price
                                               )
                    if self.channel_storage.insert(_channel):
                        self.logger.info(f"Добавлен канал. ID: {res['id']}, логин {res['username']}") # noqa
                        return {"success": "channel added"}, 200
                    else:
                        self.client.leave_channel(channel_login)
                        return {"error": "inserttion error"}, 400

            except KeyError:
                return {"error": "wrong json format"}, 400

    @auth_required
    def update_channel(self, id: int) -> Response:
        """Метод обновления данных о канале

        :param id:
            ID канала
            :type id: int
        :return: Статус операции
        :rtype: JSON
        """
        data = request.get_json()
        if data is None:
            return {"error": "empty data"}, 400
        else:
            try:
                _channel = channel.Channel(id=id,
                                           username="",
                                           name="",
                                           tg_link="",
                                           category="",
                                           sub_count="",
                                           avg_coverage=0,
                                           er=0,
                                           cpm=0,
                                           post_price=data["post_price"])
                if self.channel_storage.update_post_price(_channel):
                    self.logger.info(f"Обновлен канал ID: {_channel.id}")
                    return {"success": "post_price updated"}, 201
                else:
                    return {"error": "channel doesn't exist"}, 404
            except KeyError:
                return {"error": "wrong json format"}, 400

    def send_channels_data(self) -> Response:
        """Метод отправки EXEL файла пользователю

        :return: Ответ с готовым файлом
        :rtype: Response
        """
        data = request.get_json()
        if data is None or data == [] or type(data) is dict:
            return {"error": "wrong json format"}, 400

        id_data = []

        try:
            for i in data:
                id_data.append(i["id"])
            id_data = tuple(id_data)

        except KeyError:
            return {"error": "wrong json format"}, 400

        channels = self.channel_storage.get_channels_to_doc(id_data)

        if channels is None:
            return {"error": "channels not selected"}, 400

        workbook = openpyxl.Workbook()

        with NamedTemporaryFile() as tmp:

            sheet = workbook.active

            sheet['A1'] = "ID"
            sheet['B1'] = "Name"
            sheet['C1'] = "Tg_link"
            sheet['D1'] = "Category"
            sheet['E1'] = "Sub_count"
            sheet['F1'] = "Avg_coverage"
            sheet['G1'] = "ER"
            sheet['H1'] = "CPM"
            sheet['I1'] = "Post_price"

            for item in channels:
                sheet.append((item.id,
                             item.name,
                             item.tg_link,
                             item.category,
                             item.sub_count,
                             item.avg_coverage,
                             item.er,
                             item.cpm,
                             item.post_price))
            workbook.save(tmp.name)
            output = BytesIO(tmp.read())

        return send_file(output,
                         attachment_filename='data.xlsx',
                         as_attachment=True), 200

    def get_all_channels(self) -> Response:
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: Response
        """
        url_params = request.args
        print(url_params)
        channels = self.channel_storage.get_all(
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
            url_params.get("limit", default_limit, type=int),
            url_params.get("offset", default_offset, type=int)
        )

        channel_res = []
        for item in channels:
            channel_res.append(item.to_json())
        res = {"count": len(channels),
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


def new_handler(logger: logger.Logger, app: Flask, client: TelegramClient,
                user_storage: user.Storage,
                channel_storage: channel.Storage,
                category_storage: category.Storage,
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
        auth_bot=auth_bot
    )
