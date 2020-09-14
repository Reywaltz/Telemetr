from dataclasses import dataclass

from flask_restful import Api

from Telemetr_app.api.resources import category as categoryapi
from Telemetr_app.api.resources import channel as channelapi
from Telemetr_app.api.resources import user as userapi
from Telemetr_app.internal.categories import category
from Telemetr_app.internal.channels import channel
from Telemetr_app.internal.users import user
from Telemetr_app.pkg.log import logger


@dataclass
class Handler:
    logger: logger.Logger
    api: Api
    user_storage: user.Storage
    channel_storage: channel.Storage
    category_storage: category.Storage

    def create_routes(self):
        """Метод инициализации рутов"""
        self.api.add_resource(userapi.UserResource, "/api/v1/user/<int:id>",
                 resource_class_args=(self.logger, self.user_storage, ))

        self.api.add_resource(userapi.UserListResource, "/api/v1/user",
                        resource_class_args=(self.logger, self.user_storage, ))                 

        self.api.add_resource(channelapi.ChannelResource, "/api/v1/channel/<int:id>",
                        resource_class_args=(self.logger, self.channel_storage, ))

        self.api.add_resource(channelapi.ChannelListResource, "/api/v1/channel",
                        resource_class_args=(self.logger, self.channel_storage, ))

        self.api.add_resource(categoryapi.CategoryListResource, "/api/v1/category",
                        resource_class_args=(self.logger, self.category_storage, ))

def new_handler(logger: logger.Logger, api: Api, user_storage: user.Storage,
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
        api=api,
        user_storage=user_storage,
        channel_storage=channel_storage,
        category_storage=category_storage
    )
