from dataclasses import dataclass


from flask_restful import Api
from flask import Flask
# from Telemetr_app.api.resources.channel import get
from Telemetr_app.api.resources import category as categoryapi
from Telemetr_app.api.resources import channel as channelapi
from Telemetr_app.api.resources import user as userapi
from Telemetr_app.api.resources.category import CategoryListResource
from Telemetr_app.api.resources.channel import ChannelResource, ChannelListResource 
from Telemetr_app.api.resources.user import UserResource, UserListResource
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

    # TODO Доделать логику адрессации
    def create_routes(self):
        """Метод инициализации рутов"""
        self.app.add_url_rule("/api/v1/channel/<id>", "get", ChannelResource.get)
        self.app.add_url_rule("/api/v1/channel/", "get_all_channels", ChannelListResource.get)

        self.app.add_url_rule("/api/v1/category/", "cat_get", CategoryListResource.get)

        self.app.add_url_rule("/api/v1/user/", "users_get", UserListResource.get)
        self.app.add_url_rule("/api/v1/user/<id>", "user_get", UserResource.get)
        
        # self.api.add_resource(userapi.UserResource, "/api/v1/user/<int:id>",
        #                       resource_class_args=(self.logger, self.user_storage, ))

        # self.api.add_resource(userapi.UserListResource, "/api/v1/user",
        #                       resource_class_args=(self.logger, self.user_storage, ))                 

        # self.api.add_resource(channelapi.ChannelResource, "/api/v1/channel/<int:id>",
        #                       resource_class_args=(self.logger, self.channel_storage, ))

        # self.api.add_resource(channelapi.ChannelListResource, "/api/v1/channel",
        #                       resource_class_args=(self.logger, self.channel_storage, ))

        # self.api.add_resource(categoryapi.CategoryListResource, "/api/v1/category",
        #                       resource_class_args=(self.logger, self.category_storage, ))

    def get(self, id):
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: JSON
        """
        channel_res = []
        res = self.channel_storage.get_all()
        for item in res:
            channel_res.append(item.to_json())

        return dict(channel_res), 200


def new_handler(logger: logger.Logger, app: Flask, user_storage: user.Storage,
                channel_storage: channel.Storage, category_storage: category.Storage) -> Handler:
    """Метод создания хэндлера

    :param logger: Логгер проекта
    :type logger: logger.Logger
    :param api: Обёртка на приложение flask-a через flask-restful
    :type api: flask_restful.Api
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
