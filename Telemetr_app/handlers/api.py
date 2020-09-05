from flask_restful import Resource

from Telemetr_app.internal.postgres import user
from Telemetr_app.pkg.log import logger


class UserResource(Resource):
    """Класс-ресурс для Flask-restful"""

    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self):
        test = []
        res = self.user_storage.get_all()
        for user_ in res:
            test.append(user_.to_json())
        return test
