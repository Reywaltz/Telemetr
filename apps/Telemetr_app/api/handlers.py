from dataclasses import dataclass

from flask import Flask, jsonify, request
from internal.categories import category
from internal.channels import channel
from internal.users import user
from pkg.log import logger


@dataclass
class Handler:
    logger: logger.Logger
    app: Flask
    user_storage: user.Storage
    channel_storage: channel.Storage
    category_storage: category.Storage

    def create_routes(self):
        """Метод инициализации рутов"""
        self.app.add_url_rule("/api/v1/channel/<id>",
                              "get_channel",
                              self.get_channel)

        self.app.add_url_rule("/api/v1/channel",
                              "get_all_channels",
                              self.get_all_channels)

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

    def get_all_channels(self):
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: JSON
        """
        url_params = request.args
        res = self.channel_storage.get_all(
            url_params.get("min_subcribers", 0, type=int),
            url_params.get("max_subcribers", 9999999999, type=int),
            url_params.get("min_views", 0, type=int),
            url_params.get("max_views", 9999999999, type=int),
            url_params.get("min_er", 0, type=int),
            url_params.get("max_er", 9999999999, type=int),
            url_params.get("min_cost", 0, type=int),
            url_params.get("max_cost", 9999999999, type=int),
            url_params.get("tg_link", "%%", type=str) + "%",
            url_params.get("tg_name", "%%", type=str) + "%"
        )
        channel_res = []
        for item in res:
            channel_res.append(item.to_json())
        return jsonify(channel_res), 200

    def get_channel(self, id):
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
                return {"success": "new category added"}, 200
            else:
                return {"error": "category already exists"}, 404
        except KeyError:
            return {"error": "wrong json format"}, 404


def new_handler(logger: logger.Logger, app: Flask,
                user_storage: user.Storage,
                channel_storage: channel.Storage,
                category_storage: category.Storage) -> Handler:
    """Метод создания хэндлера

    :param logger: Логгер проекта
    :type logger: logger.Logger
    :param app: Приложение Flask
    :type app: Flask
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
        user_storage=user_storage,
        channel_storage=channel_storage,
        category_storage=category_storage
    )