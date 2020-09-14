from flask_restful import Resource
from Telemetr_app.internal.postgres import user, channel, category
from Telemetr_app.pkg.log import logger


class UserResource(Resource):
    """Класс-ресурс для Flask-restful"""

    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self, id):
        res = self.user_storage.get_user_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

class UserListResource(Resource):
    """Класс-ресурс для Flask-restful"""

    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self):
        user_res = []
        res = self.user_storage.get_all()
        for item in res:
            user_res.append(item.to_json())
        
        return user_res, 200

class ChannelResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 channel_storage: channel.ChannelStorage):
        self.logger = logger
        self.channel_storage = channel_storage

    def get(self, id):
        res = self.channel_storage.get_channel_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

class ChannelListResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 channel_storage: channel.ChannelStorage):
        self.logger = logger
        self.channel_storage = channel_storage

    def get(self):
        channel_res = []
        res = self.channel_storage.get_all()
        for item in res:
            channel_res.append(item.to_json())

        return channel_res, 200

class CategoryListResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 category_storage: category.CategoryStorage):
        self.logger = logger
        self.category_storage = category_storage

    def get(self):
        category_res = []
        res = self.category_storage.get_all()
        for item in res:
            category_res.append(item.to_json())

        return category_res, 200
