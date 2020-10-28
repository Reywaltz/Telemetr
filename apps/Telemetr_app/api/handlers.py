from dataclasses import dataclass
from io import BytesIO
from tempfile import NamedTemporaryFile

import openpyxl
from flask import Flask, jsonify, request, send_file
from internal.categories import category
from internal.channels import channel
from internal.postgres.channel import default_limit, default_offset
from internal.telegram.client import TelegramClient
from internal.users import user
from pkg.log import logger


@dataclass
class Handler:
    logger: logger.Logger
    app: Flask
    client: TelegramClient
    user_storage: user.Storage
    channel_storage: channel.Storage
    category_storage: category.Storage

    def create_routes(self):
        """Метод инициализации рутов"""
        self.app.add_url_rule("/api/v1/channel/<int:id>",
                              "get_channel",
                              self.get_channel,
                              )

        self.app.add_url_rule("/api/v1/channel/<int:id>",
                              "update_channel",
                              self.update_channel,
                              methods=["PUT"])

        self.app.add_url_rule("/api/v1/channel",
                              "get_all_channels",
                              self.get_all_channels)

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
                              self.get_users)

        self.app.add_url_rule("/api/v1/user/<id>",
                              "get_user_by_id",
                              self.get_user_by_id)

        self.app.add_url_rule("/api/v1/doc",
                              "send_channels_data",
                              self.send_channels_data,
                              methods=["POST"])

    def delete_channel(self, id: int):
        _channel = self.channel_storage.get_channel_by_id(id)

        if _channel is None:
            return {"error": "not found"}, 400

        if self.channel_storage.delete(id):
            self.logger.info(f"Удалён канал под ID {id}")
            self.client.leave_channel(_channel.tg_link)
            return {"success": "channel deleted"}, 200
        else:
            return {"error": "channel was not deleted"}, 500

    def add_channel(self):
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
                    return {"error": "No channel"}
                db_res = self.channel_storage.get_all(tg_link=res["username"])

                if db_res != []:
                    return {"error": "channel already exists in db"}

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
                        return {"success": "channel added"}
                    else:
                        self.client.leave_channel(channel_login)
                        return {"error": "inserttion error"}, 400

            except KeyError:
                return {"error": "wrong json format"}, 404

    def update_channel(self, id: int):
        """Метод обновления данных о канале

        :param id: ID канала
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
                return {"error": "wrong json format"}, 404

    def send_channels_data(self):
        """Метод отправки EXEL файла пользователю

        :return: Ответ с готовым файлом
        :rtype: Response
        """
        data = request.get_json()
        if data is None or data == [] or type(data) is dict:
            return {"error": "wrong json format"}, 404

        id_data = []

        try:
            for i in data:
                id_data.append(i["id"])
            id_data = tuple(id_data)

        except KeyError:
            return {"error": "wrong json format"}, 404

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

    def get_all_channels(self):
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: JSON
        """
        url_params = request.args
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

    def get_channel(self, id: int):
        """Метод GET для информации о канале

        :param id: ID канала в базе
        :type id: int
        :return: Информация о канале
        :rtype: JSON
        """
        res = self.channel_storage.get_channel_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

    def get_categories(self):
        """Метод GET для информации о категориях

        :return: Список категорий в БД
        :rtype: JSON
        """
        category_res = []
        res = self.category_storage.get_all()
        for item in res:
            category_res.append(item.to_json())

        return jsonify(category_res), 200

    def get_user_by_id(self, id):
        """Метод GET для информации о пользователе

        :param id: ID пользователя в базе
        :type id: int
        :return: Информация о пользователе
        :rtype: JSON
        """
        res = self.user_storage.get_user_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

    def get_users(self):
        """Метод GET для списка пользователей

        :return: Список пользователей
        :rtype: JSON
        """
        user_res = []
        res = self.user_storage.get_all()
        for item in res:
            user_res.append(item.to_json())

        return jsonify(user_res), 200

    def add_category(self):
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
                return {"error": "category already exists"}, 404
        except KeyError:
            return {"error": "wrong json format"}, 404


def new_handler(logger: logger.Logger, app: Flask, client: TelegramClient,
                user_storage: user.Storage,
                channel_storage: channel.Storage,
                category_storage: category.Storage) -> Handler:
    """Метод создания хэндлера

    :param logger: Логгер проекта
    :type logger: logger.Logger
    :param app: Приложение Flask
    :type app: Flask
    :param Client: Телеграм клиент
    :type app: TelegramClient
    :param user_storage: Хранилище пользователей
    :type user_storage: user.Storage
    :param channel_storage: Хранилище каналов
    :type channel_storage: channel.Storage
    :param category_storage: Хранилище категорий
    :type category_storage: category.Storage
    :rtype: Handler
    """
    return Handler(
        logger=logger,
        app=app,
        client=client,
        user_storage=user_storage,
        channel_storage=channel_storage,
        category_storage=category_storage
    )
