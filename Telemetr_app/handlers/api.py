from flask_restful import Resource
from Telemetr_app.internal.postgres import user, channel
from Telemetr_app.pkg.log import logger


class UserResource(Resource):
    """Класс-ресурс для Flask-restful"""

    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self):
        user_res = []
        res = self.user_storage.get_all()
        for user_ in res:
            user_res.append(user_.to_json())
        return user_res


class ChannelResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 channel_storage: channel.ChannelStorage):
        self.logger = logger
        self.channel_storage = channel_storage

    def get(self):
        channel_res = []
        res = self.channel_storage.get_all()
        for item in res:
            channel_res.append(channel.to_json())

        return channel_res
